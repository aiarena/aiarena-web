#!/usr/bin/env bash

# Helper to run celery using /app as a current working directory
(cd /app && /usr/local/bin/celery $*)
