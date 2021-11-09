# pypostal

[![Build Status](https://travis-ci.org/openvenues/pypostal.svg?branch=master)](https://travis-ci.org/openvenues/pypostal) [![PyPI version](https://img.shields.io/pypi/v/postal.svg)](https://pypi.python.org/pypi/postal) [![License](https://img.shields.io/github/license/openvenues/pypostal.svg)](https://github.com/openvenues/pypostal/blob/master/LICENSE)

These are the official Python bindings to https://github.com/openvenues/libpostal, a fast statistical parser/normalizer for street addresses anywhere in the world.

## Usage

```python
from postal.expand import expand_address
expand_address('Quatre vingt douze Ave des Champs-Élysées')

from postal.parser import parse_address
parse_address('The Book Club 100-106 Leonard St, Shoreditch, London, Greater London, EC2A 4RH, United Kingdom')
```

## Installation

Recent releases of pypostal (>=1.2) for Linux and macOS offer binary wheels that include everything pypostal needs to work. If you are install a recent version of pypostal on one of these platforms, all you need to do is call pip:

```
pip install postal
```

Otherwise, you will first need to install libpostal by following the instructions in the remainder of this section.

### Installing libpostal + pypostal

Before using the Python bindings, you must install the libpostal C library. Make sure you have the following prerequisites:

**On Ubuntu/Debian**
```
sudo apt-get install curl autoconf automake libtool python-dev pkg-config
```
**On CentOS/RHEL**
```
sudo yum install curl autoconf automake libtool python-devel pkgconfig
```
**On Mac OSX**
```
brew install curl autoconf automake libtool pkg-config
```

**Installing libpostal**

```sh
git clone https://github.com/openvenues/libpostal
cd libpostal
./bootstrap.sh
./configure --datadir=[...some dir with a few GB of space...]
make
sudo make install

# On Linux it's probably a good idea to run
sudo ldconfig
```

To install the Python library, just run:

```
pip install postal
```

## Compatibility

pypostal supports Python 3.6+. These bindings are written using the Python C API and thus support CPython only. Since libpostal is a standalone C library, support for PyPy is still possible with a CFFI wrapper, but is not a goal for this repo.

## Tests

To run the tests, install the development requirements and run pytest:

```sh
pip install -r dev-requirements.txt
pip install -e .
pytest postal/tests
```

## Building Binary Wheels

### For Linux

To build wheels for Linux, run the following from any system that supports Docker:

```sh
pushd libpostal-image/
docker build -t openvenues/libpostal .
popd

rm -rf postal.egg-info/ postal/*.so postal/*.pyc
docker run --rm --volume `pwd`:/io openvenues/libpostal /io/build-wheels.sh
# We only want the manylinux wheels.
rm wheelhouse/*-linux_*.whl
```

### For macOS

To build wheels for macOS, you will first need to install all the versions of Python listed in `tox.ini`, since each version will get its own wheel.

Then, run the following from a macOS host:

```sh
# Install libpostal per the instructions above first.
pip install -r dev-requirements.txt
tox
delocate-wheel wheelhouse/*macosx*.whl
```
