#!/usr/bin/env python3 -u
# copyright: predict-ably, BSD-3-Clause License (see LICENSE file)
"""The external dataframe and array types supported by `predictably`'s.

Should be used for typing throughout `predictably`.
"""
from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any, Literal, NoReturn, Union, get_args, overload

if TYPE_CHECKING:
    import numpy as np
    import pandas as pd
    import xarray as xa

if sys.version_info < (3, 10):
    from typing_extensions import TypeAlias
else:
    from typing import TypeAlias

import polars as pl

from predictably.utils._iter import _format_seq_to_str

SupportedDataFrames: TypeAlias = Union[pl.DataFrame, pl.LazyFrame, "pd.DataFrame"]
SupportedArrays: TypeAlias = Union["np.ndarray", "xa.DataArray"]
# Not using Union[SupportedDataFrames, SupportedArrays] because mypy is having an
# issue with overload definitions later on
SupportedDataTypes: TypeAlias = Union[
    pl.DataFrame, pl.LazyFrame, "pd.DataFrame", "np.ndarray", "xa.DataArray"
]

supported_dfs = get_args(SupportedDataFrames)
supported_arrays = get_args(SupportedArrays)
supported_data_types = get_args(SupportedDataTypes)

_supported_external_types: dict[str, tuple[Any, ...]] = {
    "dataframe": supported_dfs,
    "array": supported_arrays,
    "any": supported_data_types,
}


def _supported_type_msg(
    type_: Literal["dataframe", "array", "any"] = "dataframe"
) -> str:
    """Create message about the types of dataframes that `predictably` supports.

    Used to raise standard error messages.

    Parameters
    ----------
    type_ : {"dataframe", "array", "any"}, default="dataframe"
        When generating the message about supported types, indicates whether
        it should be referring to supported "dataframe" or "array" types or either
        of them ('any').

    Returns
    -------
    str
        Message about supported types.
    """
    if type_ == "dataframe":
        type_str = f"{type_}s"
    elif type_ == "array":
        type_str = f"{type_}s"
    elif type_ == "any":
        type_str = "dataframes and arrays"
    else:
        raise ValueError("`type_` should be 'dataframe', 'array', or 'any'.")
    supported = _supported_external_types.get(type_)
    supported_text = _format_seq_to_str(supported, last_sep="or", remove_type_text=True)
    msg = f"`predictably only supports {type_str} of type {supported_text}."
    return msg


def raise_not_supported_external_type(
    type_: Literal["dataframe", "array", "any"] = "dataframe"
) -> NoReturn:
    """Raise an error if the input data container is not supported by `predictably`.

    Used to raise standard error messages.

    Parameters
    ----------
    type_ : {"dataframe", "array", "any"}, default="dataframe"
        When generating the error message about supported types, indicates whether
        it should be referring to supported "dataframe" or "array" types or either
        of them ('any').

    Returns
    -------
    str
        Message about supported types.
    """
    raise TypeError(_supported_type_msg(type_=type_))


@overload
def check_supported_external_type(
    data: SupportedDataFrames, type_: Literal["dataframe", "any"]
) -> SupportedDataFrames:  # numpydoc ignore=GL08
    ...  # pragma: no cover


@overload
def check_supported_external_type(
    data: SupportedArrays, type_: Literal["array", "any"]
) -> SupportedArrays:  # numpydoc ignore=GL08
    ...  # pragma: no cover


def check_supported_external_type(
    data: Any, type_: Literal["dataframe", "array", "any"] = "dataframe"
) -> SupportedDataTypes:
    """Validate that the `data` is one of predictably's supported external data types.

    Input `data` is returned unchanged if it is a supported external data type.

    Parameters
    ----------
    data : Any
        The input data to check.
    type_ : {"dataframe", "array", "any"}, default="dataframe"
        Indicates the supported external data types to check against.

    Returns
    -------
    pl.LazyFrame | pl.DataFrame | pd.DataFrame | np.ndarray | xa.DataArray
        The input data if it is a supported type.

    Raises
    ------
    TypeError
        If `data` is not one of the external types supported by `predictably`.
    """
    supported = _supported_external_types.get(type_)
    if supported is None:
        raise ValueError("`type_` should be 'dataframe', 'array', or 'any'.")

    if not isinstance(data, supported):
        raise_not_supported_external_type(type_=type_)
    return data
