from setuptools import setup, find_packages
from os import path

from io import open

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

with open(path.join(here, "Pipfile"), encoding="utf-8") as f:
    import toml  # requires pyproject.toml file
    tobeinstalled = toml.loads(f.read())

dct = tobeinstalled['packages']  # dictionary
install_requires = [x + dct[x] if dct[x] != "*" else x for x in dct]
dct = tobeinstalled['dev-packages']
extras_require = {'dev': [x + dct[x] if dct[x] != "*" else x for x in dct]}
# Note: this requires a pyproject.toml file with the following contents:
# [build-system]
# requires = ["setuptools", "wheel", "toml"]


setup(
    name="indjections",  # Required
    version="0.0.3",  # Required
    description="Enables one-line installation of Django packages by injecting code in the right places.",  # Optional
    long_description=long_description,  # Optional
    long_description_content_type="text/markdown",  # Optional (see note above)
    # author="pandichef",  # Optional
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        # "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        # "Intended Audience :: Developers",
        # "Topic :: Software Development :: Build Tools",
        # Pick your license as you wish
        # "License :: OSI Approved :: MIT License",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        # These classifiers are *not* checked by 'pip install'. See instead
        # 'python_requires' below.
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    packages=find_packages(exclude=["contrib", "docs", "tests"]),  # Required
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, <4",
    install_requires=install_requires,
    extras_require=extras_require,
    # install_requires=[
    #     "django",
    #     'toml',
    #     'colorama',
    # ],  # Optional
    # extras_require={
    #     "dev": [
    #         # 'django-debug-toolbar',
    #         'pytest',
    #         # 'pytest-mock',
    #         'ipython',
    #         'pytest-cov',
    #         'pytest-django',
    #     ]
    # },  # Optional
    dependency_links=[],
    # project_urls={  # Optional
    #     "Bug Reports": "https://github.com/pypa/sampleproject/issues",
    #     "Funding": "https://donate.pypi.org",
    #     "Say Thanks!": "http://saythanks.io/to/example",
    #     "Source": "https://github.com/pypa/sampleproject/",
    # },
)
