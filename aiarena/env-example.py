# MAKE A COPY OF THIS FILE CALLED env.py AND CHANGE ANY ENVIRONMENT SETTINGS AS APPROPRIATE

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^msxz-koic8*608jsn5%$*8v&fri%=%kg4$%6mkk(e2xm4i$us'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1']

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'aiarena',
        'USER': 'aiarena',
        'PASSWORD': 'aiarena',
        'HOST': 'localhost',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    }
}