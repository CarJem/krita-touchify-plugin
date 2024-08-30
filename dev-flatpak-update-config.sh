#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PLUGIN_NAME="touchify"
KRITA_PATH="$HOME/.var/app/org.kde.krita/data/krita/pykrita"
PLUGIN_PATH="$KRITA_PATH/$PLUGIN_NAME"


rm -r "${SCRIPT_DIR:?}"/plugin/"${PLUGIN_NAME:?}"/resources/*
rm -r "${SCRIPT_DIR:?}"/plugin/"${PLUGIN_NAME:?}"/configs/*

cp -r "${PLUGIN_PATH:?}"/resources "${SCRIPT_DIR:?}"/plugin/"${PLUGIN_NAME:?}"
cp -r "${PLUGIN_PATH:?}"/configs "${SCRIPT_DIR:?}"/plugin/"${PLUGIN_NAME:?}"