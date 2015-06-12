#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='pcnile',
    version='1.0',
    license='BSD',
    package_data = {
        '': ['*.txt',],
    },
    description='Library of web-related obtainfo functions',
    author='Obtainfo project',
    author_email='pczhaoyun@gmail.com',
    url='https://github.com/pczhaoyun/pcnile',
    packages=['pcnile'],
    platforms=['Any'],
)
