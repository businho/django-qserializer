from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = 'wewls(#^h)7)(8x6l)8-d@$!hv909h48f3y3z*04_m3_5_*n^$'

DEBUG = True

INSTALLED_APPS = [
    'django_qserializer.tests.testapp',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
