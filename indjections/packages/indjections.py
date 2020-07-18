import os
import shutil
from inspect import getfile
import django

settings = """
TEMPLATES[0]['DIRS'] += [os.path.join(BASE_DIR, 'templates')]
import logging
logger = logging.getLogger('root')
logging.basicConfig(format="[%(levelname)s][%(name)s:%(lineno)s] %(message)s")
if DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
# In each py file, include "logger = logging.getLogger(__name__)"
"""

def copy_django_admin_base():
    django_root = os.path.dirname(getfile(django))
    project_root = os.getcwd()
    django_admin_base = os.path.join(
        django_root, 'contrib', 'admin', 'templates', 'admin', 'base.html')
    project_admin_base = os.path.join(
        project_root, 'templates', 'admin', 'base.html')
    if not os.path.exists(project_admin_base):  # do not overwrite
        # https://stackoverflow.com/questions/2793789/create-destination-path-for-shutil-copy-files
        os.makedirs(os.path.dirname(project_admin_base), exist_ok=True)
        shutil.copyfile(django_admin_base, project_admin_base)

hooks = [
    copy_django_admin_base,
]
