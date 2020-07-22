from pprint import pformat
from pathlib import Path
import re
import os
from os import listdir
from os.path import dirname, isfile, join
from importlib import import_module
import sys
from django.core.management.base import BaseCommand
from indjections.core import indject_string, parse_toml
from indjections import package_path
from indjections.core import get_app_and_model_data

project_app_list = get_app_and_model_data()


def make_insertion_string(tuples_to_insert, app, app_level=True):
    """app_level=True when working on app_* variables
    >>> make_insertion_string(('{label}:', '{object_name}:'),
    ...    {'label': 'main', 'models': [
    ...        {'object_name': "Model1"}, {'object_name': "Model2"}
    ...    ]})
    'main:Model1:Model2:'
    >>> make_insertion_string((':', '{label}:', '{object_name}:'),
    ...    {'label': 'main', 'models': [
    ...        {'object_name': "Model1"}, {'object_name': "Model2"}
    ...    ]}, app_level=False)
    ':main:Model1:Model2:'
    >>> make_insertion_string(('{label}:',),
    ...    {'label': 'main', 'models': [
    ...        {'object_name': "Model1"}, {'object_name': "Model2"}
    ...    ]})
    'main:'
    """
    if type(tuples_to_insert) == str:
        tuples_to_insert = (tuples_to_insert,)
    if app_level:
        tuples_to_insert = ('',) + tuples_to_insert
    models = app['models']
    # if app_level:
    insertion_string = tuples_to_insert[0]
    try:
        insertion_string += tuples_to_insert[1].format(**app)
    except IndexError:
        pass
    # else:
    #     insertion_string = tuples_to_insert[0].format(**app)

    model_string = ""
    for model in models:
        # if app_level:
        try:
            model_string += tuples_to_insert[2].format(**model)
        except IndexError:
            pass
        # else:
        #     model_string += tuples_to_insert[1].format(**model)
    insertion_string += model_string
    return insertion_string

def make_insertion_string_multi_app(tuples_to_insert, apps=project_app_list):
    if type(tuples_to_insert) == str:
        tuples_to_insert = (tuples_to_insert,)
    insertion_string = tuples_to_insert[0]
    for app in apps:
        insertion_string += make_insertion_string(tuples_to_insert[1:], app)
    return insertion_string


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
            insertion_string = make_insertion_string_multi_app(tuples_to_insert=indjections.settings)
            indject_string(settings.__file__, package, insertion_string, delete_only=delete_only)
        except AttributeError:
            print(f"{package} has no settings indjection.")

        # urls
        try:
            insertion_string = make_insertion_string_multi_app(tuples_to_insert=indjections.urls)
            indject_string(urls.__file__, package, insertion_string, delete_only=delete_only)
        except AttributeError:
            print(f"{package} has no urls indjection.")

        # base_top
        try:
            insertion_string = make_insertion_string_multi_app(tuples_to_insert=indjections.base_top)
            indject_string(base_html,
                           package + '__base_top', insertion_string, after=False,
                           is_template=True, delete_only=delete_only)
        except AttributeError:
            print(f"{package} has no base_top.")

        # base_head
        try:
            insertion_string = make_insertion_string_multi_app(tuples_to_insert=indjections.base_head)
            indject_string(base_html,
                           package + '__base_head', insertion_string, after=False,
                           reference_regex="</head>", is_template=True,
                           delete_only=delete_only)
        except AttributeError:
            print(f"{package} has no base_head.")

        # base_body
        try:
            insertion_string = make_insertion_string_multi_app(tuples_to_insert=indjections.base_body)
            indject_string(base_html,
                           package + '__base_body', insertion_string, after=True,
                           reference_regex="<body[\s\S]*?>", is_template=True,
                           delete_only=delete_only)
            # regex: https://stackoverflow.com/questions/6441015/symbol-for-any-number-of-any-characters-in-regex
        except AttributeError:
            print(f"{package} has no base_body.")

        # base_finally i.e., the area just before the </body> tag
        try:
            insertion_string = make_insertion_string_multi_app(tuples_to_insert=indjections.base_finally)
            indject_string(base_html,
                           package + '__base_finally', insertion_string, after=False,
                           reference_regex="</body>", is_template=True,
                           delete_only=delete_only)
        except AttributeError:
            print(f"{package} has no base_finally.")

        # app_*
        # Note: filter is implicitly similar to try/except block elsewhere
        app_level_files = list(filter(lambda x: x.startswith('app_'),
                                      dir(indjections)))  # list of strings
        for file_name in app_level_files:
            for app in project_app_list:
                tuples_to_insert = getattr(indjections, file_name)
                include = indjections_settings.get('INCLUDE_APPS', None)
                exclude = indjections_settings.get('EXCLUDE_APPS', None)
                if include and exclude:
                    raise Exception(f'In INDJECTIONS_SETTINGS, specify only "EXCLUDE_APPS" or "INCLUDE_APPS", but not both.')
                if include or include == {}:
                    include_this_app = app['label'] in include and package in include[app['label']]
                elif exclude or exclude == {}:
                    include_this_app = app['label'] not in exclude and package not in exclude[app['label']]
                else:  # default: include all apps
                    include_this_app = True
                insertion_string = make_insertion_string(tuples_to_insert, app)
                file_path = join(app['path'], f'{file_name.replace("app_", "")}.py')
                Path(file_path).touch()  # make sure file exists
                indject_string(file_path, package, insertion_string,
                               delete_only=not include_this_app)  # delete if excluded!

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


def use_custom_installers(directory_name='custom_installers'):
    from indjections import package_path
    try:
        files = os.listdir(directory_name)
        files.remove('__init__.py')
        for file in files:
            module_name = os.path.splitext(file)[0]
            exec(f'from {directory_name} import {module_name}')  # local version
            try:
                exec(f'import {package_path}.{module_name}')  # global version
            except ModuleNotFoundError:
                pass
            exec(f"""sys.modules[f'{package_path}.{module_name}'] = {module_name}""")
    except FileNotFoundError:
        pass  # no custom installers found


class Command(BaseCommand):
    help = 'Modifies settings.py and urls.py with boilerplate'

    def handle(self, *args, **kwargs):
        use_custom_installers()

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
