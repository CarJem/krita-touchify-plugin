#!/bin/bash
source "$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )/zenv.env"

rm -r "${ROOT_DIR:?}"/plugin/"${TOUCHIFY_PLUGIN_NAME:?}"/resources/*
cp -r "$KRITA_PATH/$TOUCHIFY_PLUGIN_NAME"/resources "${ROOT_DIR:?}"/plugin/"${TOUCHIFY_PLUGIN_NAME:?}"