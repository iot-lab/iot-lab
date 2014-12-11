#! /usr/bin/env python
# -*- coding:utf-8 -*-
__version__ = '1.0.0'

import sys
import logging


# Use loggers for all outputs to have the same config
LOG_FMT = logging.Formatter("%(created)f;%(message)s")

# error logger
LOGGER = logging.getLogger('iotlabaggregator')
_LOGGER = logging.StreamHandler(sys.stderr)
_LOGGER.setFormatter(LOG_FMT)
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(_LOGGER)
