#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name='PyV4L2Camera',
    version='0.1.dev0',
    setup_requires=['cffi>=1.5.2'],
    cffi_modules=['PyV4L2Camera/v4l2_build.py:ffi'],
    install_requires=['cffi>=1.5.2'],
    extras_require={
        'examples': ['pillow'],
    },
    packages=find_packages(),
)
