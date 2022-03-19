FROM python:3.7-slim

RUN apt-get update \
    && apt-get install -y gcc libmariadb-dev

COPY . /app

WORKDIR /app/pip
RUN pip install --upgrade pip
RUN python pip-install.py
RUN pip install -r requirements.txt
RUN pip install -r requirements.DEVELOPMENT.txt

WORKDIR /app