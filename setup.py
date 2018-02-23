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


VERSION = '1.1.7'


def main():
    setup(
        name='postal',
        version=VERSION,
        install_requires=[
            'six',
        ],
        setup_requires=[
            'nose>=1.0'
        ],
        ext_modules=[
            Extension('postal._expand',
                      sources=['postal/pyexpand.c', 'postal/pyutils.c'],
                      libraries=['postal'],
                      include_dirs=['/usr/local/include'],
                      library_dirs=['/usr/local/lib'],
                      extra_compile_args=['-std=c99'],
                      ),
            Extension('postal._parser',
                      sources=['postal/pyparser.c', 'postal/pyutils.c'],
                      libraries=['postal'],
                      include_dirs=['/usr/local/include'],
                      library_dirs=['/usr/local/lib'],
                      extra_compile_args=['-std=c99'],
                      ),
            Extension('postal._token_types',
                      sources=['postal/pytokentypes.c'],
                      libraries=['postal'],
                      include_dirs=['/usr/local/include'],
                      library_dirs=['/usr/local/lib'],
                      extra_compile_args=['-std=c99'],
                      ),
            Extension('postal._tokenize',
                      sources=['postal/pytokenize.c', 'postal/pyutils.c'],
                      libraries=['postal'],
                      include_dirs=['/usr/local/include'],
                      library_dirs=['/usr/local/lib'],
                      extra_compile_args=['-std=c99'],
                      ),
            Extension('postal._normalize',
                      sources=['postal/pynormalize.c', 'postal/pyutils.c'],
                      libraries=['postal'],
                      include_dirs=['/usr/local/include'],
                      library_dirs=['/usr/local/lib'],
                      extra_compile_args=['-std=c99'],
                      ),
            Extension('postal._near_dupe',
                      sources=['postal/pyneardupe.c', 'postal/pyutils.c'],
                      libraries=['postal'],
                      include_dirs=['/usr/local/include'],
                      library_dirs=['/usr/local/lib'],
                      extra_compile_args=['-std=c99'],
                      ),
            Extension('postal._dedupe',
                      sources=['postal/pydedupe.c', 'postal/pyutils.c'],
                      libraries=['postal'],
                      include_dirs=['/usr/local/include'],
                      library_dirs=['/usr/local/lib'],
                      extra_compile_args=['-std=c99'],
                      ),
        ],
        packages=find_packages(),
        package_data={
            'postal': ['*.h']
        },
        zip_safe=False,
        url='https://github.com/openvenues/pypostal',
        download_url='https://github.com/openvenues/pypostal/tarball/{}'.format(VERSION),
        description='Python bindings to libpostal for fast international address parsing/normalization',
        license='MIT License',
        maintainer='mapzen.com',
        maintainer_email='pelias@mapzen.com',
        classifiers=[
            'Intended Audience :: Developers',
            'Intended Audience :: Information Technology',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: C',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: POSIX :: Linux',
            'Topic :: Text Processing :: Linguistic',
            'Topic :: Scientific/Engineering :: GIS',
            'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
            'Topic :: Software Development :: Libraries :: Python Modules'
        ],
    )


if __name__ == '__main__':
    main()
