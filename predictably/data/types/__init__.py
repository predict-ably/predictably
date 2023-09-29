#!/usr/bin/env python3 -u
# copyright: predict-ably, BSD-3-Clause License (see LICENSE file)
""":mod:`predictably.data.types` provides `predictably`'s core data types.

Users can declare their data type through the ``from_external_data`` functional
interface or the `from_array` and `from_dataframe` interface on a particular
data type class.
"""
from typing import List

from predictably.data.types._base import Metadata
from predictably.data.types._cross_section import CrossSection
from predictably.data.types._from_external import from_external_data
from predictably.data.types._panel import Panel
from predictably.data.types._timeseries import Timeseries

__author__: List[str] = ["RNKuhns"]
__all__: List[str] = [
    "CrossSection",
    "Metadata",
    "Panel",
    "Timeseries",
    "from_external_data",
]
