#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import setuptools
import versioneer

print(os.getcwd())
sys.path.insert(0, os.getcwd())
print(sys.path)


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="datalad-metadata-model",
    version=versioneer.get_version(),
    author="The Datalad Team",
    author_email="christian.moench@web.de",
    description="Datalad Metadata Model",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/christian-monch/metadata-model",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha"
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
