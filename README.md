pypostal
--------

[![Build Status](https://travis-ci.org/openvenues/pypostal.svg?branch=master)](https://travis-ci.org/openvenues/pypostal) [![PyPI version](https://img.shields.io/pypi/v/postal.svg)](https://pypi.python.org/pypi/postal) [![License](https://img.shields.io/github/license/openvenues/pypostal.svg)](https://github.com/openvenues/pypostal/blob/master/LICENSE)

These are the official Python bindings to https://github.com/openvenues/libpostal, a fast statistical parser/normalizer for street addresses anywhere in the world.

Usage
-----

```python
from postal.expand import expand_address
expand_address('Quatre vingt douze Ave des Champs-Élysées')

from postal.parser import parse_address
parse_address('The Book Club 100-106 Leonard St, Shoreditch, London, Greater London, EC2A 4RH, United Kingdom')
```

Installation
------------

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

```
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

Compatibility
-------------

pypostal supports Python 2.7+ and Python 3.4+. These bindings are written using the Python C API and thus support CPython only. Since libpostal is a standalone C library, support for PyPy is still possible with a CFFI wrapper, but is not a goal for this repo.

Tests
-----

Make sure you have [nose](https://nose.readthedocs.org/en/latest/) installed, then run:

```
python setup.py build_ext --inplace
nosetests postal/tests
```

The ```build_ext --inplace``` business is needed so the C extensions build in the source checkout directory and are accessible/importalbe by the Python modules.
