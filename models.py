import uuid

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Boolean, Integer, String, LargeBinary
from sqlalchemy.orm import backref, relationship


_db = SQLAlchemy()


def get_db(app):
    global _db

    with app.app_context():
        _db.init_app(app)
        _db.create_all()

    return _db


class Document(_db.Model):
    __tablename__ = 'document'

    id = Column(Integer, primary_key=True)
    uuid = Column(String, unique=True, nullable=False)
    ready = Column(Boolean)
    pages = Column(Integer)
    data = Column(LargeBinary, nullable=False)

    def __init__(self, data):
        self.uuid = uuid.uuid4()
        self.data = data


class Image(_db.Model):
    __tablename__ = 'image'

    id = Column(Integer, primary_key=True)
    page = Column(Integer, nullable=False)
    data = Column(LargeBinary, nullable=False)
    document_id = Column(Integer, ForeignKey('document.id'))
    document = relationship('Document', backref=backref('image'))

    def __init__(self, document_id, page, data):
        self.document_id = document_id
        self.page = page
        self.data = data
