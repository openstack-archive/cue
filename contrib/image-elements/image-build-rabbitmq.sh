#!/bin/bash

set -eux

# Path Settings
export CUE_HOME=$(readlink -e $(dirname $(readlink -f $0))/../..)

# BUILD_DIR Directory where builds will be performed and images will be left
export BUILD_DIR=${BUILD_DIR:-$CUE_HOME/build}

# DIB Output Image Type
export IMAGE_TYPE=${IMAGE_TYPE:-qcow2}

# Image Name
BUILD_FILE="rabbitmq-cue-image.qcow2"

# Common elements we'll use in all builds
COMMON_ELEMENTS=${COMMON_ELEMENTS:-"vm ubuntu"}

# Common Settings for all msgaas images builds
SIZE="2"
ELEMENTS="ntp hosts cue-rabbitmq-base ifmetric"
ELEMENTS_PATH="$CUE_HOME/contrib/image-elements"

# QEMU Image options
QEMU_IMG_OPTIONS='compat=0.10'

# Install some required apt packages if needed
if ! [ -e /usr/sbin/debootstrap -a -e /usr/bin/qemu-img ]; then
  sudo apt-get update
  sudo apt-get install --yes debootstrap qemu-utils
fi
 

if [ ! -d $BUILD_DIR/diskimage-builder ]; then
  echo "---> Cloning diskimage-builder"
  git clone https://git.openstack.org/openstack/diskimage-builder $BUILD_DIR/diskimage-builder
fi

if [ ! -d $BUILD_DIR/tripleo-image-elements ]; then
  echo "---> Cloning tripleo-image-elements"
  git clone https://git.openstack.org/openstack/tripleo-image-elements $BUILD_DIR/tripleo-image-elements
fi

# Setup the elements path
export ELEMENTS_PATH="$ELEMENTS_PATH:$BUILD_DIR/tripleo-image-elements/elements:$BUILD_DIR/diskimage-builder/elements"

# Prepare the build directory
if [ ! -d $BUILD_DIR/dist ]; then
  mkdir $BUILD_DIR/dist
fi

# Complete QEMU_IMG_OPTIONS
if [ ! -z "${QEMU_IMG_OPTIONS}" ]; then
    QEMU_IMG_OPTIONS="--qemu-img-options ${QEMU_IMG_OPTIONS}"
fi

# Prepare venv for diskimage-builder
virtualenv $BUILD_DIR/diskimage-builder/.venv

# Build the image
( set +u; . "$BUILD_DIR/diskimage-builder/.venv/bin/activate"; set -u;
  pushd $BUILD_DIR/diskimage-builder
  pip install -r requirements.txt
  python setup.py install
  popd
  disk-image-create -a amd64 -o $BUILD_DIR/dist/$BUILD_FILE --image-size $SIZE $QEMU_IMG_OPTIONS $COMMON_ELEMENTS $ELEMENTS
)

