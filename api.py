import io
import uuid

import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
from pdf2image import convert_from_bytes

from settings import Config

api = Flask(__name__)
api.config.from_object(Config)

db = SQLAlchemy(api)
db.create_all()

broker = RabbitmqBroker(host=api.config.get('BROKER'))
dramatiq.set_broker(broker)


@api.route('/documents', methods=['POST'])
def post():
    result = post_document()

    return Response(response=result, status=201, content_type='application/json')


@api.route('/documents/<string:uuid>', defaults={'page': None})
@api.route('/documents/<string:uuid>/<int:page>')
def get(unique_id, page):
    result = get_image(unique_id, page) if page else get_document(unique_id)
    if not result:
        return Response(status=404)

    content_type = 'image/png' if page else 'application/json'

    return Response(response=result, status=200, content_type=content_type)


def post_document():
    document = Documents(request.data)

    db.session.add(document)
    db.session.commit()

    process_document.send(document.id)

    return {'uuid': document.uuid}


def get_document(unique_id):
    document = Documents.query.filter_by(uuid=unique_id).first()
    if not document:
        return None

    return {'uuid': document.uuid, 'ready': document.ready, 'pages': document.pages}


def get_image(unique_id, page):
    document = Documents.query.filter_by(uuid=unique_id).first()
    if not document or not document.ready:
        return None

    image = Images.query.filter_by(document_id=document.id, page=page).first()
    if not image:
        return None

    return image.data


@dramatiq.actor
def process_document(document_id):
    document = Documents.query.get(document_id)
    pages = convert_from_bytes(document.data)

    for number, page in enumerate(pages, 1):
        page = normalize(page)
        buffer = io.BytesIO()

        page.save(buffer, format='png')
        image = Images(document_id, number, buffer.getvalue())

        db.session.add(image)

    document.update(ready=True, pages=len(pages))
    db.session.commit()


def normalize(image, max_width=1200, max_height=1600):
    width, height = image.size

    if width > max_width or height > max_height:
        if width / max_width > height / max_height:
            image = image.resize((max_width, None))

        else:
            image = image.resize((None, max_height))

    return image


class Documents(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(32), unique=True, nullable=False)
    ready = db.Column(db.Boolean)
    pages = db.Column(db.Integer)
    data = db.Column(db.LargeBinary, nullable=False)
    images = db.relationship('Images', backref='document', lazy=True)

    def __init__(self, data):
        self.uuid = uuid.uuid4()
        self.data = data


class Images(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.Integer, nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)

    def __init__(self, document_id, page, data):
        self.document_id = document_id
        self.page = page
        self.data = data


if __name__ == '__main__':
    api.run(debug=True)

