settings = """
try:
    AUTHENTICATION_BACKENDS += ['django.contrib.auth.backends.ModelBackend',
                                'allauth.account.auth_backends.AuthenticationBackend']
except NameError:
    AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend',
                               'allauth.account.auth_backends.AuthenticationBackend']
INSTALLED_APPS += [
    'django.contrib.sites',  # not installed by default
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]
"""

urls = """
from django.urls import include
urlpatterns += [path('accounts/', include('allauth.urls'))]
"""
