#!/usr/bin/env python3 -u
# copyright: predict-ably BSD-3-Clause License (see LICENSE file)
"""Tests of predictably package's data types.

Tests for all data type functionality are included here.
"""
import re
from typing import List

import polars as pl
import pytest
import xarray as xa

__all__: List[str] = []
__author__: List[str] = ["RNKuhns"]

from predictably._core._exceptions import ForwardRefError
from predictably.data.types._base import BasePredictablyDataType, Metadata
from predictably.data.types._types import (
    _evaluate_available_forward_refs,
    _get_forward_ref_module_name,
    _supported_type_msg,
    check_supported_external_type,
    dependency_abbrev_map,
    dependency_name_map,
    raise_not_supported_external_type,
    supported_arrays,
    supported_data_types,
    supported_dfs,
)
from predictably.utils._iter import _remove_type_text
from predictably.validate import is_sequence

_metadata_post_init_fields = ["cross_section_dim_", "time_dim_", "data_fields_"]
_base_predictably_data_type_post_init_fields = ["lazyframe"]
_base_predictably_data_type_not_implemented_methods = (
    "_generate_metadata",
    "_array_to_dataframe",
    "to_dataframe",
    "to_array",
)
_supported_msg_tester = {
    "any": supported_data_types,
    "dataframe": supported_dfs,
    "array": supported_arrays,
}


@pytest.fixture
def metadata_post_init_fields():
    """Test fixture for Metadata post init fields.

    Used since lists are mutable and we don't want side effects across tests.
    """
    return _metadata_post_init_fields


@pytest.fixture
def base_data_type_post_init_fields():
    """Test fixture for BasePredictablyDataType post init fields.

    Used since lists are mutable and we don't want side effects across tests.
    """
    return _base_predictably_data_type_post_init_fields


@pytest.fixture
def test_dataframe():
    """Test fixture for dataframe to test BasePredictablyDataType.

    Used since dataframes can be updated and we don't want side effects across tests.
    """
    return pl.from_dict(
        {
            "Column1": [1, 2, 3, 4, 5],
            "Column2": [6, 7, 8, 9, 10],
            "Column3": [11, 12, 13, 14, 15],
        }
    )


@pytest.mark.parametrize("supported_types", [*_supported_msg_tester.keys()])
def test_supported_type_msg(supported_types):
    """Verify that _supported_type_msg produces expected message.

    Used to make sure that generated message includes supported dataframes.
    """
    msg = _supported_type_msg(supported_types)
    match_ = re.match(r"^`predictably` only supports.*", msg)
    matched_group = match_.group()
    matched_start_okay = isinstance(matched_group, str)
    all_types_in_msg = all(
        _remove_type_text(a) in matched_group
        for a in _supported_msg_tester[supported_types]
    )
    assert (
        matched_start_okay and all_types_in_msg
    ), "Supported type message not correct."


def test_supported_type_msg_raises_incorrect_input():
    """Verify that _supported_type_msg produces expected message.

    Used to make sure that generated message includes supported dataframes.
    """
    with pytest.raises(
        ValueError, match="`type_` should be 'dataframe', 'array', or 'any'."
    ):
        _ = _supported_type_msg(type_="zz")


@pytest.mark.parametrize("supported_types", [*_supported_msg_tester.keys()])
def test_raise_not_supported_external_type_raies_type_error(supported_types):
    """Verify that raise_not_supported_external_type raises a type error.

    Also verifies the error message.
    """
    with pytest.raises(TypeError, match=r"^`predictably` only supports.*"):
        raise_not_supported_external_type(type_=supported_types)


