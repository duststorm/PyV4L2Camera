#!/usr/bin/env python3

import sys

from setuptools import setup, find_packages
from setuptools.extension import Extension

from PyV4L2Camera import __version__

try:
    sys.argv.remove('--use-cython')
    USE_CYTHON = True
except ValueError:
    USE_CYTHON = False

ext = '.pyx' if USE_CYTHON else '.c'
extensions = [
    Extension(
        'PyV4L2Camera/camera',
        ['PyV4L2Camera/camera' + ext],
        libraries=['v4l2', ]
    ),
    Extension(
        'PyV4L2Camera/controls',
        ['PyV4L2Camera/controls' + ext],
        libraries=['v4l2', ]
    )
]

if USE_CYTHON:
    from Cython.Build import cythonize
    extensions = cythonize(extensions)

setup(
    name='PyV4L2Camera',
    version=__version__,
    description='Simple, libv4l2 based frame grabber',
    author='Dominik Pieczyński',
    author_email='dominik.pieczynski@gmail.com',
    url='https://gitlab.com/radish/PyV4L2Camera',
    license='GNU Lesser General Public License v3 (LGPLv3)',
    ext_modules=extensions,
    extras_require={
        'examples': ['pillow', 'numpy'],
    },
    packages=find_packages()
)
