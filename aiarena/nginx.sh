#!/usr/bin/env sh

# Helper to run nginx
cp -r /app/nginx/* /etc/nginx/ && exec nginx -g "daemon off;"
