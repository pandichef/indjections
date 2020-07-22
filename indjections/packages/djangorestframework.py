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
""", """
from .models import {object_name}

class {object_name}Serializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = {object_name}
        fields = {field_names}
""")
