#!/usr/bin/env python3 -u
# copyright: predict-ably, BSD-3-Clause License (see LICENSE file)
"""Tests for predictably exceptions.

tests in this module:

    test_exceptions_raise_error - Test that skbase exceptions raise expected error.
"""
from typing import List

import pytest

from predictably._exceptions import ForwardRefError

__author__: List[str] = ["RNKuhns"]

ALL_EXCEPTIONS = (ForwardRefError,)


@pytest.mark.parametrize("predictably_exception", ALL_EXCEPTIONS)
def test_exceptions_raise_error(predictably_exception):
    """Test that predictably exceptions raise an error as expected."""
    with pytest.raises(predictably_exception):
        raise predictably_exception()

    msg = "Some message."
    with pytest.raises(predictably_exception, match=msg):
        raise predictably_exception(msg)
