import os
import shutil
from inspect import getfile
import django
from pprint import pformat
from pathlib import Path
import re
import os
from os import listdir
from os.path import dirname, isfile, join
from importlib import import_module
import sys
from colorama import Fore, Back, Style, Cursor, init

# from termcolor
from django.core.management.base import BaseCommand, CommandError
from indjections.core import indject_string, parse_toml
from indjections import package_path
from indjections.core import get_app_and_model_data


init()  # enable text coloring on Windows
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
        tuples_to_insert = ("",) + tuples_to_insert
    models = app["models"]
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


def copy_django_admin_base():
    """If defaults are used, just copy over all the Django admin templates
    """
    django_root = os.path.dirname(getfile(django))
    project_root = os.getcwd()
    django_admin_base = os.path.join(
        django_root, "contrib", "admin", "templates", "admin", "base.html"
    )
    project_admin_base = os.path.join(project_root, "templates", "admin", "base.html")
    if not os.path.exists(project_admin_base):  # do not overwrite
        # https://stackoverflow.com/questions/2793789/create-destination-path-for-shutil-copy-files
        os.makedirs(os.path.dirname(project_admin_base), exist_ok=True)
        shutil.copyfile(django_admin_base, project_admin_base)


def execute_installation_file(
    package,
    settings,
    urls,
    package_path=package_path,
    delete_only=False,
    verbosity=1,
    interactive=True,
):
    # print(f"{package}:{delete_only}")

    indjections_settings = getattr(settings, "INDJECTIONS_SETTINGS", {})

    base_html = indjections_settings.get(
        "BASE_HTML", join(settings.BASE_DIR, "templates", "admin", "base.html")
    )
    if base_html == join(settings.BASE_DIR, "templates", "admin", "base.html"):
        copy_django_admin_base()

    try:
        indjections = import_module(
            f"{package_path}.{package}"
        )  # this fails on python 3.5

        # pre (un)install hooks
        if not delete_only:
            try:
                for hook in indjections.pre_hooks:
                    hook()
                if verbosity >= 2:
                    print(f"    {len(indjections.pre_hooks)} pre_hooks executed")
            except AttributeError:
                if verbosity >= 3:
                    # print(f"    {package} has no pre_hooks")
                    print(f"    No pre_hooks found")
        else:
            try:
                for hook in indjections.pre_hooks_delete:
                    hook()
                if verbosity >= 3:
                    print(
                        f"    {len(indjections.pre_hooks_delete)} pre_hooks_delete executed"
                    )
            except AttributeError:
                if verbosity >= 3:
                    # print(f"    {package} has no pre_hooks_delete")
                    print(f"    No pre_hooks_delete found")

        # settings
        try:
            insertion_string = make_insertion_string_multi_app(
                tuples_to_insert=indjections.settings
            )
            indject_string(
                settings.__file__,
                package,
                insertion_string,
                delete_only=delete_only,
                verbosity=verbosity,
                interactive=interactive,
            )
            # if verbosity >= 2 and not delete_only:
            #     print(f"    Block in settings.py injected")
            # if verbosity >= 3 and delete_only:
            #     print(f"    Block in settings.py deleted")
        except AttributeError:
            if verbosity >= 3:
                # print(f"    {package} has no settings indjection")
                print(f"    No settings declaration found")

        # urls
        try:
            insertion_string = make_insertion_string_multi_app(
                tuples_to_insert=indjections.urls
            )
            indject_string(
                urls.__file__,
                package,
                insertion_string,
                delete_only=delete_only,
                verbosity=verbosity,
                interactive=interactive,
            )
            # if verbosity >= 2 and not delete_only:
            #     print(f"    block in urls.py injected")
            # if verbosity >= 3 and delete_only:
            #     print(f"    block in urls.py deleted")
        except AttributeError:
            if verbosity >= 3:
                # print(f"    {package} has no urls indjection")
                print(f"    No urls declaration found")

        # base_top
        try:
            insertion_string = make_insertion_string_multi_app(
                tuples_to_insert=indjections.base_top
            )
            indject_string(
                base_html,
                package + "__base_top",
                insertion_string,
                after=False,
                is_template=True,
                delete_only=delete_only,
                verbosity=verbosity,
                interactive=interactive,
            )
            # if verbosity >= 2 and not delete_only:
            #     print(f"    block in base_top injected")
            # if verbosity >= 3 and delete_only:
            #     print(f"    block in base_top deleted")
        except AttributeError:
            if verbosity >= 3:
                # print(f"    {package} has no base_top")
                print(f"    No base_top declaration found")

        # base_head
        try:
            insertion_string = make_insertion_string_multi_app(
                tuples_to_insert=indjections.base_head
            )
            indject_string(
                base_html,
                package + "__base_head",
                insertion_string,
                after=False,
                reference_regex="</head>",
                is_template=True,
                delete_only=delete_only,
                verbosity=verbosity,
                interactive=interactive,
            )
            # if verbosity >= 2 and not delete_only:
            #     print(f"    block in base_head injected")
            # if verbosity >= 3 and delete_only:
            #     print(f"    block in base_head deleted")
        except AttributeError:
            if verbosity >= 3:
                # print(f"    {package} has no base_head")
                print(f"    No base_head declaration found")

        # base_body
        try:
            insertion_string = make_insertion_string_multi_app(
                tuples_to_insert=indjections.base_body
            )
            indject_string(
                base_html,
                package + "__base_body",
                insertion_string,
                after=True,
                reference_regex="<body[\s\S]*?>",
                is_template=True,
                delete_only=delete_only,
                verbosity=verbosity,
                interactive=interactive,
            )
            # regex: https://stackoverflow.com/questions/6441015/symbol-for-any-number-of-any-characters-in-regex
            # if verbosity >= 2 and not delete_only:
            #     print(f"    block in base_body injected")
            # if verbosity >= 3 and delete_only:
            #     print(f"    block in base_body deleted")
        except AttributeError:
            if verbosity >= 3:
                print(f"    No base_body declaration found")

        # base_finally i.e., the area just before the </body> tag
        try:
            insertion_string = make_insertion_string_multi_app(
                tuples_to_insert=indjections.base_finally
            )
            indject_string(
                base_html,
                package + "__base_finally",
                insertion_string,
                after=False,
                reference_regex="</body>",
                is_template=True,
                delete_only=delete_only,
                verbosity=verbosity,
                interactive=interactive,
            )
            # if verbosity >= 2 and not delete_only:
            #     print(f"    block in base_finally injected")
            # if verbosity >= 3 and delete_only:
            #     print(f"    block in base_finally deleted")
        except AttributeError:
            if verbosity >= 3:
                # print(f"    {package} has no base_finally")
                print(f"    No base_finally declaration found")

        # project_*
        # Note: filter is implicitly similar to try/except block elsewhere
        project_level_files = list(
            filter(lambda x: x.startswith("project_"), dir(indjections))
        )  # list of strings
        project_level_file_path = dirname(urls.__file__)
        for file_name in project_level_files:
            tuples_to_insert = getattr(indjections, file_name)
            insertion_string = make_insertion_string_multi_app(
                tuples_to_insert=tuples_to_insert
            )
            name_in_file_system = f'{file_name.replace("project_", "")}.py'
            file_path = join(project_level_file_path, name_in_file_system)
            Path(file_path).touch()
            indject_string(
                file_path,
                package,
                insertion_string,
                delete_only=delete_only,
                verbosity=verbosity,
                interactive=interactive,
            )
            # if verbosity >= 2:
            #     print(f"    {package} has a {file_name} declaration")
            #     print(f'    Inserting {name_in_file_system} in project configuration directory')
        if not project_level_files:
            if verbosity >= 3:
                print(f"    No project_* declarations found")

        # app_*
        # Note: filter is implicitly similar to try/except block elsewhere
        app_level_files = list(
            filter(lambda x: x.startswith("app_"), dir(indjections))
        )  # list of strings
        for file_name in app_level_files:
            for app in project_app_list:
                tuples_to_insert = getattr(indjections, file_name)
                include = indjections_settings.get("INCLUDE_APPS", None)
                exclude = indjections_settings.get("EXCLUDE_APPS", None)
                if include and exclude:
                    raise Exception(
                        f'In INDJECTIONS_SETTINGS, specify only "EXCLUDE_APPS" or "INCLUDE_APPS", but not both.'
                    )
                if include or include == {}:
                    include_this_app = (
                        app["label"] in include and package in include[app["label"]]
                    )
                elif exclude or exclude == {}:
                    include_this_app = (
                        app["label"] not in exclude
                        and package not in exclude[app["label"]]
                    )
                else:  # default: include all apps
                    include_this_app = True
                insertion_string = make_insertion_string(tuples_to_insert, app)
                name_in_file_system = f'{file_name.replace("app_", "")}.py'
                file_path = join(app["path"], name_in_file_system)
                Path(file_path).touch()  # make sure file exists
                indject_string(
                    file_path,
                    package,
                    insertion_string,
                    delete_only=delete_only or not include_this_app,
                    verbosity=verbosity,
                    interactive=interactive,
                )  # delete if excluded!
                # if verbosity >= 2:
                # print(f'    Inserting {name_in_file_system} in app "{app["label"]}"')
                # print(f'    ........................ in app "{app["label"]}"')

        if not app_level_files:
            if verbosity >= 3:
                print(f"    No app_* declarations found")

        # post (un)install hooks
        if not delete_only:
            try:
                for hook in indjections.post_hooks:
                    hook()
                if verbosity >= 2:
                    # assert False, package
                    print(f"    {len(indjections.post_hooks)} post_hooks executed")
            except AttributeError:
                if verbosity >= 3:
                    # print(f"    {package} has no post_hooks")
                    print(f"    No post_hooks found")
        else:
            try:
                for hook in indjections.post_hooks_delete:
                    hook()
                if verbosity >= 3:
                    print(
                        f"    {len(indjections.post_hooks_delete)} post_hooks_delete executed"
                    )
            except AttributeError:
                if verbosity >= 3:
                    # print(f"    {package} has no post_hooks_delete")
                    print(f"    No post_hooks_delete found")

        # final results
        if delete_only:
            if verbosity >= 3:
                print(Fore.GREEN + "    <==== Successful ====>" + Fore.RESET)
        elif verbosity >= 1:  # if 2, then verbose output implies success
            print(Fore.GREEN + "    <==== Successful ====>" + Fore.RESET)
    except ModuleNotFoundError:
        if verbosity >= 1:
            # print(f"    {package} has no defined indjections")
            print(Fore.RED + "    <==== None found ====>" + Fore.RESET)


