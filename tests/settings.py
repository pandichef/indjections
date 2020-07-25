import os
BASE_DIR = os.path.dirname(__file__)
DEBUG = True
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',  # grappelli wants this to be above
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'indjections',
    # 'main',
    'tests.main',
]
SECRET_KEY = 'not very secret in tests'
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'tests.urls'
# ROOT_URLCONF = 'config.urls'
USE_TZ = True
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': True,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        # 'TEST': {"NAME": ':memory:'},
    }
}
STATIC_URL = '/static/'

INDJECTIONS_SETTINGS = {
    # 'TOML_FILE': './tests/project/packages.toml',
    'TOML_FILE': os.path.join(BASE_DIR, 'packages.toml'),
    'TOML_KEYS': [
        "install_requires",
        "extras_require.dev",
        "indjections.extras",
    ],
    # 'DEV_PACKAGES_KEY': "extras_require.dev",
    # 'BASE_HTML': './tests/project/templates/base.html',  # tmp
    'BASE_HTML': os.path.join(BASE_DIR, 'base.html'),
}
