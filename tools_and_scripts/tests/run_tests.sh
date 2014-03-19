#! /bin/bash
export PYTHONPATH="../:$PYTHONPATH"
FILES="$(find .. -name '*py')"

coverage run --branch -m doctest $FILES
coverage report $FILES

pylint --rcfile=$(dirname $0)/pylint.rc $FILES
pep8 $FILES
