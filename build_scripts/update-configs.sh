#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT_DIR=$( dirname "$SCRIPT_DIR" )
PLUGIN_NAME="touchify"
KRITA_PATH="$HOME/.var/app/org.kde.krita/data/krita/pykrita"
PLUGIN_PATH="$KRITA_PATH/$PLUGIN_NAME"


rm -r "${ROOT_DIR:?}"/plugin/"${PLUGIN_NAME:?}"/resources/*

cp -r "${PLUGIN_PATH:?}"/resources "${ROOT_DIR:?}"/plugin/"${PLUGIN_NAME:?}"