from os.path import basename
import re
import toml

# 1. unlocked = deleted and rewrite... unchanged
# 2. unlocked = deleted and rewrite... modified
# 3. doesn't exist = rewrite
# 4. locked = don't do anything


def indject_string_at(original_string: str, string_to_append: str,
                      reference_regex: str, after: bool) -> str:
    """
    >>> original_string = '<html>hello</html>'
    >>> indject_string_at(original_string, 'world', None, True)
    '<html>hello</html>world'
    >>> indject_string_at(original_string, 'world', None, False)
    'world<html>hello</html>'
    >>> indject_string_at(original_string, 'world', 'hello', True)
    '<html>helloworld</html>'
    >>> indject_string_at(original_string, 'world', 'hello', False)
    '<html>worldhello</html>'
    """
    if reference_regex is None and after:
        return original_string + string_to_append
    elif reference_regex is None and not after:
        return string_to_append + original_string
    elif after:
        return re.sub(r'(' + reference_regex + r')', r'\1' + string_to_append, original_string)
    else:
        return re.sub(r'(' + reference_regex + r')', string_to_append + r'\1', original_string)


def indject_string(file_name, package_name, insert_string, is_template=False,
                   reference_regex=None, after=True, delete_only=False):
    if is_template:
        _o = '{'
        _o2 = r'\{'  # { is apparently a special regex character
        _c = '}'
    else:
        _o = ''
        _o2 = ''
        _c = ''

    with open(file_name, 'r') as f:  # https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files
        original_file_string = f.read()

    # if re.search(f"""\n\n{_o2}### block: {package_name}/lock ###{_c}(\n|.)*{_o2}### endblock: {package_name} ###{_c}""",
    if re.search(f"""{_o2}### block: {package_name}/lock ###{_c}(\n|.)*{_o2}### endblock: {package_name} ###{_c}\n""",
            original_file_string) and not delete_only:  # note: this means that locked blocks should also be deleted
        print(f"{package_name} block found and locked in {basename(file_name)}. Doing nothing.")
    else:
        # file_string = re.sub(f"""\n\n{_o2}### block: {package_name} ###{_c}(\n|.)*{_o2}### endblock: {package_name} ###{_c}""",
        file_string = re.sub(f"""{_o2}### block: {package_name} ###{_c}(\n|.)*{_o2}### endblock: {package_name} ###{_c}\n""",
            "", original_file_string)
        found_block_and_deleted = file_string != original_file_string
        if not delete_only:
            file_string = indject_string_at(
                file_string,
                f"""{_o}### block: {package_name} ###{_c}{insert_string}{_o}### endblock: {package_name} ###{_c}\n""",
                reference_regex, after)

        # file_string += f"""
        # {_o}### block: {package_name} ###{_c}{insert_string}{_o}### endblock: {package_name} ###{_c}
        # """  # implicitly adds to the end of the file

        with open(file_name, 'w') as f:  # https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files
            f.write(file_string)

        if not delete_only:
            if found_block_and_deleted:
                print(f"{package_name} block found and deleted in {basename(file_name)}. Inserting new block.")
            else:
                print(f"{package_name} block not found in {basename(file_name)}. Inserting new block.")
        else:
            if found_block_and_deleted:
                print(f"{package_name} block found and deleted in {basename(file_name)}.")
            else:
                pass  # print(f"{package_name} block not found in {basename(file_name)}.")


def parse_toml(toml_string: str, toml_keys) -> list:
    tobeinstalled = toml.loads(toml_string)

    concatenated_packages = []
    try:
        for key_string in toml_keys:
            keys = key_string.split('.')

            # assert False, issubclass(type(tobeinstalled['dev-packages']['indjections']), InlineTableDict)
            # package_header_keys = package_header.split('.')
            # dev_package_header_keys = dev_package_header.split('.')
            dct = tobeinstalled
            for key in keys:
                print(key)
                dct = dct[key]
            # package_list = []
            # dct = tobeinstalled['install_requires']
            # install_requires = [x + dct[x] if dct[x] != "*" and not issubclass(type(dct[x]), InlineTableDict) else x for x in dct]
            packages = list(dct)
            # dct = tobeinstalled
            # for key in dev_package_header_keys:
            #     dct = dct[key]
            # dct = tobeinstalled['extras_require']['dev']
            # extras_require_dev = [x + dct[x] if dct[x] != "*" and not issubclass(type(dct[x]), InlineTableDict) else x for x in dct]
            # extras_require_dev = list(dct)
            # assert False, extras_require_dev
            concatenated_packages += packages
        # assert False, concatenated_packages
    except KeyError:
        pass  # This key wasn't found in the TOML file
    return concatenated_packages


