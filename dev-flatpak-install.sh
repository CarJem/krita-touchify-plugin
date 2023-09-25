#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PLUGIN_NAME="vaporjem-tweaks"


rm -r ~/.var/app/org.kde.krita/data/krita/pykrita/$PLUGIN_NAME/*
cp "$SCRIPT_DIR/plugin/$PLUGIN_NAME.desktop" ~/.var/app/org.kde.krita/data/krita/pykrita/
cp "$SCRIPT_DIR/plugin/$PLUGIN_NAME.action" ~/.var/app/org.kde.krita/data/krita/pykrita/
cp -r "$SCRIPT_DIR/plugin/$PLUGIN_NAME" ~/.var/app/org.kde.krita/data/krita/pykrita/