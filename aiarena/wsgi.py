"""
WSGI config for aiarena project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os
import site
from django.core.wsgi import get_wsgi_application

import sys
sys.path.append('/home/aiarena/ai-arena/aiarena')
site.addsitedir('/home/aiarena/ai-arena/python_env/lib/python3.5/site-packages')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aiarena.settings')

application = get_wsgi_application()
