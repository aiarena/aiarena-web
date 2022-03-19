import os
# THIS FILE IS IGNORED, CHANGES DONE TO IT ARE NOT COMMITED

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('MYSQL_DATABASE', 'aiarena'),
        'USER': os.getenv('MYSQL_USER', 'aiarena'),
        'PASSWORD': os.getenv('MYSQL_PASSWORD', 'aiarena'),
        'HOST': os.getenv('MYSQL_HOST', 'localhost'),  # Or an IP Address that your DB is hosted on
        'PORT': os.getenv('MYSQL_PORT', '32768'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        # todo: having this enabled will open a transaction for every request and therefore slow down the site
        # todo: ideally we will eventually remove this and specify each individual view that needs its own transaction.
        'ATOMIC_REQUESTS': True,
    }
}
