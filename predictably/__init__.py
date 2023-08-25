#!/usr/bin/env python3 -u
# copyright: predict-ably, BSD-3-Clause License (see LICENSE file)
""":mod:`predictably` provides a unified time series forecasting interface.

Predictable, well-documented interfaces so you can predict *ably*.
"""
from typing import List

from predictably._config import (
    config_context,
    get_config,
    get_default_config,
    reset_config,
    set_config,
)

__version__: str = "0.2.0"

__author__: List[str] = ["RNKuhns"]
__all__: List[str] = [
    "get_default_config",
    "get_config",
    "set_config",
    "reset_config",
    "config_context",
]
