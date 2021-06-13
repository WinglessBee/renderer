import io
import json

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from flasgger import Swagger
from flask import Flask, Response, request
from flask.logging import create_logger
from pdf2image import convert_from_bytes
from pdf2image.exceptions import PDFPageCountError, PDFSyntaxError

from models import Document, Image, get_db
from settings import Config


api = Flask(__name__)
api.config.from_object(Config)

logger = create_logger(api)

db = get_db(api)

dramatiq.set_broker(RedisBroker(url=api.config.get('REDIS_URL')))

swagger_template = {
    'swagger': '2.0',
    'info': {
        'title': 'Renderer',
        'description': 'Render normalized PNG images from PDF files',
        'version': '0.1.0'
    },
}
swagger_config = {
    'specs': [{'endpoint': '/', 'route': '/swagger.json'}],
    'specs_route': '/'
}
Swagger(api, template=swagger_template, config=swagger_config, merge=True)


@api.route('/documents', methods=['POST'])
def post_document():
    """Add a document
    ---
    tags:
      - Documents
    parameters:
      - name: data
        in: formData
        type: file
        required: true
    consumes:
      - multipart/form-data
    responses:
      201:
        description: Created
        content:
          application/json:
            schema:
              type: object
              properties:
                uuid:
                  type: string
    """
    result = save_document()

    return Response(response=result, status=201, content_type='application/json')


@api.route('/documents/<string:uuid>')
def get_document(uuid):
    """Get document information
    ---
    tags:
      - Documents
    parameters:
      - name: uuid
        in: path
        type: string
        required: true
    responses:
      200:
        description: OK
        content:
          application/json:
            schema:
              type: object
              properties:
                uuid:
                  type: string
                ready:
                  type: boolean
                pages:
                  type: integer
      404:
        description: Not Found
    """
    result = load_document(uuid)
    if not result:
        return Response(status=404)

    return Response(response=result, status=200, content_type='application/json')


@api.route('/documents/<string:uuid>/<int:page>')
def get_image(uuid, page):
    """Get an image
    ---
    tags:
      - Documents
    parameters:
      - name: uuid
        in: path
        type: string
        required: true
      - name: page
        in: path
        type: integer
        required: true
    responses:
      200:
        description: OK
        content:
          image/png:
            schema:
              type: string
              format: binary
      404:
        description: Not Found
    """
    result = load_image(uuid, page)
    if not result:
        return Response(status=404)

    return Response(response=result, status=200, content_type='image/png')


def save_document():
    document = Document(request.files['data'].stream.read())

    db.session.add(document)
    db.session.commit()

    process_document.send(document.id)

    return json.dumps({'uuid': document.uuid})


def load_document(uuid):
    document = Document.query.filter_by(uuid=uuid).first()
    if not document:
        return None

    return json.dumps({'uuid': document.uuid, 'ready': document.ready, 'pages': document.pages})


def load_image(uuid, page):
    document = Document.query.filter_by(uuid=uuid).first()
    if not document or not document.ready:
        return None

    image = Image.query.filter_by(document_id=document.id, page=page).first()
    if not image:
        return None

    return image.data


@dramatiq.actor
def process_document(document_id):
    with api.app_context():
        document = Document.query.get(document_id)

        try:
            pages = convert_from_bytes(document.data)

        except (PDFPageCountError, PDFSyntaxError, ValueError) as e:
            document.ready = False
            db.session.commit()
            logger.exception(e)
            return

        for number, page in enumerate(pages, 1):
            page = normalize(page)
            buffer = io.BytesIO()

            page.save(buffer, format='png')
            image = Image(document_id, number, buffer.getvalue())

            db.session.add(image)

        document.ready = True
        document.pages = len(pages)
        db.session.commit()


def normalize(image, max_width=1200, max_height=1600):
    width, height = image.size
    ratio = width / height

    if ratio > (max_width / max_height):
        image = image.resize((max_width, int(max_width / ratio)))

    else:
        image = image.resize((int(max_height * ratio), max_height))

    return image


if __name__ == '__main__':
    api.run(debug=True)
