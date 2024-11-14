#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
KRITA_PATH="$HOME/.var/app/org.kde.krita/data/krita/pykrita"


install_plugin() {
    PLUGIN_NAME=$1
    rm -r "${KRITA_PATH:?}"/"${PLUGIN_NAME:?}"/*
    cp "$SCRIPT_DIR/plugin/$PLUGIN_NAME.desktop" "${KRITA_PATH:?}/"
    cp "$SCRIPT_DIR/plugin/$PLUGIN_NAME.action" "${KRITA_PATH:?}/"
    cp -r "$SCRIPT_DIR/plugin/$PLUGIN_NAME" "${KRITA_PATH:?}/"
}

install_plugin "touchify"
install_plugin "touchify-reference-tabs"
install_plugin "touchify-compact-brush-toggler"
install_plugin "touchify-brush-options"
install_plugin "touchify-color-options"


