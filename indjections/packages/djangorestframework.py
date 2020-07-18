settings = """
INSTALLED_APPS += ['rest_framework']
"""

urls = """
from django.urls import include
urlpatterns += [path('api-auth/', include('rest_framework.urls'))]
"""
