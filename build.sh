#!/bin/sh

# Requires rpm package
# Reintroduce bdist_wininst when Windows building works again
cd $(dirname $0) && \
python setup.py test && \
python setup.py $1 bdist_egg bdist_rpm sdist upload clean && \
rm -fr *.pyc build dist *.egg-info
