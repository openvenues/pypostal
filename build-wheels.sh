#!/usr/bin/env bash
set -e -u -x

THIS_DIR="$(pwd)"
DEPS_DIR="$THIS_DIR/deps"

ls -l /opt/python/

PYBINS=(
  "/opt/python/cp27-cp27m/bin"
  # Skip the cp27mu build, which has Unicode problems.
  "/opt/python/cp35-cp35m/bin"
  "/opt/python/cp36-cp36m/bin"
  "/opt/python/cp37-cp37m/bin"
  "/opt/python/cp38-cp38/bin"
  "/opt/python/cp39-cp39/bin"
)

function repair_wheel {
    wheel="$1"
    if ! auditwheel show "$wheel"; then
        echo "Skipping non-platform wheel $wheel"
    else
        auditwheel repair "$wheel" --plat "$PLAT" -w /io/wheelhouse/
    fi
}

cd "$THIS_DIR"
export CFLAGS="-I${DEPS_DIR}/include"
export LDFLAGS="-L${DEPS_DIR}/lib"

ls -l "${DEPS_DIR}/lib/"
cp "${DEPS_DIR}"/lib/libpostal.so* "/lib64/"

# Compile wheels
cd /io/
for PYBIN in ${PYBINS[@]}; do
    # TODO: Some way to single-source these dev dependencies?
    "${PYBIN}/pip" -qq install "six" "nose>=1.0"

    "${PYBIN}/python" /io/setup.py install
    "${PYBIN}/python" /io/setup.py build_ext --inplace
    "${PYBIN}/nosetests" --no-path-adjustment /io/postal/tests

    "${PYBIN}/pip" -qq wheel /io/ --no-deps --wheel-dir wheelhouse/
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
