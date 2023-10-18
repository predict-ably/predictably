#!/usr/bin/env python3 -u
# copyright: predict-ably, BSD-3-Clause License (see LICENSE file)
# Elements of predictably.utils reuse code developed for skbase. These elements
# are copyrighted by the skbase developers, BSD-3-Clause License. For
# conditions see https://github.com/sktime/skbase/blob/main/LICENSE
"""Tests of the functionality for working with iterables.

tests in this module incdlue:

- test_remove_single: verify that _remove_single works as expected.
- test_format_seq_to_str: verify that _format_seq_to_str outputs expected format.
- test_format_seq_to_str_raises: verify _format_seq_to_str raises error on unexpected
  output.
- test_scalar_to_seq_expected_output: verify that _scalar_to_seq returns expected
  output.
- test_scalar_to_seq_raises: verify that _scalar_to_seq raises error when an
  invalid value is provided for sequence_type parameter.
"""
from collections.abc import Sequence

import pytest

from predictably.utils._iter import (
    _format_seq_to_str,
    _remove_single,
    _remove_type_text,
    _scalar_to_seq,
)

__author__ = ["RNKuhns"]


class SomeClass:
    """This is a test class."""

    def __init__(self, a: int = 7) -> None:
        self.a = a


def test_remove_type_text() -> None:
    """Test _remove_type_text removes <class ... > text as expected."""
    msg = "Not removing type text from type"
    assert _remove_type_text(int) == "int", msg
    assert _remove_type_text(Sequence) == "collections.abc.Sequence", msg
    msg = "Not removing type text from str"
    assert _remove_type_text("<class 'int'>") == "int", msg
    msg = "Not leaving strings without <class ...> text unchanged."
    assert _remove_type_text("int") == "int", msg
    assert _remove_type_text("<type 'int'>") == "<type 'int'>", msg
    msg = "Not removing ForwardRef"
    assert _remove_type_text("ForwardRef('pd.DataFrame')") == "pd.DataFrame", msg


def test_remove_single() -> None:
    """Test _remove_single output is as expected."""
    # Verify that length > 1 sequence not impacted.
    assert _remove_single([1, 2, 3]) == [1, 2, 3]

    # Verify single member of sequence is removed as expected
    assert _remove_single([1]) == 1


def test_format_seq_to_str() -> None:
    """Test _format_seq_to_str returns expected output."""
    # Test basic functionality (including ability to handle str and non-str)
    seq = [1, 2, "3", 4]
    assert _format_seq_to_str(seq) == "1, 2, 3, 4"

    # Test use of last_sep
    assert _format_seq_to_str(seq, last_sep="and") == "1, 2, 3 and 4"
    assert _format_seq_to_str(seq, last_sep="or") == "1, 2, 3 or 4"

    # Test use of different sep argument
    assert _format_seq_to_str(seq, sep=";") == "1;2;3;4"

    # Test using remove_type_text keyword
    assert (
        _format_seq_to_str([list, tuple], remove_type_text=False)
        == "<class 'list'>, <class 'tuple'>"
    )
    assert _format_seq_to_str([list, tuple], remove_type_text=True) == "list, tuple"
    assert (
        _format_seq_to_str([list, tuple], last_sep="and", remove_type_text=True)
        == "list and tuple"
    )

    assert _format_seq_to_str(int) == "<class 'int'>"
    assert _format_seq_to_str(int, remove_type_text=True) == "int"

    # Test with scalar inputs
    assert _format_seq_to_str(7) == "7"  # int, float, bool primitives cast to str
    assert _format_seq_to_str("some_str") == "some_str"
    # Verify that keywords don't affect output
    assert _format_seq_to_str(7, sep=";") == "7"
    assert _format_seq_to_str(7, last_sep="or") == "7"


def test_format_seq_to_str_raises() -> None:
    """Test _format_seq_to_str raises error when input is unexpected type."""
    with pytest.raises(
        TypeError, match="`seq` must be a sequence or scalar str, int, float, bool.*"
    ):
        _format_seq_to_str(c for c in [1, 2, 3])


def test_scalar_to_seq_expected_output() -> None:
    """Test _scalar_to_seq returns expected output."""
    assert _scalar_to_seq(7) == (7,)
    # Verify it works with scalar classes and objects
    assert _scalar_to_seq(int) == (int,)
    assert _scalar_to_seq(SomeClass) == (SomeClass,)
    # Verify things work with class instance
    some_class = SomeClass()
    assert _scalar_to_seq(some_class) == (some_class,)
    # Verify strings treated like scalar not sequence
    assert _scalar_to_seq("some_str") == ("some_str",)
    assert _scalar_to_seq("some_str", sequence_type=list) == ["some_str"]

    # Verify sequences returned unchanged
    assert _scalar_to_seq((1, 2)) == (1, 2)


def test_scalar_to_seq_raises() -> None:
    """Test scalar_to_seq raises error when `sequence_type` is unexpected type."""
    with pytest.raises(
        ValueError,
        match="`sequence_type` must be a subclass of collections.abc.Sequence.",
    ):
        _scalar_to_seq(7, sequence_type=int)

    with pytest.raises(
        ValueError,
        match="`sequence_type` must be a subclass of collections.abc.Sequence.",
    ):
        _scalar_to_seq(7, sequence_type=dict)
