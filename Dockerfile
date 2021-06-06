FROM python:3.9.5-slim-buster

RUN pip install pipenv

ADD . /code
WORKDIR /code

ENV FLASK_APP=api.py

RUN pipenv install --system --skip-lock

EXPOSE 5000

CMD python ${FLASK_APP}
