import os
from indjections.utils import run_command
# from indjections.core import suppress_stdout


def startapp_users():
    if not os.path.exists('users'):
        run_command("python manage.py startapp users")


def create_user_model():
    with open('./users/models.py', 'w') as f:
        f.write("""from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass
""")


pre_hooks = [
    startapp_users,
    create_user_model
]

settings = """
INSTALLED_APPS += ['users']
AUTH_USER_MODEL = 'users.User'
"""

# def make_migrations():
#     run_command("python manage.py makemigrations users")
#
# def migrate():
#     run_command("python manage.py migrate")  # migrate everything since this is app #1
#
# post_hooks = [
#     make_migrations,
#     migrate,
# ]
