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
about = {}
with open(path.join(here, "bamboo_engine", "__version__.py"), "r") as f:
    exec(f.read(), about)

long_description = "next generation flow engine of bamboo-pipeline"
version = about["__version__"]

setup(
    name="bamboo-engine",
    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=version,
    description="bamboo-engine",  # noqa
    long_description=long_description,
    # The project's main homepage.
    url="https://github.com/Tencent/bk-sops/tree/sdk/bamboo-engine",
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
        "Werkzeug>=1.0.1,<2.0",
        "pyparsing>=2.2.0,<3.0",
        "mako>=1.1.4,<2.0",
        "prometheus-client>=0.9.0,<1.0.0",
    ],
    zip_safe=False,
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    # entry_points={
    #     "console_scripts": ["bk-admin=blueapps.contrib.bk_commands:bk_admin"],
    # },
)
