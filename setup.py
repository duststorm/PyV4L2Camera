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
    description='Simple, libv4l2 based frame grabber',
    author='Dominik Pieczyński',
    author_email='dominik.pieczynski@gmail.com',
    url='https://gitlab.com/radish/PyV4L2Camera',
    license='GNU Lesser General Public License v3 (LGPLv3)',
    ext_modules=cythonize(extensions),
    extras_require={
        'examples': ['pillow', 'numpy'],
    },
    packages=find_packages()
)
