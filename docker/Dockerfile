FROM unit:1.31.0-python3.11

RUN apt-get update && \
    apt-get install -y \
        build-essential \
        make \
        gcc

ADD ./pip/requirements.txt /srv/requirements.txt
RUN pip install -r /srv/requirements.txt

COPY . /app
WORKDIR /app

RUN python django-discord-bind/setup.py install --force

ENV PYTHONDONTWRITEBYTECODE 1

EXPOSE 8411