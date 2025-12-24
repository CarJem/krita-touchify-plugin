#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

"$SCRIPT_DIR/close-krita.sh"
"$SCRIPT_DIR/install-plugin.sh"
"$SCRIPT_DIR/launch-krita.sh"
