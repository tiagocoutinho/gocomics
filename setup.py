# -*- coding: utf-8 -*-
#
# This file is part of the gocomics project
#
# Copyright (c) 2017 Tiago Coutinho
# Distributed under the MIT license. See LICENSE for more info.

import os
import sys
from setuptools import setup

requirements = [
    'grequests',
    'bs4',
]

setup(
    name='gocomics',
    version='0.0.1',
    description="downloader of gocomics comics",
    author="Tiago Coutinho",
    author_email='coutinhotiago@gmail.com',
    url='https://github.com/tiagocoutinho/gocomics',
    py_modules=['gocomics'],
    entry_points={
        'console_scripts': [
            'gocomics=gocomics:main'
        ]
    },
    install_requires=requirements,
    zip_safe=False,
    keywords='gocomics, comics',
    classifiers=[
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
