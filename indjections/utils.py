import os
import subprocess
import functools
from contextlib import redirect_stdout
from io import StringIO


def suppress_stdout(func):
    """
    >>> @suppress_stdout
    ... def func():
    ...     print('Returning 1')
    ...     return 1
    >>> func()
    1
    """
    @functools.wraps(func)
    def wrapper_suppress_stdout(*args, **kwargs):
        with redirect_stdout(StringIO()):
            return func(*args, **kwargs)
    return wrapper_suppress_stdout


def run_command(command):
    if os.path.exists('Pipfile.lock'):
        subprocess.run(f"pipenv run {command}", shell=True, check=True, capture_output=True)
    elif os.path.exists('poetry.lock'):
        subprocess.run(f"poetry run {command}", shell=True, check=True, capture_output=True)
    else:
        subprocess.run(f"{command}", shell=True, check=True, capture_output=True)
