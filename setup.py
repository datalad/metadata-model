# -*- coding: utf-8 -*-

import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="datalad-metadata-model",
    version="0.1.0",
    author="Christian Mönch",
    author_email="christian.moench@web.de",
    description="Metadata model for datalad",
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
    install_requires=[
        "dataclasses"
    ]
)
