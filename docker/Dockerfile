FROM python:3.10-slim
ARG ENVIRONMENT_TYPE="DEVELOPMENT"

RUN apt-get update \
    && apt-get install -y gcc

RUN pip install --upgrade pip gunicorn

ADD ./pip/requirements.txt /srv/requirements.txt

RUN pip install -r /srv/requirements.txt

COPY . /app

WORKDIR /app/pip

RUN python pip-install.py

WORKDIR /app