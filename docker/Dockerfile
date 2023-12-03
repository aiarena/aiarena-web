FROM unit:1.31.0-python3.11

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