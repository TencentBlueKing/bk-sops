"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# To use a consistent encoding
from codecs import open
from os import path

# Always prefer setuptools over distutils
from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()
version = __import__("pipeline").__version__

setup(
    name="bamboo-pipeline",
    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=version,
    description="pipeline",  # noqa
    long_description=long_description,
    # The project's main homepage.
    url="",
    # Author details
    author="Blueking",
    author_email="Blueking",
    include_package_data=True,
    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(),
    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],
    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        # Base
        "Django>=2.2.6,<3.0",
        "requests>=2.22.0,<=2.23.0",
        "celery>=4.4.0,<5.0",
        "django-celery-beat==2.0.0",
        "django-celery-results==1.2.1",
        "Mako>=1.0.6,<2.0",
        "pytz==2019.3",
        # pipeline
        "jsonschema==2.5.1",
        "ujson==1.35",
        "pyparsing==2.2.0",
        "redis==3.2.0",
        "redis-py-cluster==2.1.0",
        "django-timezone-field==4.0",
        "boto3==1.9.130",
        "Werkzeug==1.0.1",
    ],
    zip_safe=False,
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    # entry_points={
    #     "console_scripts": ["bk-admin=blueapps.contrib.bk_commands:bk_admin"],
    # },
)
