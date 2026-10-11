#!/usr/bin/env bash
set -euo pipefail

project=$1
source_dir=$(mktemp -d)
curl -fsSL https://github.com/openvenues/libpostal/archive/25099c506612b34b23b1bfe286ca6321fcf06f35.tar.gz |
    tar -xz --strip-components=1 -C "$source_dir"
cd "$source_dir"
./bootstrap.sh
CFLAGS="${CFLAGS:-} -std=gnu99" ./configure --prefix="$LIBPOSTAL_PREFIX" --datadir=/usr/local/share --disable-data-download
make -j2
make install
cp LICENSE "$project/postal/LICENSE.libpostal"
cp "$LIBPOSTAL_PREFIX/bin/libpostal_data" "$project/postal/libpostal_data"
"$LIBPOSTAL_PREFIX/bin/libpostal_data" download all "$LIBPOSTAL_DATA_DIR"
