#!/usr/bin/env python3 -u
# copyright: predict-ably, BSD-3-Clause License (see LICENSE file)
"""The external dataframe and array types supported by `predictably`'s.

Should be used for typing throughout `predictably`.
"""
from __future__ import annotations

import sys
import warnings
from importlib import import_module
from importlib.util import find_spec
from typing import (
    TYPE_CHECKING,
    Any,
    ForwardRef,
    Literal,
    NoReturn,
    Union,
    get_args,
    overload,
)

if TYPE_CHECKING:
    import numpy as np  # pragma: no cover
    import pandas as pd  # pragma: no cover
    import pyarrow as pa  # pragma: no cover
    import xarray as xa  # pragma: no cover

if sys.version_info < (3, 10):
    from typing_extensions import TypeAlias
else:
    from typing import TypeAlias

import polars as pl

from predictably._core._exceptions import ForwardRefError
from predictably.utils._iter import _format_seq_to_str, _remove_type_text

SupportedDataFrames: TypeAlias = Union[
    pl.DataFrame, pl.LazyFrame, "pd.DataFrame", "pa.Table"
]
SupportedArrays: TypeAlias = Union["np.ndarray", "xa.DataArray"]
# Not using Union[SupportedDataFrames, SupportedArrays] because mypy is having an
# issue with overload definitions later on
SupportedDataTypes: TypeAlias = Union[
    pl.DataFrame, pl.LazyFrame, "pd.DataFrame", "pa.Table", "np.ndarray", "xa.DataArray"
]

supported_dfs = get_args(SupportedDataFrames)
supported_arrays = get_args(SupportedArrays)
supported_data_types = get_args(SupportedDataTypes)

_supported_external_types: dict[str, tuple[Any, ...]] = {
    "dataframe": supported_dfs,
    "array": supported_arrays,
    "any": supported_data_types,
}

dependency_abbrev_map: dict[str, str] = {
    "np": "numpy",
    "pa": "pyarrow",
    "pd": "pandas",
    "pl": "polars",
    "xa": "xarray",
}
dependency_name_map: dict[str, str] = {v: k for k, v in dependency_abbrev_map.items()}


def _get_forward_ref_module_name(fref: str, return_abbrev: bool = False) -> str:
    """Get the module name of a forward ref alias.

    This is useful for ensuring you've got the name of a module and not the alias
    of a module. For example, ensuring that "pd" and "pandas" both return "pandas".

    Parameters
    ----------
    fref : str
        The forward ref that needs to have the module name returned.
    return_abbrev : bool, default=False
        Whether to return the module's abbreviation instead of its name.

    Returns
    -------
    str
        The name or abbreviation of the module for the forward reference.
    """
    msg = f"Error deriving name of forward ref for unsupported depenedency {fref}."
    if return_abbrev:
        if fref in dependency_abbrev_map:
            value_ = fref
        elif fref in dependency_name_map:
            value_ = dependency_name_map[fref]
        else:
            raise ForwardRefError(msg)
    else:
        if fref in dependency_name_map:
            value_ = fref
        elif fref in dependency_abbrev_map:
            value_ = dependency_abbrev_map[fref]
        else:
            raise ForwardRefError(msg)
    return value_


def _evaluate_available_forward_refs(
    supported: tuple[str | type, ...]
) -> tuple[tuple[type, ...], tuple[str, ...]]:
    """Load and evaluate available forward references.

    This will determine if forward references are available as already imported
    modules or available for import. If a forward reference is available it is
    evaluated.

    Parameters
    ----------
    supported : tuple[str | type]
        String versions of forward references for supported data types.

    Returns
    -------
    tuple[tuple[type], tuple[str]]
        The supported type forward references that are available after evaluation and
        a tuple of the string names of forward references that weren't available.
    """
    supported_types = []
    unavailable_supported_types = []
    for s in supported:
        if isinstance(s, type):
            supported_types.append(s)
        # For forward refs, we can check and see if forward ref is importable
        elif isinstance(s, ForwardRef):
            forward_ref_text = _remove_type_text(s)
            split_forward_ref_text = forward_ref_text.split(".")
            mod_ref = split_forward_ref_text[0]
            mod_abbrev = _get_forward_ref_module_name(mod_ref, return_abbrev=True)
            mod_name = _get_forward_ref_module_name(mod_ref)
            mod_spec = find_spec(mod_name)
            if not (mod_spec is None or mod_spec.loader is None):
                forward_ref_text_switch_alias = split_forward_ref_text.copy()
                if mod_ref == mod_abbrev:
                    forward_ref_text_switch_alias[0] = mod_name
                mod_ = import_module(mod_name)
                supported_types.append(
                    getattr(mod_, ".".join(split_forward_ref_text[1:]))
                )
            else:
                unavailable_supported_types.append(forward_ref_text)
        else:
            unavailable_supported_types.append(_remove_type_text(s))
    return tuple(supported_types), tuple(unavailable_supported_types)


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
    if type_ in ("array", "dataframe"):
        type_str = f"{type_}s"
    # elif type_ == "array":
    #     type_str = f"{type_}s"
    elif type_ == "any":
        type_str = "dataframes and arrays"
    else:
        raise ValueError("`type_` should be 'dataframe', 'array', or 'any'.")
    supported = _supported_external_types.get(type_)
    supported_text = _format_seq_to_str(supported, last_sep="or", remove_type_text=True)
    msg = f"`predictably` only supports {type_str} of type {supported_text}."
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
    data: SupportedDataFrames, type_: Literal["dataframe"]
) -> SupportedDataFrames:  # numpydoc ignore=GL08
    ...  # pragma: no cover


@overload
def check_supported_external_type(
    data: SupportedDataTypes, type_: Literal["any"]
) -> SupportedDataTypes:  # numpydoc ignore=GL08
    ...  # pragma: no cover


@overload
def check_supported_external_type(
    data: SupportedArrays, type_: Literal["array"]
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
    supported_, unavailable_supported_ = _evaluate_available_forward_refs(supported)
    if len(unavailable_supported_) > 0:
        if len(unavailable_supported_) == 1:
            dep_text = "dependency"
        else:
            dep_text = "dependencies"
        unavailable_text = _format_seq_to_str(
            unavailable_supported_, last_sep="and", remove_type_text=True
        )
        msg = f"`predictably` optional {dep_text} {unavailable_text} are not available"
        msg += " for import. To use their functionality they should be installed."
        warnings.warn(msg, stacklevel=2)
    if not isinstance(data, supported_):
        raise_not_supported_external_type(type_=type_)
    return data