@pytest.mark.parametrize("return_abbrev", (True, False))
def test_get_forward_ref_module_name(return_abbrev):
    """Test that the _get_forward_ref_module_name function works as expected.

    Verify that the correct name or abbreviation are returned.
    """
    msg = "_get_forward_ref_module_name not mapping between names and aliases."
    for abbrev_ in dependency_abbrev_map:
        output_ = _get_forward_ref_module_name(abbrev_, return_abbrev=return_abbrev)
        if return_abbrev:
            assert output_ == abbrev_, msg
        else:
            assert output_ == dependency_abbrev_map[abbrev_], msg
    for name_ in dependency_name_map:
        output_ = _get_forward_ref_module_name(name_, return_abbrev=return_abbrev)
        if return_abbrev:
            assert output_ == dependency_name_map[name_], msg
        else:
            assert output_ == name_, msg

    # Verify an error is raised when trying to evaluate forward Ref of unavailable
    # module
    with pytest.raises(ForwardRefError):
        _get_forward_ref_module_name("zz", return_abbrev=return_abbrev)


def test_evaluate_available_forward_refs_modules():
    """Test _evaluate_available_forward_refs able to evaluate forward ref dependencies.

    This is to verify that all the known optional dependencies can have their
    forward refs evaluated when the module is not yet imported.
    """
    msg = "The forward ref annotations of known dependencies could not be evaluated."
    evaluated, unsupported = _evaluate_available_forward_refs(supported_data_types)
    assert len(evaluated) == len(supported_data_types) and len(unsupported) == 0, msg


def test_evaluate_available_forward_refs_modules_unavailable_input():
    """Test _evaluate_available_forward_refs with unavailable forward refs.

    This is to verify that unavailable inputs are captured in second output tuple
    of _evaluate_available_forward_refs.
    """
    msg = "The forward ref annotations of known dependencies could not be evaluated."
    _, unsupported = _evaluate_available_forward_refs("ForwardRef('Something')")
    assert len(unsupported) > 0, msg


def test_check_supported_external_type_works_with_valid_input(test_dataframe):
    """Verify that the validation of supported external data types works correctly.

    Used to make sure the supported external data types pass the validation
    as expected.
    """
    # See if supported dataframes pass check
    for type_ in ("dataframe", "any"):
        check_supported_external_type(test_dataframe, type_=type_)
        check_supported_external_type(test_dataframe.to_pandas(), type_=type_)
        check_supported_external_type(test_dataframe.to_arrow(), type_=type_)

    # See if supported arrays pass check
    for type_ in ("array", "any"):
        check_supported_external_type(test_dataframe.to_numpy(), type_=type_)
        check_supported_external_type(
            xa.DataArray(test_dataframe.to_numpy()), type_=type_
        )

    # Verify that typerror is raised for unsupported external data types
    with pytest.raises(TypeError, match="^`predictably` only supports.*"):
        check_supported_external_type(test_dataframe.to_numpy(), type_="dataframe")


def test_check_supported_external_type_raises_invalid_type(test_dataframe):
    """Verify check_supported_external_type raises when type_ is invalid.

    Used to verify error handling works as expected.
    """
    with pytest.raises(
        ValueError, match="`type_` should be 'dataframe', 'array', or 'any'."
    ):
        check_supported_external_type(test_dataframe, type_="zz")


@pytest.mark.parametrize("field_names", (None, [f"Field_{idx}" for idx in range(3)]))
def test_metadata_post_init_executes(metadata_post_init_fields, field_names):
    """Test metadata class post initialization executes.

    This is to verify that use of attrs ability to have code run post initialization
    is working correctly.
    """
    meta = Metadata(field_names=field_names)
    msg = "Post init attributes are not set correctly"
    assert all(hasattr(meta, a) for a in metadata_post_init_fields), msg

    unexpected_return_types = [
        a
        for a in metadata_post_init_fields
        if not is_sequence(getattr(meta, a), sequence_type=list, element_type=str)
    ]
    assert len(unexpected_return_types) == 0, msg


