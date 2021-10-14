#!/usr/bin/env bash
set -e -u -x

THIS_DIR="$(pwd)"
DEPS_DIR="$THIS_DIR/deps"
LIBPOSTAL_GIT_TAG="9c975972985b54491e756efd70e416f18ff97958"

yum install -y \
    curl \
    autoconf \
    automake \
    libtool \
    python-devel \
    pkgconfig

mkdir -p "$DEPS_DIR"
git clone https://github.com/openvenues/libpostal
pushd libpostal
git checkout "$LIBPOSTAL_GIT_TAG"

./bootstrap.sh
./configure \
    --datadir="$(pwd)/datadir" \
    --prefix="$DEPS_DIR" \
    --bindir="$DEPS_DIR"
    # --disable-data-download
make install

popd