from pprint import pprint
from pathlib import Path
import os
import sys
from django.apps import apps


def get_app_and_model_data():
    """
    History
    -------
    Refactored from get_api_strings() (see below)

    >>> pprint(get_app_and_model_data()[0]['models'])
    [{'attributes': ['id', 'name'],
      'import_path': 'tests.main.models',
      'import_string': 'from tests.main.models import Author',
      'name': 'Author',
      'name_lower': 'author'},
     {'attributes': ['id', 'text', 'author'],
      'import_path': 'tests.main.models',
      'import_string': 'from tests.main.models import Item',
      'name': 'Item',
      'name_lower': 'item'}]
    """
    settings = sys.modules[os.environ['DJANGO_SETTINGS_MODULE']]

    list_of_app_dicts = []
    for app in list(apps.get_app_configs()):
        if app.path.startswith(settings.BASE_DIR):  # local apps only
            app_dict = {'path': app.path}
            app_dict.update({'label': app.label})  # e.g., auth
            app_dict.update({'module': app.name})  # e.g., django.contrib.auth
            app_dict.update({'verbose_name': app.verbose_name})
            models = app.__dict__.get('models', None)
            model_list = []
            for model in models:
                model_dict = {}
                model_dict['name_lower'] = model
                model_dict['import_path'] = models[model].__dict__['__module__']
                model_name, model_attributes = models[model].__dict__['__doc__'][:-1].split('(')
                model_dict['name'] = model_name
                model_dict['attributes'] = model_attributes.split(', ')
                model_dict['import_string'] = f"from {model_dict['import_path']} import {model_dict['name']}"
                model_list.append(model_dict)
            app_dict['models'] = model_list
            list_of_app_dicts.append(app_dict)
    return list_of_app_dicts


# def get_api_strings(self, *args, **kwargs):
def get_api_strings():
    # UNDER CONSTRUCTION
    """
    >>> print(get_api_strings())
    from rest_framework import serializers, viewsets
    from rest_framework.permissions import IsAuthenticated
    from tests.main.models import Author
    <BLANKLINE>
    <BLANKLINE>
    class AuthorSerializer(serializers.HyperlinkedModelSerializer):
        class Meta:
            model = Author
            fields = ['id', 'name']
    <BLANKLINE>
    <BLANKLINE>
    class AuthorViewSet(viewsets.ModelViewSet):
        queryset = Author.objects.all()
        serializer_class = AuthorSerializer
    <BLANKLINE>
    <BLANKLINE>
    from tests.main.models import Item
    <BLANKLINE>
    <BLANKLINE>
    class ItemSerializer(serializers.HyperlinkedModelSerializer):
        class Meta:
            model = Item
            fields = ['id', 'text', 'author']
    <BLANKLINE>
    <BLANKLINE>
    class ItemViewSet(viewsets.ModelViewSet):
        queryset = Item.objects.all()
        serializer_class = ItemSerializer
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    """
    settings = sys.modules[os.environ['DJANGO_SETTINGS_MODULE']]

    app_list = get_app_and_model_data()  # returns a list of dicts

    for app in app_list:
        views = os.path.join(app['path'], 'views.py')
        Path(views).touch()
        insert_string = """from rest_framework import serializers, viewsets\n"""
        insert_string += """from rest_framework.permissions import IsAuthenticated\n"""
        for model in app['models']:
            insert_string += f"from {model['import_path']} import {model['name']}\n\n"
            insert_string += f"""
class {model['name']}Serializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = {model['name']}
        fields = {str(model['attributes'])}
\n"""
            insert_string += f"""
class {model['name']}ViewSet(viewsets.ModelViewSet):
    queryset = {model['name']}.objects.all()
    serializer_class = {model['name']}Serializer
\n\n"""
    return insert_string
