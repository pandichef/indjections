import re
import toml

# 1. unlocked = deleted and rewrite... version 1
# 2. doesn't exist = rewrite
# 3. locked = don't do anything

def indject_string(file_name, package_name, insert_string):
        with open(file_name, 'r') as f:  # https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files
            original_file_string = f.read()
        if not re.search(
                f"""\n\n### block: {package_name}/lock ###(\n|.)*### endblock: {package_name} ###""",
                original_file_string):
            file_string = re.sub(
                f"""\n\n### block: {package_name} ###(\n|.)*### endblock: {package_name} ###""",
                "", original_file_string)
            file_string += f"""
### block: {package_name} ###{insert_string}### endblock: {package_name} ###
"""
            with open(file_name, 'w') as f:  # https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files
                f.write(file_string)


def parse_toml(toml_string: str, package_header='install_requires',
               dev_package_header='extras_require.dev') -> tuple:
    tobeinstalled = toml.loads(toml_string)
    package_header_keys = package_header.split('.')
    dev_package_header_keys = dev_package_header.split('.')
    dct = tobeinstalled
    for key in package_header_keys:
        dct = dct[key]
    # package_list = []
    # dct = tobeinstalled['install_requires']
    install_requires = [x + dct[x] if dct[x] != "*" else x for x in dct]
    dct = tobeinstalled
    for key in dev_package_header_keys:
        dct = dct[key]
    # dct = tobeinstalled['extras_require']['dev']
    extras_require_dev = [x + dct[x] if dct[x] != "*" else x for x in dct]
    return install_requires, extras_require_dev
