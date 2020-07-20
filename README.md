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
 
### Does this package run anything in production?
No.  `indjections` is only used during development to help with Django configurations 
and project setup.
 
## What do I need another package?
I got tired of installing packages by hand.  This project has a similar goal to [Cookiecutter Django](https://github.com/pydanny/cookiecutter-django).
I didn't love the cookiecutter approach, so I wrote `indjections` as an alternative.
[Cookiecutter Django](https://github.com/pydanny/cookiecutter-django) is a top down approach where packages are all bundled together.
So if you don't like something, you need to spend time removing code (or write your own cookiecutter).
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
