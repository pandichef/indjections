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
