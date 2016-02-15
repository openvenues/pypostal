pypostal
--------

[![Build Status](https://travis-ci.org/openvenues/pypostal.svg?branch=master)](https://travis-ci.org/openvenues/pypostal)

These are the official Python bindings to https://github.com/openvenues/libpostal, a fast statistical parser/normalizer for street addresses anywhere in the world.

Usage
-----

```python
from postal.expand import expand_address
expand_address('Quatre vignt douze Ave des Champs-Élysées')

from postal.parser import parse_address
parse_address('The Book Club 100-106 Leonard St, Shoreditch, London, Greater London, EC2A 4RH, United Kingdom')
```

Installation
------------

Before using the Python bindings, you must install the libpostal C library. Make sure you have the following prerequisites:

**On Linux (Ubuntu)**
```
sudo apt-get install libsnappy-dev autoconf automake libtool python-dev
```

**On Mac OSX**
```
sudo brew install snappy autoconf automake libtool
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
git clone https://github.com/openvenues/pypostal
cd pypostal
python setup.py install
```

If you want to import or run tests straight from your source checkout, use:

```
python setup.py build_ext --inplace
```

Compatibility
-------------

pypostal supports Python 2.7+ and Python 3.4+. These bindings are written using the Python C API and thus support CPython only. Since libpostal is a standalone C library, support for PyPy is still possible with a ctypes or CFFI wrapper, but is not a goal for this repo.

Tests
-----

Make sure you have [nose](https://nose.readthedocs.org/en/latest/) installed, then run:

```
nosetests postal/tests
```
