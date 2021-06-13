FROM python:3.9.5-slim-buster

RUN apt-get update
RUN apt-get install poppler-utils -y

RUN pip install pipenv

COPY . /code
WORKDIR /code

ENV FLASK_APP /code/api.py

RUN pipenv install --system --skip-lock

CMD flask run --host=0.0.0.0 --port=5000
