# Indjections
This project enables one-line installation of Django packages by
injecting code in the _right_ places.

## Installation
Install using `pip`...

    pip install indjections

or, if using [pipenv](https://pipenv.pypa.io/en/latest/)...

    pipenv install indjections --dev

Add `'indjections'` to your `INSTALLED_APPS` setting.
```python
INSTALLED_APPS = [
    ...
    'indjections',
]
```

## Example
By default, `indjections` assumes your [TOML](https://github.com/toml-lang/toml) file is a [Pipfile](https://github.com/pypa/pipfile) in the
project root.  For example, say your [Pipfile](https://github.com/pypa/pipfile) has the following packages:
```toml
[dev-packages]
django-debug-toolbar = "*"

[packages]
djangorestframework = "*"
django-hijack = "*"
```

To install these packages, you just have to run a Django management command:
```
python manage.py indject
```

This will auto-insert code into `settings.py`, `urls.py`, and `base.html`
as described by the package's documentation.  For example, for `django-hijack`, the following
snippet is added to `settings.py` (as described in the [documentation](https://django-hijack.readthedocs.io/en/stable/#installation)):
```python
### block: django-hijack ####
INSTALLED_APPS += ['hijack', 'compat']
### endblock: django-hijack ####
```

Moreover, if you remove this package from your project's [Pipfile](https://github.com/pypa/pipfile) and rerun `python manage.py indject`,
then `indjections` will search for `### block: django-hijack ####`/`### endblock: django-hijack ####` and delete this text.

That's it!

Oh, one more thing... `indjections` assumes that `base.html` is
the Django admin `base.html` and is located at your project root's `templates/admin/base.html`.
If you want to use another `base.html`, you can add a setting to your project's `settings.py`:

```python
INDJECTIONS_SETTINGS = {
    'BASE_HTML': os.path.join(BASE_DIR, 'templates', 'custom_base.html')
}
```

## Q&A
### What if I want to modify the inserted code?
You have two options:
1. If you change `### block: django-hijack ####` to `### block: django-hijack/lock ####`,
then `injections` will not reinsert code if `python manage.py indject` is run again.
However, if the package is removed from the [TOML](https://github.com/toml-lang/toml) file, then `indjections`
will delete the block even if `lock` appears in the block header.
1. `indjections` installation files are regular Python modules.  So if you 
create a custom installer and drop it into `{project_root_directory}/indjections/packages/{package_name}.py`,
then that's the version that will be used.
1. `indjections` also includes a convenience utility to monkey patch variables in 
installion files.  For example, say the default installer for 
`djangorestframework` has this definition...
```python
TYPE_OF_SERIALIZER = "ModelSerializer"
```
To change this to `HyperlinkedModelSerializer`, you can include the following in
your project's `settings.py`...
```python
from indjections import get_installer
get_installer('djangorestframework').TYPE_OF_SERIALIZER  = 'HyperlinkedModelSerializer'
```

### What if I don't use pipenv?
The packages can be defined with _any_ [TOML](https://github.com/toml-lang/toml) file.  For example, if you use [poetry](https://python-poetry.org/),
then add the following to your project's `settings.py`:
```python
INDJECTIONS_SETTINGS = {
    'TOML_FILE': os.path.join(BASE_DIR, 'pyproject.toml'),
    'TOML_KEYS': ["tool.poetry.dependencies", "tool.poetry.dev-dependencies"],
}
```

### How do I create my own installation file?

#### Basic Implementation
`indjections` looks for a module named `indjections.packages.{package_name}`.
This declaratively defines 6 locations in a Django project:

`settings`: The bottom of `settings.py` as defined by the `DJANGO_SETTINGS_MODULE` environment variable.

`urls`: The bottom of `urls.py` as defined by `settings.ROOT_URLCONF`.

`base_top`: The very top of `base.html` e.g., `{% load i18n %}`

`base_head`: The bottom of the `<head>` section in `base.html` e.g., custom CSS.

`base_body`: The top of the `<body>` section in `base.html`.

`base_finally`: The bottom of the `<body>` section in `base.html` e.g., Javascript `<script>` tags

These 6 sections seem to cover the vast majority of Django package installation requirements.

Additionally, `indjections` provides 4 hooks:

`pre_hook`: Functions run before inserting code (for each package separately)

`post_hook`: Functions run after inserting code (for each package separately)

`pre_hook_delete`: Functions run before deleting code (for each package separately); in other words,
if the package is removed from the [TOML](https://github.com/toml-lang/toml) file

`post_hook_delete`: Functions run after deleting code (for each package separately); in other words,
if the package is removed from the [TOML](https://github.com/toml-lang/toml) file

For example, the installation file for `django` might include a `post_hook`
to copy Django admin template files to the project root directory.

#### Advanced Implementation (THESE FEATURES ARE UNDER CONSTRUCTION)
The 6 locations also support insertions of app and model level code.  These are 
specified as a tuple, where the first parameter is at the project level, the second
at the app level, and the third at the model level.  For example, say our project
has two apps. `app1` consists of models `Model1` and `Model2` and `app2` consists
of models `Model3` and `Model4`.  Moreover, we have an installer called 
`_simple_print` with the following content...

```python
settings = (
    '\n# project level code',
    '\nprint("{label}")',  # "label" is a Django name at the app level
    '\nprint("{app_label}:{object_name}")',  # "app_label" and "object_name" are at the model level
)
```

This produces the following text in `settings.py`...
```python
### block: _simple_print ####
# project level code
print("app1")
print("app1:Model1")
print("app1:Model2")
print("app2")
print("app2:Model3")
print("app2:Model4")
### endblock: _simple_print ####
```

Note that `settings = "print('hello')"` is equivalent to `settings = ("print('hello')",)`.

Finally, installation files can have variables of the form `app_*`,
which will insert code into app files of the form `app_*.py`.  Here, the first 
element of the tuple variable is at the **app** level and the second element is 
at the **model level**.  For example, say the installer for `djangorestframework` 
has the following content...

```python
app_serializers = ("""
from rest_framework import serializers
""","""
class {object_name}Serializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = {object_name}
        fields = {field_names}
""")
```

This will produce the following in `app1/serializers.py`...
```python
### block: djangorestframework ####
from rest_framework import serializers

class Model1Serializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Model1
        fields = ['field1', 'field2', 'field3']

class Model2Serializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Model2
        fields = ['field1', 'field2', 'field3']
### endblock: djangorestframework ####
```

and the corresponding insertion in `app2/serializers.py`.

By default, all apps and models in the _project_ are including.  (Obviously, 
this won't impact third party packages in any way.)  To include/exclude a subset, 
use the following syntax in the installation file...

```python
include = ['app1', 'app2__model1']
```

which, in the above example, is equivalent to...

```python
exclude = ['app2__model2']
```
 
Finally, to see the full list of app and model inspection variables, run 
the following in the console...
```python
from indjections.core import get_app_and_model_data
print(get_app_and_model_data())
```
 
### Does this package run anything in production?
No.  `indjections` is only used during development to help with Django configurations 
and project setup.
 
## Why do I need another package?
I got tired of installing packages by hand.  This project has a similar goal to [Cookiecutter Django](https://github.com/pydanny/cookiecutter-django).
I didn't love the cookiecutter approach, so I wrote `indjections` as an alternative.
[Cookiecutter Django](https://github.com/pydanny/cookiecutter-django) is a top down approach where packages are all bundled together.
So if you don't like something, you need to spend time removing code (or writing your own cookiecutter).
`indjections` is a bottom up approach i.e., you can do the usual `django-admin startproject {project_name}`
and then let `python manage.py indject` insert code in the right places.

## Bonus Example: Configuring [React.js](https://reactjs.org/) with Django
After parsing the relevant [TOML](https://github.com/toml-lang/toml) file,
`indjections` looks for the equivalent file name in `indjections.packages.{package_name}`.  If it
finds the file, the installation procedure begins.

But note that the string reference found in the [TOML](https://github.com/toml-lang/toml) file 
does _not_ actually need to be a Python package.  Take the following example:
```toml
[dev-packages]
django-debug-toolbar = "*"

[packages]
djangorestframework = "*"
django-hijack = "*"

[indjections.extras]
_create-react-app = "*"
```
There is no Python package called `_create-react-app`.  However, `indjections` ships
with a `_create-react-app.py` installation file.  This will automatically execute [create-react-app](https://reactjs.org/docs/create-a-new-react-app.html#create-react-app)
and add a reasonable set of configurations for a Django project to serve the [React.js](https://reactjs.org/) app's static files.  More specifically, the installer:
* Runs `npx create-react-app reactapp` in the project's root directory
* Sets `STATICFILES_DIRS` and `TEMPLATES` to plug Django into the React app
* Sets Django's `autoreload` signal to watch for file changes in the React app; when files change,
the React app is rebuilt *and* the Django server restarts.

Of course, this might not be the optimal setup for your needs, but a) it works out of the box and b)
 it's a good starting point for customization.
 
By the way, `indjections.extras` is a special name.  By default,
`indjections` looks for `dev-packages`, `packages`, and `indjections.extras`.

## Supported Packages

### Currently Supported
* [django-debug-toolbar](https://django-debug-toolbar.readthedocs.io/en/latest/installation.html)
* [djangorestframework](https://www.django-rest-framework.org/#installation)
* [django-hijack](https://django-hijack.readthedocs.io/en/stable/#installation)

### Seeking Contributors for the Following Packages
* django-filter
* django-allauth
* django-cors-headers
* django-tables2
* djangoql
* django-material-admin
