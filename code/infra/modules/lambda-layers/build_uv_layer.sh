#!/usr/bin/env bash
set -e

LAYER_PATH=$1
PYTHON_VERSION=$2
ARCHITECTURE=$3
ZIP_NAME=$4

cd "$LAYER_PATH"
rm -rf python
rm -rf packages
mkdir python

if ! command -v uv &> /dev/null; then
  pip install --quiet uv
fi

uv export --quiet --frozen --no-dev --no-editable -o requirements.txt

if [ "$ARCHITECTURE" == "arm64" ]; then
    PLATFORM="aarch64-manylinux2014"
else
    PLATFORM="x86_64-manylinux2014"
fi

uv pip install \
   --quiet \
   --no-installer-metadata \
   --no-compile-bytecode \
   --no-build \
   --python-platform $PLATFORM \
   --python ${PYTHON_VERSION} \
   --prefix packages \
   -r requirements.txt

cp -r packages/lib python/

zip -qq -r "${ZIP_NAME}" python/

rm -rf python requirements.txt packages
