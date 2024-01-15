FROM unit:1.31.0-python3.11 as base

RUN apt-get update && \
    apt-get install -y \
        build-essential \
        lsb-release \
        make \
        gcc \
        wget \
        curl \
        gnupg2

RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN apt -y update
RUN apt-get install postgresql-client-15 -y

ADD ./pip/requirements.txt /srv/requirements.txt
RUN pip install -r /srv/requirements.txt

COPY . /app
WORKDIR /app

RUN python django-discord-bind/setup.py install --force

ENV PYTHONDONTWRITEBYTECODE 1

EXPOSE 8411

FROM base as cloud

ENV DJANGO_ENVIRONMENT PRODUCTION
ARG SECRET_KEY

ADD ./aiarena/unit-config.json /docker-entrypoint.d/
RUN chown -R unit:unit /app/

ADD ./pip/requirements.PRODUCTION.txt /srv/requirements.PRODUCTION.txt
RUN pip install -r /srv/requirements.PRODUCTION.txt

RUN python /app/manage.py collectstatic --noinput --clear

FROM base as dev

ENV DJANGO_ENVIRONMENT DEVELOPMENT

ADD ./pip/requirements.DEVELOPMENT.txt /srv/requirements.DEVELOPMENT.txt
RUN pip install -r /srv/requirements.DEVELOPMENT.txt
