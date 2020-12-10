#! /usr/bin/env python3

"""
Package setup file
"""

from setuptools import find_packages, setup

with open("README.md") as fi:
    long_description = fi.read()

packages = find_packages()

setup(
    name="f1-2020-db",
    version="0.0.1",
    author="Alastair Garner",
    author_email="alastairgarner@outlook.com",
    description="A package to record UDP telemetry data as sent by the F1 2020 game.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    # project_urls={
    #     "Source Repository": "https://gitlab.com/gparent/f1-2020-telemetry/",
    # },
    packages=packages,
    entry_points={
        "console_scripts": [
            "f1-2020-test=f1_2020_telemetry.cli.test:main",
            "f1-2020-record=f1_2020_telemetry.cli.record:main",
        ]
    },
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Games/Entertainment",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        'numpy',
        'pandas',
        'f1-2020-telem',
    ],
)
