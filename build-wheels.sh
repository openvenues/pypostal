#!/usr/bin/env bash
set -e -u -x

THIS_DIR="$(pwd)"
DEPS_DIR="$THIS_DIR/deps"

ls -l /opt/python/

PYBINS=(
  "/opt/python/cp36-cp36m/bin"
  "/opt/python/cp37-cp37m/bin"
  "/opt/python/cp38-cp38/bin"
  "/opt/python/cp39-cp39/bin"
  "/opt/python/cp310-cp310/bin"
)

function repair_wheel {
    wheel="$1"
    if ! auditwheel show "$wheel"; then
        echo "Skipping non-platform wheel $wheel"
    else
        auditwheel repair "$wheel" --plat "$PLAT" -w /io/wheelhouse/
    fi
}

export CFLAGS="-I${DEPS_DIR}/include"
export LDFLAGS="-L${DEPS_DIR}/lib"

ls -l "${DEPS_DIR}/lib/"
# Without copying these to /lib64/, we get this error when trying to import postal:
# "ImportError: libpostal.so.1: cannot open shared object file: No such file or directory"
cp "${DEPS_DIR}"/lib/libpostal.so* "/lib64/"

rm -rf "/io/.eggs"
rm -rf "/io/postal.egg-info"
rm -rf "/io/build"
rm -rf "/io/dist"

export LIBPOSTAL_DATA_DIR="/libpostal/datadir/libpostal"

# Compile wheels
cd /io/
for PYBIN in ${PYBINS[@]}; do
    "${PYBIN}/pip" -qq install --editable .
    "${PYBIN}/pip" -qq install -r dev-requirements.txt
    "${PYBIN}/pytest" /io/postal/tests
    "${PYBIN}/pip" -qq wheel . --no-deps --wheel-dir wheelhouse/
done

# Bundle external shared libraries into the wheels
for whl in wheelhouse/*.whl; do
    repair_wheel "$whl"
done

cd /
# Install packages and test
for PYBIN in ${PYBINS[@]}; do
    "${PYBIN}/pip" -qq \
        install postal --no-index --find-links /io/wheelhouse
    "${PYBIN}/python" -c \
        "from postal.parser import parse_address; print(parse_address('rhode island'))"
done
