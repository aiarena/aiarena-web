FROM python:3.7

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update \
    && apt-get install -y gcc

COPY . workspace

WORKDIR /workspace/pip
RUN pip install --upgrade pip
RUN python pip-install.py
RUN pip install -r requirements.txt
RUN pip install -r requirements.DEVELOPMENT.txt