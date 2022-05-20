#!/bin/env python

import os
import sys
from os.path import dirname
from os.path import join as pathjoin
from setuptools import find_packages
from setuptools import setup


NAME = "msspeech"
VERSION = "3.4"


with open(pathjoin(dirname(__file__), "README.md"), encoding="UTF-8") as f:
    DESCRIPTION = f.read()

REQUIRED, REQUIRED_URL = [], []

with open("requirements.txt") as f:
    for line in f.readlines():
        if "http://" in line or "https://" in line:
            REQUIRED_URL.append(line)

        else:
            REQUIRED.append(line)


packages = sorted(set(find_packages()))

setup(
    name=NAME,
    version=VERSION,
    description="Microsoft speech synthesis from Microsoft Edge web browser read aloud.",
    long_description=DESCRIPTION,
    long_description_content_type="text/markdown",
    author="alekssamos",
    author_email="aleks-samos@yandex.ru",
    maintainer="alekssamos",
    maintainer_email="aleks-samos@yandex.ru",
    url="https://github.com/alekssamos/msspeech/",
    packages=packages,
    entry_points={
        'console_scripts': [
            'msspeech=msspeech.__main__:main',
        ],
    },
    install_requires=REQUIRED,
    dependency_links=REQUIRED_URL,
    include_package_data=True,
)
