DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

SITE_ID = 1
DEBUG = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'sequere',
    'sequere.tests',
]

SECRET_KEY = 'blabla'

ROOT_URLCONF = 'sequere.tests.urls'

TEST_RUNNER = 'sequere.tests.runner.DjangoTestSuiteRunner'
