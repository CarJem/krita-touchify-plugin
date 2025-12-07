#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT_DIR=$( dirname "$SCRIPT_DIR" )
KRITA_PATH="$HOME/.var/app/org.kde.krita/data/krita/pykrita"


install_plugin() {
    PLUGIN_NAME=$1
    PLUGIN_PATH="${KRITA_PATH:?}"/"${PLUGIN_NAME:?}"
    find "$PLUGIN_PATH" ! -path "$PLUGIN_PATH" ! -name "registered_actions.action" -exec rm -r {} \;
    #rm -r "${KRITA_PATH:?}"/"${PLUGIN_NAME:?}"/*
    cp "$ROOT_DIR/plugin/$PLUGIN_NAME.desktop" "${KRITA_PATH:?}/"
    cp "$ROOT_DIR/plugin/$PLUGIN_NAME.action" "${KRITA_PATH:?}/"
    cp -r "$ROOT_DIR/plugin/$PLUGIN_NAME" "${KRITA_PATH:?}/"
}

install_plugin "touchify"
install_plugin "touchify_pie_wheels"
install_plugin "touchify-reference-tabs"
install_plugin "touchify-compact-brush-toggler"
install_plugin "touchify-brush-options"
install_plugin "touchify-color-options"
install_plugin "touchify-poser"


