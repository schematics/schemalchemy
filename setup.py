#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

version = '0.0.1'

setup(
    name='schemalchemy',
    license='MIT',
    version=version,
    description='SchemAlchemy = Schematics + SQLAlchemy',
    url='https://github.com/schematics/schemalchemy',
    modules=['schemalchemy'],
    install_requires=['schematics', 'sqlalchemy'],
)