def test_metadata_post_init_set_param_values_match_expected():
    """Test metadata class post initialization sets expected values on attributes.

    This goes a step farther to verify that given a set of input we get the
    expected values set on the attributes set post init (cross_section_dim_,
    time_dim_, data_fields_).
    """
    # First check cases where cross_section_dim and time_dim are in field_names
    # if provided
    # field_names, but no cross_section_dim, time_dim
    field_names = ["Cross_Section_Id", "Timestamp", "Column 1", "Column 2"]
    meta = Metadata(field_names=field_names)
    assert meta.time_dim_ == []
    assert meta.cross_section_dim_ == []
    assert meta.data_fields_ == field_names
    # field_names and cross_section_dim
    meta = Metadata(field_names=field_names, cross_section_dim="Cross_Section_Id")
    assert meta.time_dim_ == []
    assert meta.cross_section_dim_ == ["Cross_Section_Id"]
    assert meta.data_fields_ == [f for f in field_names if f != "Cross_Section_Id"]
    # field_names and time_dim
    meta = Metadata(field_names=field_names, time_dim="Timestamp")
    assert meta.time_dim_ == ["Timestamp"]
    assert meta.cross_section_dim_ == []
    assert meta.data_fields_ == [f for f in field_names if f != "Timestamp"]
    # field_names and both cross_section_dim and time_dim
    meta = Metadata(
        field_names=field_names,
        cross_section_dim="Cross_Section_Id",
        time_dim="Timestamp",
    )
    assert meta.time_dim_ == ["Timestamp"]
    assert meta.cross_section_dim_ == ["Cross_Section_Id"]
    assert meta.data_fields_ == [
        f for f in field_names if f not in ("Cross_Section_Id", "Timestamp")
    ]
    # Verify it works when cross_section_dim is a sequence
    meta = Metadata(
        field_names=field_names,
        cross_section_dim=("Cross_Section_Id", "Column 1"),
        time_dim="Timestamp",
    )
    assert meta.time_dim_ == ["Timestamp"]
    assert meta.cross_section_dim_ == ["Cross_Section_Id", "Column 1"]
    assert meta.data_fields_ == [
        f for f in field_names if f not in ("Cross_Section_Id", "Column 1", "Timestamp")
    ]
    # Check things work when field_names don't include cross_section_dim and time_dim
    meta = Metadata(
        field_names=field_names[-1],
        cross_section_dim=("Cross_Section_Id",),
        time_dim="Timestamp",
    )
    assert meta.time_dim_ == ["Timestamp"]
    assert meta.cross_section_dim_ == ["Cross_Section_Id"]
    assert meta.data_fields_ == [field_names[-1]]


@pytest.mark.parametrize(
    "field_names", (None, "some Column", [f"Field_{idx}" for idx in range(3)])
)
@pytest.mark.parametrize(
    "cross_section_dim", (None, "some Column", [f"Field_{idx}" for idx in range(3)])
)
@pytest.mark.parametrize("time_dim", (None, "some Column"))
@pytest.mark.parametrize("additional_metadata", (None, {"Some Metadata": 7}))
def test_metadata_attrs_validation_okay_inputs(
    field_names, cross_section_dim, time_dim, additional_metadata
):
    """Test that attrs validation doesn't raise errors when input is okay.

    Used to make sure we aren't falsely flagging okay input as invalid.
    """
    try:
        Metadata(
            field_names=field_names,
            cross_section_dim=cross_section_dim,
            time_dim=time_dim,
            additional_metadata=additional_metadata,
        )
    except ValueError as e:  # pragma: no cover
        msg = f"Unexpected parameter validation exception: {e}"  # pragma: no cover
        pytest.fail(msg)  # pragma: no cover


def test_metadata_attrs_validation_raises():
    """Test that attrs validation raises error for invalid input.

    Used to make sure invalid input correctly gets flagged as invalid.
    """
    # Check different types of invalid input raise errors for
    # `field_names`, `cross_section_dim`, `time_dim`, and `additional_metadata`
    for invalid_input in (7, 11.0, range(7), (e for e in range(7))):
        with pytest.raises(ValueError, match="^`field_names` should be sequence"):
            Metadata(field_names=invalid_input)
        with pytest.raises(ValueError, match="^`cross_section_dim` should be sequence"):
            Metadata(cross_section_dim=invalid_input)
        with pytest.raises(ValueError, match="^`time_dim` should be a string"):
            Metadata(time_dim=invalid_input)
        with pytest.raises(ValueError, match="^`additional_metadata` should be a"):
            Metadata(additional_metadata=invalid_input)

    # Check sequence of strings raises for `time_dim`
    str_seq = ["Some String", "Another String"]
    with pytest.raises(ValueError, match="^`time_dim` should be a string"):
        Metadata(time_dim=str_seq)
    with pytest.raises(ValueError, match="^`time_dim` should be a string"):
        Metadata(time_dim=tuple(str_seq))

    # Check dictionaries with non-string keys raise error for `additional_metadata`
    with pytest.raises(ValueError, match="^`additional_metadata` should be a dict"):
        Metadata(additional_metadata={1: "something", 2: 3, 3: 55.0})


