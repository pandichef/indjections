import re
import os
from os import listdir
from os.path import dirname, isfile, join
from importlib import import_module
import sys
from django.core.management.base import BaseCommand
from indjections.core import indject_string, parse_toml
from indjections import package_path


def execute_installation_file(package, settings, urls, package_path=package_path,
                              delete_only=False):
    indjections_settings = getattr(settings, 'INDJECTIONS_SETTINGS', {})

    base_html = indjections_settings.get(
        'BASE_HTML', join(settings.BASE_DIR, 'templates', 'admin', 'base.html'))

    try:
        indjections = import_module(f'{package_path}.{package}')  # this fails on python 3.5

        # pre (un)install hooks
        if not delete_only:
            try:
                for hook in indjections.pre_hooks:
                    hook()
            except AttributeError:
                print(f"{package} has no pre_hooks.")
        else:
            try:
                for hook in indjections.pre_hooks_delete:
                    hook()
            except AttributeError:
                pass  # print(f"{package} has no pre_hooks_delete.")

        # settings
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
            indject_string(base_html,
                           package + '__base_top', indjections.base_top, after=False,
                           is_template=True, delete_only=delete_only)
        except AttributeError:
            print(f"{package} has no base_top.")

        # base_head
        try:
            indject_string(base_html,
                           package + '__base_head', indjections.base_head, after=False,
                           reference_regex="</head>", is_template=True,
                           delete_only=delete_only)
        except AttributeError:
            print(f"{package} has no base_head.")

        # base_body
        try:
            indject_string(base_html,
                           package + '__base_body', indjections.base_body, after=True,
                           reference_regex="<body[\s\S]*?>", is_template=True,
                           delete_only=delete_only)
            # regex: https://stackoverflow.com/questions/6441015/symbol-for-any-number-of-any-characters-in-regex
        except AttributeError:
            print(f"{package} has no base_body.")

        # base_finally i.e., the area just before the </body> tag
        try:
            indject_string(base_html,
                           package + '__base_finally', indjections.base_finally, after=False,
                           reference_regex="</body>", is_template=True,
                           delete_only=delete_only)
        except AttributeError:
            print(f"{package} has no base_finally.")

        # post (un)install hooks
        if not delete_only:
            try:
                for hook in indjections.post_hooks:
                    hook()
            except AttributeError:
                print(f"{package} has no post_hooks.")
        else:
            try:
                for hook in indjections.post_hooks_delete:
                    hook()
            except AttributeError:
                pass  # print(f"{package} has no post_hooks_delete.")
    except ModuleNotFoundError:
        print(f"{package} has no defined indjections.")
    print('################################################################################')



class Command(BaseCommand):
    help = 'Modifies settings.py and urls.py with boilerplate'

    def handle(self, *args, **kwargs):
        # not "from django.conf import settings" to prevent tests from loading Django
        settings = sys.modules[os.environ['DJANGO_SETTINGS_MODULE']]
        indjections_settings = getattr(settings, 'INDJECTIONS_SETTINGS', {})

        # import_module(settings.ROOT_URLCONF)
        urls = sys.modules[settings.ROOT_URLCONF]
        # assert False, settings.INDJECTIONS_SETTINGS

        toml_file = indjections_settings.get(
            'TOML_FILE', os.path.join(settings.BASE_DIR, 'Pipfile'))
        toml_keys = indjections_settings.get('TOML_KEYS', (
                "packages",
                "dev-packages",
                "indjections.extras",
            ))

        with open(toml_file, 'r') as f:
            installed_packages = parse_toml(
                f.read(), toml_keys)

        # installed_packages = extras_require + install_requires

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
