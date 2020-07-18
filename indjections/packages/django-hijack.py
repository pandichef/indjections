settings = """
INSTALLED_APPS += ['hijack', 'compat']
"""

urls = """
from django.urls import include
urlpatterns += [path('hijack/', include('hijack.urls', namespace='hijack'))]
"""

base_top = """
{% load staticfiles %}
{% load hijack_tags %}
"""

base_head = """
<link rel="stylesheet" type="text/css" href="{% static 'hijack/hijack-styles.css' %}" />
"""

base_body = """
{% hijack_notification %}
"""
