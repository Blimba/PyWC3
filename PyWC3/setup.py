#!/usr/bin/env python3
"""Module setup utils"""
from setuptools import setup, find_packages
from __version__ import __version__ as verstr
setup(
    name="pythonlua",
    version=verstr,
    url="https://github.com/Blimba/PyWC3",
    author="Bart Limburg",
    author_email="bartlimburg@gmail.com",
    licence="Apache",
    packages=find_packages(),
    package_data={'': ['../LICENSE']},
    include_package_data=True,
    long_description="",
)