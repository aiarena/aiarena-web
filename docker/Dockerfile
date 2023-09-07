FROM python:3.10-slim-bullseye

RUN apt-get update && \
    apt-get install -y \
        build-essential \
        make \
        gcc

ADD ./pip/requirements.txt /srv/requirements.txt
RUN pip install -r /srv/requirements.txt

COPY . /app
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1

EXPOSE 8411