#! /bin/bash


coverage run --branch -m doctest  ../parse_json.py
coverage report ../parse_json.py

