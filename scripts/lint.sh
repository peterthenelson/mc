#!/bin/bash

hash pylint 2>/dev/null || { echo >&2 "Please install pylint."; exit 1; }

cd "$(git rev-parse --show-toplevel)"
pylint --rcfile=.pylintrc $(find . -iname '*.py')
