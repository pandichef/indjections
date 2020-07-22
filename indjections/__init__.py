from importlib import import_module

package_path="indjections.packages"


def get_installer(package, package_path=package_path):
    return import_module(f'{package_path}.{package}')  # this fails on python 3.5
