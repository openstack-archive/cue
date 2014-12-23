#!/bin/bash

DIR=$(readlink -e $(dirname $(readlink -f $0)))

pushd $DIR

for f in lib/*; do
    if [ ! -e "$DIR/../../../devstack/$f" ]; then
        echo "Installing symlink for $f"
        ln -fs $DIR/$f $DIR/../../../devstack/$f
    fi
done

popd
