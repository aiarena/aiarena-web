#!/usr/bin/env bash

uwsgi=/usr/local/bin/uwsgi
uwsgi_args=${*:-"--ini /app/aiarena/uwsgi.ini"}

${uwsgi} ${uwsgi_args}
