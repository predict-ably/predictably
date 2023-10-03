#!/usr/bin/env python3 -u
# copyright: predictably developers, BSD-3-Clause License (see LICENSE file)
# Elements of predictably.validate reuse code developed for skbase. These elements
# are copyrighted by the skbase developers, BSD-3-Clause License. For
# conditions see https://github.com/sktime/skbase/blob/main/LICENSE
"""Tools for validating and comparing predictably objects and collections.

This module contains functions used throughout `predictably` to provide standard
validation of inputs to `predictably` methods and functions.
"""
from typing import List

from predictably.validate._named_objects import (
    check_sequence_named_objects,
    is_sequence_named_objects,
)
from predictably.validate._types import check_sequence, check_type, is_sequence

__author__: List[str] = ["RNKuhns"]
__all__: List[str] = [
    "check_sequence",
    "check_sequence_named_objects",
    "check_type",
    "is_sequence",
    "is_sequence_named_objects",
]
