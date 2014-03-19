#! /bin/bash


coverage run --branch -m doctest  ../parse_json.py ../serial_aggregator.py
coverage report ../parse_json.py ../serial_aggregator.py

