import re
import os
from os import listdir
from os.path import dirname, isfile, join
from importlib import import_module
import sys
from django.core.management.base import BaseCommand
from indjections.core import indject_string, parse_toml


def execute_installation_file(package, settings, urls, package_path="indjections.packages",
                              delete_only=False):
    try:
        # settings
        indjections = import_module(f'{package_path}.{package}')
        try:
            indject_string(settings.__file__, package, indjections.settings, delete_only=delete_only)
        except AttributeError:
            print(f"{package} has no settings indjection.")

        # urls
        try:
            indject_string(urls.__file__, package, indjections.urls, delete_only=delete_only)
        except AttributeError:
            print(f"{package} has no urls indjection.")

        # base_top
        try:
            indject_string(settings.INDJECTIONS_SETTINGS['BASE_HTML'],
                           package + '__base_top', indjections.base_top, after=False,
                           is_template=True, delete_only=delete_only)
        except AttributeError:
            print(f"{package} has no base_top.")

        # base_head
        try:
            indject_string(settings.INDJECTIONS_SETTINGS['BASE_HTML'],
                           package + '__base_head', indjections.base_head, after=False,
                           reference_regex="</head>", is_template=True,
                           delete_only=delete_only)
        except AttributeError:
            print(f"{package} has no base_head.")

        # base_body
        try:
            indject_string(settings.INDJECTIONS_SETTINGS['BASE_HTML'],
                           package + '__base_body', indjections.base_body, after=True,
                           reference_regex="<body[\s\S]*?>", is_template=True,
                           delete_only=delete_only)
            # regex: https://stackoverflow.com/questions/6441015/symbol-for-any-number-of-any-characters-in-regex
        except AttributeError:
            print(f"{package} has no base_body.")

        # hooks
        if not delete_only:
            try:
                for hook in indjections.hooks:
                    hook()
            except AttributeError:
                print(f"{package} has no hooks.")
    except ModuleNotFoundError:
        print(f"{package} has no defined indjections.")
    print('################################################################################')



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
            execute_installation_file(package, settings, urls)

        print('=====================================')
        print('====> Cleaning up removed packages...')
        print('=====================================')
        import indjections.packages
        indjections_packages_dir = dirname(vars(indjections.packages)['__file__'])
        indjections_packages_list = listdir(indjections_packages_dir)
        indjections_packages_list = [f for f in indjections_packages_list if
                                     isfile(join(indjections_packages_dir, f))]
        indjections_packages_list.remove('__init__.py')
        indjections_packages_list = list(map(lambda e: e.split('.')[0],
                                        indjections_packages_list))

        packages_to_delete = list(filter(lambda e: e not in installed_packages,
                                         indjections_packages_list))

        for package in packages_to_delete:
            execute_installation_file(package, settings, urls, delete_only=True)
