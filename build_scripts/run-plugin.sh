#!/bin/bash
source "$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )/zenv.env"

"$SCRIPT_DIR/close-krita.sh"
"$SCRIPT_DIR/install-plugin.sh"
$START_COMMAND