def test_base_data_type_post_init_executes(
    base_data_type_post_init_fields, test_dataframe
):
    """Test metadata class post initialization executes.

    This is to verify that use of attrs ability to have code run post initialization
    is working correctly.
    """
    meta = Metadata(field_names=test_dataframe.columns)

    base = BasePredictablyDataType(dataframe=test_dataframe, metadata=meta)
    # Verify that all attributes set in post init exist
    msg = "Post init attributes are not set correctly"
    assert all(hasattr(base, a) for a in base_data_type_post_init_fields), msg
    assert isinstance(base.lazyframe, pl.LazyFrame), msg

    # Verify with polars LazyFrame
    base = BasePredictablyDataType(dataframe=test_dataframe.lazy(), metadata=meta)
    # Verify that all attributes set in post init exist
    msg = "Post init attributes are not set correctly"
    assert all(hasattr(base, a) for a in base_data_type_post_init_fields), msg
    assert isinstance(base.lazyframe, pl.LazyFrame), msg

    # Verify with pandas dataframe
    base = BasePredictablyDataType(dataframe=test_dataframe.to_pandas(), metadata=meta)
    # Verify that all attributes set in post init exist
    msg = "Post init attributes are not set correctly"
    assert all(hasattr(base, a) for a in base_data_type_post_init_fields), msg
    assert isinstance(base.lazyframe, pl.LazyFrame), msg

    # Verify with pyarrow table (has __dataframe__)
    base = BasePredictablyDataType(dataframe=test_dataframe.to_arrow(), metadata=meta)
    # Verify that all attributes set in post init exist
    msg = "Post init attributes are not set correctly"
    assert all(hasattr(base, a) for a in base_data_type_post_init_fields), msg
    assert isinstance(base.lazyframe, pl.LazyFrame), msg


def test_base_data_type_to_lazyframe_raises_for_unsupported_type(test_dataframe):
    """Verify _to_lazyframe raises an error for unsupported dataframe type.

    Attrs validation of parameter arguments won't allow unsupported dataframe
    to be pass at instance construction. So we test error handling of unsupported
    type in _to_lazyframe here in case we use it outside of post-init context
    later.
    """
    # Verify passing numpy as dataframe raises an error (use from_array instead)
    meta = Metadata(field_names=test_dataframe.columns)
    base = BasePredictablyDataType(dataframe=test_dataframe, metadata=meta)
    with pytest.raises(TypeError, match="^`predictably` only"):
        base._to_lazyframe(test_dataframe.to_numpy())


def test_base_data_type_not_implemented_methods_raise(test_dataframe):
    """Verify that methods that aren't implemented on the base class raise an error.

    Verifies they are part of the interface, but raise not implemented error.
    """
    meta = Metadata(field_names=test_dataframe.columns)
    base = BasePredictablyDataType(dataframe=test_dataframe, metadata=meta)
    with pytest.raises(NotImplementedError):
        base._generate_metadata(test_dataframe, metadata=meta)

    with pytest.raises(NotImplementedError):
        base._array_to_dataframe(test_dataframe, meta)
    with pytest.raises(NotImplementedError):
        base.to_dataframe()
    with pytest.raises(NotImplementedError):
        base.to_array()
    with pytest.raises(NotImplementedError):
        base.from_dataframe(test_dataframe, metadata=meta)
    with pytest.raises(NotImplementedError):
        base.from_array(test_dataframe.to_numpy(), metadata=meta)
