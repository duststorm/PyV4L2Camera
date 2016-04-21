#!/usr/bin/env python3

from Cython.Build import cythonize
from setuptools import setup, find_packages
from setuptools.extension import Extension

extensions = [
    Extension(
        'PyV4L2Camera/camera',
        ['PyV4L2Camera/camera.pyx'],
        libraries=['v4l2', ]
    )
]

setup(
    name='PyV4L2Camera',
    version='0.1.dev0',
    setup_requires=['Cython>=0.24'],
    ext_modules=cythonize(extensions),
    install_requires=['Cython>=0.24'],
    extras_require={
        'examples': ['pillow'],
    },
    packages=find_packages(),
)
