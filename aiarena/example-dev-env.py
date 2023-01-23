# MAKE A COPY OF THIS FILE CALLED env.py AND CHANGE ANY ENVIRONMENT SETTINGS AS APPROPRIATE

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgres',
        'NAME': 'aiarena',
        'USER': 'aiarena',
        'PASSWORD': 'aiarena',
        'HOST': 'localhost',  # Or an IP Address that your DB is hosted on
        'PORT': '32768',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        # todo: having this enabled will open a transaction for every request and therefore slow down the site
        # todo: ideally we will eventually remove this and specify each individual view that needs its own transaction.
        'ATOMIC_REQUESTS': True,
    }
}
