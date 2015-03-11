# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

version = __import__('sequere').__version__

root = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(root, 'README.rst')) as f:
    README = f.read()

setup(
    name='django-sequere',
    version=version,
    description='A Django application to implement a follow system and a timeline using multiple backends (db, redis, etc.)',
    long_description=README,
    author='Florent Messa',
    author_email='florent.messa@gmail.com',
    url='http://github.com/thoas/django-sequere',
    zip_safe=False,
    include_package_data=True,
    keywords='django libraries settings redis follow timeline'.split(),
    platforms='any',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Topic :: Utilities',
    ],
    extras_require={
        'redis': ['redis'],
        'nydus': ['nydus'],
    },
    install_requires=['six'],
    tests_require=['coverage', 'exam', 'celery', 'nydus'],
    packages=find_packages(exclude=['tests']),
)
