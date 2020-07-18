import re
import os
from importlib import import_module
import sys
from django.core.management.base import BaseCommand
from indjections.core import indject_string, parse_toml


class Command(BaseCommand):
    help = 'Modifies settings.py and urls.py with boilerplate'

    def handle(self, *args, **kwargs):
        settings = sys.modules[os.environ['DJANGO_SETTINGS_MODULE']]
        # import_module(settings.ROOT_URLCONF)
        urls = sys.modules[settings.ROOT_URLCONF]

        with open(settings.INDJECTIONS_SETTINGS['TOML_FILE'], 'r') as f:
            install_requires, extras_require = parse_toml(
                f.read(), settings.INDJECTIONS_SETTINGS['PACKAGES_KEY'],
                settings.INDJECTIONS_SETTINGS['DEV_PACKAGES_KEY'])

        installed_packages = extras_require + install_requires

        for package in installed_packages:
            try:
                # settings
                indjections = import_module(f'indjections.packages.{package}')
                try:
                    indject_string(settings.__file__, package, indjections.settings)
                except AttributeError:
                    print(f"{package} has no settings indjection.")

                # urls
                try:
                    indject_string(urls.__file__, package, indjections.urls)
                except AttributeError:
                    print(f"{package} has no urls indjection.")

                # hooks
                try:
                    for hook in indjections.hooks:
                        hook()
                except AttributeError:
                    print(f"{package} has no hooks.")

                # base_top
                try:
                    indject_string(settings.INDJECTIONS_SETTINGS['BASE_HTML'],
                                   package + '__base_top', indjections.base_top, after=False,
                                   is_template=True)
                except AttributeError:
                    print(f"{package} has no base_top.")

                # base_head
                try:
                    indject_string(settings.INDJECTIONS_SETTINGS['BASE_HTML'],
                                   package + '__base_head', indjections.base_head, after=False,
                                   reference_regex="</head>", is_template=True)
                except AttributeError:
                    print(f"{package} has no base_head.")

                # base_body
                try:
                    indject_string(settings.INDJECTIONS_SETTINGS['BASE_HTML'],
                                   package + '__base_body', indjections.base_body, after=True,
                                   reference_regex="<body[\s\S]*?>", is_template=True)  # https://stackoverflow.com/questions/6441015/symbol-for-any-number-of-any-characters-in-regex
                except AttributeError:
                    print(f"{package} has no base_body.")
            except ModuleNotFoundError:
                print(f"{package} has no defined indjections.")
            print('################################################################################')
