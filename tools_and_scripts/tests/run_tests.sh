#! /bin/bash

cd $(dirname $0)

export PYTHONPATH="../:$PYTHONPATH"
FILES="$(find .. -name '*py')"

coverage run --branch -m doctest $FILES
coverage report $FILES

pylint --rcfile=pylint.rc $FILES
pep8 $FILES
