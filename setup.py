#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools
import sys
from os.path import dirname

# This is needed for versioneer to be importable when building with PEP 517.
# See <https://github.com/warner/python-versioneer/issues/193> and links
# therein for more information.
sys.path.append(dirname(__file__))
import versioneer


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="datalad-metadata-model",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="The Datalad Team",
    author_email="christian.moench@web.de",
    description="Datalad Metadata Model",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/christian-monch/metadata-model",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "mdc=tools.metadata_creator.main:main"
        ]
    },
    install_requires=[
        "dataclasses"
    ]
)
