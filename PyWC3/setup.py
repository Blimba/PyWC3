#!/usr/bin/env python3
"""Module setup utils"""

from setuptools import setup, find_packages
import re
VERSIONFILE="__version__.py"
verstr, = re.findall("^__version__ = ['\"]([^'\"]*)['\"]", open(VERSIONFILE, "rt").read(), re.M)
if not verstr:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

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