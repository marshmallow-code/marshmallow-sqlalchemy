# -*- coding: utf-8 -*-
import re
from setuptools import setup, find_packages


INSTALL_REQUIRES = ("marshmallow>=2.0.0", "SQLAlchemy>=0.9.7")
EXTRAS_REQUIRE = {
    "tests": ["pytest", "mock"],
    "lint": [
        "flake8==3.7.7",
        'flake8-bugbear==19.3.0; python_version >= "3.5"',
        "pre-commit==1.17.0",
    ],
}
EXTRAS_REQUIRE["dev"] = EXTRAS_REQUIRE["tests"] + EXTRAS_REQUIRE["lint"] + ["tox"]


def find_version(fname):
    """Attempts to find the version number in the file names fname.
    Raises RuntimeError if not found.
    """
    version = ""
    with open(fname, "r") as fp:
        reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
        for line in fp:
            m = reg.match(line)
            if m:
                version = m.group(1)
                break
    if not version:
        raise RuntimeError("Cannot find version information")
    return version


def read(fname):
    with open(fname) as fp:
        content = fp.read()
    return content


setup(
    name="marshmallow-sqlalchemy",
    version=find_version("src/marshmallow_sqlalchemy/__init__.py"),
    description="SQLAlchemy integration with the marshmallow (de)serialization library",
    long_description=read("README.rst"),
    author="Steven Loria",
    author_email="sloria1@gmail.com",
    url="https://github.com/marshmallow-code/marshmallow-sqlalchemy",
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    license="MIT",
    zip_safe=False,
    keywords="sqlalchemy marshmallow",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    test_suite="tests",
    project_urls={
        "Changelog": "https://marshmallow-sqlalchemy.readthedocs.io/en/latest/changelog.html",
        "Issues": "https://github.com/marshmallow-code/marshmallow-sqlalchemy/issues",
        "Funding": "https://opencollective.com/marshmallow",
    },
)
