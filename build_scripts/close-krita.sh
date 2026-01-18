#!/bin/bash
source "$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )/zenv.env"
$EXIT_COMMAND|| echo 'Krita was not running'