#!/usr/bin/env bash

nextjs_server=/app/frontend/.next/standalone/server.js
HOSTNAME=0.0.0.0
PORT=8312

node ${nextjs_server}
