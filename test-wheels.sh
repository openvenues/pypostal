#!/usr/bin/env bash
set -e

pip -qq install /io/wheelhouse/postal-1.1.9-cp39-cp39-manylinux_2_5_x86_64.manylinux1_x86_64.whl

export LIBPOSTAL_DATA_DIR=/datadir/libpostal

python <<EOM
from postal.parser import parse_address
print(parse_address("rhode island"))
EOM