def load_custom_installers(directory_name: str = "custom_installers") -> list:
    from indjections import package_path

    try:
        files = os.listdir(directory_name)
        try:
            files.remove("__init__.py")
        except ValueError:
            pass  # remove if __init__.py exists; otherwise do nothing
        for file in files:
            module_name = os.path.splitext(file)[0]
            exec(f"from {directory_name} import {module_name}")  # local version
            try:
                exec(f"import {package_path}.{module_name}")  # global version
            except ModuleNotFoundError:
                pass
            exec(f"""sys.modules[f'{package_path}.{module_name}'] = {module_name}""")
        # if verbosity >= 1:
        #     list_of_custom_installers = ', '.join(list(
        #         map(lambda x: x.replace('.py', ''), files)
        #     ))
        #     print(f"Using the following custom installers: {list_of_custom_installers}\n")
        return list(map(lambda x: x.replace(".py", ""), files))
    except FileNotFoundError:
        return []  # directory not found


class Command(BaseCommand):
    help = (
        "Install third party Django packages by injecting code into "
        "settings.py, urls.py, and app files."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "args",
            metavar="package_name",
            nargs="*",
            help="Specify the package name to inject code for.",
        )
        parser.add_argument(
            "--noinput",
            "--no-input",
            action="store_false",
            dest="interactive",
            help="Tells Django to NOT prompt the user for input of any kind.",
        )

    def handle(self, *package_names, **options):
        self.verbosity = options.get("verbosity", 0)
        # 0=no output
        # 1=display installations
        # 2=display installation details
        # 3=display additional installation details & clean up details
        self.interactive = options.get("interactive", False)

        custom_list = load_custom_installers()

        # not "from django.conf import settings" to prevent tests from loading Django
        settings = sys.modules[os.environ["DJANGO_SETTINGS_MODULE"]]
        indjections_settings = getattr(settings, "INDJECTIONS_SETTINGS", {})

        # import_module(settings.ROOT_URLCONF)
        urls = sys.modules[settings.ROOT_URLCONF]
        # assert False, settings.INDJECTIONS_SETTINGS

        toml_file = indjections_settings.get(
            "TOML_FILE", os.path.join(settings.BASE_DIR, "Pipfile")
        )
        toml_keys = indjections_settings.get(
            "TOML_KEYS", ("packages", "dev-packages", "indjections.extras",)
        )

        if indjections_settings.get("USE_SETUP_CFG", None):
            with open("setup.cfg", "r") as f:
                text = f.read()
            from configparser import ConfigParser

            config = ConfigParser()
            config.read("setup.cfg")
            installed_packages = config._sections["options"]["install_requires"].split(
                "\n"
            )
            installed_packages = list(filter(lambda x: x != "", installed_packages))
            installed_packages = list(
                map(
                    lambda x: x.split("==")[0]
                    .split("<=")[0]
                    .split(">=")[0]
                    .split("<")[0]
                    .split(">")[0]
                    .split("#")[0],
                    installed_packages,
                )
            )
        else:
            with open(toml_file, "r") as f:
                installed_packages = parse_toml(f.read(), toml_keys)

        if package_names:  # if users passes an argument
            installed_packages = list(
                filter(lambda x: x in package_names, installed_packages)
            )

        for package in installed_packages:
            if package == "djangorestframework":
                print(2)
            if self.verbosity >= 1:
                if package in custom_list:
                    text_to_print = f"Indjecting {package} [custom version]"
                    end = (
                        " " * (57 - len(text_to_print)) if self.verbosity == 1 else "\n"
                    )
                    print(text_to_print, end=end)
                else:
                    text_to_print = f"Indjecting {package}"
                    end = (
                        " " * (57 - len(text_to_print)) if self.verbosity == 1 else "\n"
                    )
                    print(text_to_print, end=end)
            execute_installation_file(
                package,
                settings,
                urls,
                verbosity=self.verbosity,
                interactive=self.interactive,
                delete_only=False,
            )

        if self.verbosity >= 3:
            print("=====================================")
            print("====> Cleaning up removed packages...")
            print("=====================================")
        import indjections.packages

        indjections_packages_dir = dirname(vars(indjections.packages)["__file__"])
        indjections_packages_list = listdir(indjections_packages_dir)
        indjections_packages_list = [
            f
            for f in indjections_packages_list
            if isfile(join(indjections_packages_dir, f))
        ]
        indjections_packages_list.remove("__init__.py")
        indjections_packages_list = list(
            map(lambda e: e.split(".")[0], indjections_packages_list)
        )

        packages_to_delete = list(
            filter(lambda e: e not in installed_packages, indjections_packages_list)
        )

        for package in packages_to_delete:
            # if package == "djangorestframework":
            #     print(1)
            if self.verbosity >= 3:
                print(f"Cleaning up {package}")
            execute_installation_file(
                package,
                settings,
                urls,
                delete_only=True,
                verbosity=self.verbosity,
                interactive=self.interactive,
            )
