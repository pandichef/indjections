settings = """
INSTALLED_APPS += ['rest_framework']
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [  # Ref: https://www.django-rest-framework.org/api-guide/authentication/
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}
"""

urls = """
from django.urls import include
urlpatterns += [path('api-auth/', include('rest_framework.urls'))]
"""
