# -*- coding: utf-8 -*-
import re
from setuptools import setup, find_packages


REQUIRES = (
    'marshmallow>=2.0.0b1',
    'SQLAlchemy>=0.7',
    'six>=1.9.0',
)


def find_version(fname):
    """Attempts to find the version number in the file names fname.
    Raises RuntimeError if not found.
    """
    version = ''
    with open(fname, 'r') as fp:
        reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
        for line in fp:
            m = reg.match(line)
            if m:
                version = m.group(1)
                break
    if not version:
        raise RuntimeError('Cannot find version information')
    return version

__version__ = find_version('marshmallow_sqlalchemy/__init__.py')


def read(fname):
    with open(fname) as fp:
        content = fp.read()
    return content

setup(
    name='marshmallow-sqlalchemy',
    version=__version__,
    description='SQLAlchemy integration with the marshmallow (de)serialization library',
    long_description=read('README.rst'),
    author='Steven Loria',
    author_email='sloria1@gmail.com',
    url='https://github.com/marshmallow-code/marshmallow-sqlalchemy',
    packages=find_packages(exclude=("test*", )),
    package_dir={'marshmallow-sqlalchemy': 'marshmallow-sqlalchemy'},
    include_package_data=True,
    install_requires=REQUIRES,
    license=read("LICENSE"),
    zip_safe=False,
    keywords='sqlalchemy marshmallow',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
)
