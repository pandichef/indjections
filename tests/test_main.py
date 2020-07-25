# import pytest
import os
from os.path import dirname, join
import sys
import importlib
# from unittest import mock

settings = sys.modules[os.environ['DJANGO_SETTINGS_MODULE']]
importlib.import_module(settings.ROOT_URLCONF)
urls = sys.modules[settings.ROOT_URLCONF]

test_app_dir = join(dirname(dirname(settings.__file__)), 'main')

# assert False, test_app_dir

# from django.contrib.auth import get_user_model
# User = get_user_model()
from indjections.management.commands.indject import Command

import pytest

@pytest.fixture
def setup_and_cleanup(request):
    with open(settings.__file__, 'r') as fn:
        original_settings_string = fn.read()
    with open(urls.__file__, 'r') as fn:
        original_urls_string = fn.read()
    with open(join(test_app_dir, 'serializers.py'), 'r') as fn:
        original_serializers_string = fn.read()
    with open(join(test_app_dir, 'views.py'), 'r') as fn:
        original_views_string = fn.read()
    def restore_files():
        with open(settings.__file__, 'w') as ifn:
            ifn.write(original_settings_string)
        with open(urls.__file__, 'w') as ifn:
            ifn.write(original_urls_string)
        with open(join(test_app_dir, 'serializers.py'), 'w') as ifn:
            ifn.write(original_serializers_string)
        with open(join(test_app_dir, 'views.py'), 'w') as ifn:
            ifn.write(original_views_string)
    request.addfinalizer(restore_files)
    return original_settings_string, original_urls_string


def test_unlocked(setup_and_cleanup):
    original_settings_string, original_urls_string = setup_and_cleanup
    # with mock.patch('builtins.open',
    #                 mock.mock_open(read_data=read_tests_pyproject()),
    #                 create=True) as m:
    commandobj = Command()
    # os.environ['PYPROJECT_PATH'] = './tests/pyproject.toml'
    # os.environ['PYPROJECT_PATH'] = './tests/pyproject.toml'
    commandobj.handle()  # execute management command
    with open(settings.__file__, 'r') as fn:
        final_settings_string = fn.read()
    with open(urls.__file__, 'r') as fn:
        final_urls_string = fn.read()
    settings_insertstring = """### block: django-debug-toolbar ###
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
    try:
        INTERNAL_IPS += ['127.0.0.1']
    except NameError:
        INTERNAL_IPS = ['127.0.0.1']
### endblock: django-debug-toolbar ###
"""
    urls_insertstring = """### block: django-debug-toolbar ###
from django.conf import settings
from django.urls import include, path

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
### endblock: django-debug-toolbar ###
"""
    assert final_settings_string[-len(settings_insertstring):] == settings_insertstring
    assert final_urls_string[-len(urls_insertstring):] == urls_insertstring


def test_locked(setup_and_cleanup):
    original_settings_string, original_urls_string = setup_and_cleanup
    locked_text = """### block: django-debug-toolbar/lock ###
print('This is locked.)
### endblock: django-debug-toolbar ###
### block: djangorestframework/lock ###
print('This is locked.)
### endblock: djangorestframework ###
"""
    with open(settings.__file__, 'w') as fn:
        fn.write(original_settings_string + locked_text)
    with open(urls.__file__, 'w') as fn:
        fn.write(original_urls_string + locked_text)
    commandobj = Command()
    # os.environ['PYPROJECT_PATH'] = './tests/pyproject.toml'
    commandobj.handle()  # execute management command
    with open(settings.__file__, 'r') as fn:
        final_settings_string = fn.read()
    with open(urls.__file__, 'r') as fn:
        final_urls_string = fn.read()
    assert final_settings_string[-len(locked_text):] == locked_text
    assert final_urls_string[-len(locked_text):] == locked_text
