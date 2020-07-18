from os.path import basename
import re
import toml

# 1. unlocked = deleted and rewrite... unchanged
# 2. unlocked = deleted and rewrite... modified
# 3. doesn't exist = rewrite
# 4. locked = don't do anything


def indject_string(file_name, package_name, insert_string):
        with open(file_name, 'r') as f:  # https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files
            original_file_string = f.read()
        if re.search(f"""\n\n### block: {package_name}/lock ###(\n|.)*### endblock: {package_name} ###""",
                original_file_string):
            print(f"{package_name} block found and locked in {basename(file_name)}. Doing nothing.")
        else:
            file_string = re.sub(f"""\n\n### block: {package_name} ###(\n|.)*### endblock: {package_name} ###""",
                "", original_file_string)
            found_block_and_deleted = file_string != original_file_string
            file_string += f"""
### block: {package_name} ###{insert_string}### endblock: {package_name} ###
"""
            with open(file_name, 'w') as f:  # https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files
                f.write(file_string)
            if found_block_and_deleted:
                print(f"{package_name} block found and deleted in {basename(file_name)}. Inserting new block.")
            else:
                print(f"{package_name} block not found in {basename(file_name)}. Inserting new block.")



def parse_toml(toml_string: str, package_header='packages',
               dev_package_header='dev-packages') -> tuple:
    from toml.decoder import InlineTableDict
    tobeinstalled = toml.loads(toml_string)
    # assert False, issubclass(type(tobeinstalled['dev-packages']['indjections']), InlineTableDict)
    package_header_keys = package_header.split('.')
    dev_package_header_keys = dev_package_header.split('.')
    dct = tobeinstalled
    for key in package_header_keys:
        dct = dct[key]
    # package_list = []
    # dct = tobeinstalled['install_requires']
    # install_requires = [x + dct[x] if dct[x] != "*" and not issubclass(type(dct[x]), InlineTableDict) else x for x in dct]
    install_requires = list(dct)
    dct = tobeinstalled
    for key in dev_package_header_keys:
        dct = dct[key]
    # dct = tobeinstalled['extras_require']['dev']
    # extras_require_dev = [x + dct[x] if dct[x] != "*" and not issubclass(type(dct[x]), InlineTableDict) else x for x in dct]
    extras_require_dev = list(dct)
    # assert False, extras_require_dev
    return install_requires, extras_require_dev
