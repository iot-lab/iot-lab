#! /usr/bin/env python
# -*- coding:utf-8 -*-

""" Install some of the scripts.
Intended to be run on the ssh frontends """

import sys
from setuptools import setup, find_packages


def get_version():
    """ Extract module version without importing file
    Importing cause issues with coverage,
        (modules can be removed from sys.modules to prevent this)
    Importing __init__.py triggers importing rest and then requests too

    Inspired from pep8 setup.py
    """
    with open('iotlabaggregator/__init__.py') as init_f:
        for line in init_f:
            if line.startswith('__version__'):
                return eval(line.split('=')[-1])  # pylint:disable=eval-used

SCRIPTS = ['serial_aggregator', 'sniffer_aggregator']
DL_URL = 'http://github.com/iot-lab/iot-lab/tools_and_scripts/aggregator/'
SETUP_DEPS = [
    'setuptools-pep8', 'setuptools-lint', 'nose', 'nosexcover', 'mock'
]
if (2, 6) == sys.version_info[0:2]:
    SETUP_DEPS.append('pylint<1.4.0')
    SETUP_DEPS.append('astroid<1.3.0')


setup(
    name='iotlabaggregator',
    version='1.0.0',
    description='IoT-LAB testbed node connection command-line tools',
    author='IoT-LAB Team',
    author_email='admin@iot-lab.info',
    url='http://www.iot-lab.info',
    download_url=DL_URL,
    packages=find_packages(),
    scripts=SCRIPTS,
    classifiers=['Development Status :: 3 - Alpha',
                 'Programming Language :: Python',
                 'Intended Audience :: End Users/Desktop',
                 'Environment :: Console',
                 'Topic :: Utilities', ],
    install_requires=['iotlabcli>=1.4.0'],
)
