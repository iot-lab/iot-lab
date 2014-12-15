#! /usr/bin/env python
# -*- coding:utf-8 -*-

""" Install some of the scripts.
Intended to be run on the ssh frontends """

from setuptools import setup

setup(
    name='iotlabtools',
    version='1.0.0',
    description='IoT-LAB testbed command-line tools',
    author='IoT-LAB Team',
    author_email='admin@iot-lab.info',
    url='http://www.iot-lab.info',
    download_url='http://github.com/iot-lab/iot-lab/tools_and_scripts/',
    py_modules=['serial_aggregator'],
    entry_points={
        'console_scripts': ['serial_aggregator = serial_aggregator:main'],
    },
    classifiers=['Development Status :: 4 - Beta',
                 'Programming Language :: Python',
                 'Intended Audience :: End Users/Desktop',
                 'Environment :: Console',
                 'Topic :: Utilities', ],
    install_requires=['iotlabcli>=1.4.0'],
)
