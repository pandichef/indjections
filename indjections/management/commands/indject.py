import re
import os
import importlib
import sys
from django.core.management.base import BaseCommand
from indjections.core import indject_string, parse_toml

from os.path import abspath, dirname


class Command(BaseCommand):
    help = 'Modifies settings.py and urls.py with boilerplate'

    def handle(self, *args, **kwargs):
        # time = timezone.now().strftime('%X')
        # self.stdout.write("It's now %s" % time)
        settings = sys.modules[os.environ['DJANGO_SETTINGS_MODULE']]
        importlib.import_module(settings.ROOT_URLCONF)
        urls = sys.modules[settings.ROOT_URLCONF]

        # pyroject_path = os.environ.get(
        #     'PYPROJECT_PATH',
        #     dirname(dirname(dirname(dirname(abspath(__file__)))))
        # )

        # sys.path.insert(0, pyroject_path)
        # from pyproject import dependencies

        # def dct2lst(dct):
        #     return [x + dct[x] if dct[x] != "*" else x for x in dct]

        # install_requires = dct2lst(dependencies['install_requires'])
        # extras_require = {'dev': dct2lst(dependencies['extras_require']['dev'])}

        # with open(os.environ.get('PYPROJECT_PATH', 'pyproject.toml'), 'r') as f:
        with open(settings.INDJECTIONS_SETTINGS['TOML_FILE'], 'r') as f:
            import toml
            # install_requires, extras_require = dependencies
            # assert False, f.read()
            # install_requires, extras_require = parse_toml(f.read(), 'install_requires', 'requires_extra.dev')
            # install_requires, extras_require = parse_toml(f.read(), 'install_requires', 'extras_require.dev')
            install_requires, extras_require = parse_toml(
                f.read(), settings.INDJECTIONS_SETTINGS['PACKAGES_KEY'],
                settings.INDJECTIONS_SETTINGS['DEV_PACKAGES_KEY'])

        # assert False, tobeinstalled

        # dct = tobeinstalled['install_requires']
        # install_requires = [x + dct[x] if dct[x] != "*" else x for x in dct]
        # dct = tobeinstalled['extras_require']['dev']
        # extras_require = [x + dct[x] if dct[x] != "*" else x for x in dct]
        # assert False, install_requires

        installed_packages = install_requires + extras_require

        for package in installed_packages:
            from importlib import import_module
            try:
                indjections = import_module(f'indjections.packages.{package}')
                try:
                    indject_string(settings.__file__, package, indjections.settings)
                except AttributeError:
                    print(f"{package} has no settings indjection.")
                try:
                    indject_string(urls.__file__, package, indjections.urls)
                except AttributeError:
                    print(f"{package} has no urls indjection.")
            except ModuleNotFoundError:
                print(f"{package} has no defined indjections.")

'''
            if package == 'django-debug-toolbar':
                indject_string(settings.__file__, package, """
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
    try:
        INTERNAL_IPS += ['127.0.0.1']
    except NameError:
        INTERNAL_IPS = ['127.0.0.1']
""")

                indject_string(urls.__file__, package, """
from django.conf import settings
from django.urls import include, path

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
""")

            elif package == 'djangorestframework':
                indject_string(settings.__file__, package, """
INSTALLED_APPS += ['rest_framework']
""")

                indject_string(urls.__file__, package, """
from django.urls import include
urlpatterns += [path('api-auth/', include('rest_framework.urls'))]
""")

            else:
                print(f"{package} has no defined indjections.")
'''
