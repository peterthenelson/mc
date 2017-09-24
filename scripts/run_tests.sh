#!/bin/bash
set -e
cd "$(git rev-parse --show-toplevel)"
python -m unittest discover -p '*_test.py'
