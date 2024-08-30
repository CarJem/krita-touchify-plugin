#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PLUGIN_NAME="touchify"
KRITA_PATH="$HOME/.var/app/org.kde.krita/data/krita/pykrita"


rm -r "${KRITA_PATH:?}"/"${PLUGIN_NAME:?}"/*
cp "$SCRIPT_DIR/plugin/$PLUGIN_NAME.desktop" "${KRITA_PATH:?}/"
cp "$SCRIPT_DIR/plugin/$PLUGIN_NAME.action" "${KRITA_PATH:?}/"
cp -r "$SCRIPT_DIR/plugin/$PLUGIN_NAME" "${KRITA_PATH:?}/"