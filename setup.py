import argparse
import os
import subprocess
import sys

from setuptools import setup, Extension, Command, find_packages
from setuptools.command.build_py import build_py
from setuptools.command.build_ext import build_ext
from setuptools.command.install import install
from distutils.errors import DistutilsArgError

this_dir = os.path.realpath(os.path.dirname(__file__))


def main():
    setup(
        name='pypostal',
        version='0.3',
        install_requires=[
            'six',
        ],
        setup_requires=[
            'nose>=1.0'
        ],
        ext_modules=[
            Extension('postal._expand',
                      sources=['postal/pyexpand.c'],
                      libraries=['postal'],
                      include_dirs=['/usr/local/include'],
                      library_dirs=['/usr/local/lib'],
                      extra_compile_args=['-std=c99',
                                          '-Wno-unused-function'],
                      ),
            Extension('postal._parser',
                      sources=['postal/pyparser.c'],
                      libraries=['postal'],
                      include_dirs=['/usr/local/include'],
                      library_dirs=['/usr/local/lib'],
                      extra_compile_args=['-std=c99',
                                          '-Wno-unused-function'],
                      ),
        ],
        packages=find_packages(),
        zip_safe=False,
        url='http://mapzen.com',
        description='Fast address standardization and deduplication',
        license='MIT License',
        maintainer='mapzen.com',
        maintainer_email='pelias@mapzen.com'
    )


if __name__ == '__main__':
    main()
