from string import Template

TYPE_OF_SERIALIZER = "HyperlinkedModelSerializer"

settings = ("""
INSTALLED_APPS += ['rest_framework']
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [  # Ref: https://www.django-rest-framework.org/api-guide/authentication/
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}
""", """
# App: {label}
""", """
# Model: {object_name}
""")

urls = """
from django.urls import include
urlpatterns += [path('api-auth/', include('rest_framework.urls'))]
"""

app_serializers = ("""
from rest_framework import serializers
""", Template("""
from .models import {object_name}

class {object_name}Serializer(serializers.${serializer_class}):
    class Meta:
        model = {object_name}
        fields = {field_names}
""").substitute(serializer_class=TYPE_OF_SERIALIZER))
