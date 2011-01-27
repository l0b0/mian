#!/bin/bash

set -o errexit -o nounset

cd -- "$(dirname -- "$(readlink -fn -- "$0")")"

# Test
python setup.py test

# Build
python setup.py ${1:-} bdist_egg bdist_rpm sdist upload

# Cleanup
python setup.py clean
rm -fr *.pyc build dist *.egg-info
