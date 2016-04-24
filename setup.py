#!/usr/bin/env python3

from Cython.Build import cythonize
from setuptools import setup, find_packages
from setuptools.extension import Extension

from PyV4L2Camera import __version__

extensions = [
    Extension(
        'PyV4L2Camera/camera',
        ['PyV4L2Camera/camera.pyx'],
        libraries=['v4l2', ]
    )
]

setup(
    name='PyV4L2Camera',
    version=__version__,
    ext_modules=cythonize(extensions),
    extras_require={
        'examples': ['pillow', 'numpy'],
    },
    packages=find_packages(),
)
