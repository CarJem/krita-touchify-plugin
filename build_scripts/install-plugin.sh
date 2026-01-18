#!/bin/bash
source "$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )/zenv.env"

install_plugin() {
    PLUGIN_NAME=$1
    PLUGIN_PATH="${KRITA_PATH:?}"/"${PLUGIN_NAME:?}"
    find "$PLUGIN_PATH" ! -path "$PLUGIN_PATH" ! -name "registered_actions.action" -exec rm -r {} \;
    #rm -r "${KRITA_PATH:?}"/"${PLUGIN_NAME:?}"/*
    cp "$ROOT_DIR/plugin/$PLUGIN_NAME.desktop" "${KRITA_PATH:?}/"
    cp "$ROOT_DIR/plugin/$PLUGIN_NAME.action" "${KRITA_PATH:?}/"
    cp -r "$ROOT_DIR/plugin/$PLUGIN_NAME" "${KRITA_PATH:?}/"
}

install_plugin "jemlib"
install_plugin "touchify"
install_plugin "touchify_brush_options"
install_plugin "touchify_color_options"
install_plugin "touchify_compact_brush_toggler"
install_plugin "touchify_quick_actions"
install_plugin "touchify_sub_view"



