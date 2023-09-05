#!/usr/bin/env python3 -u
# copyright: predict-ably, BSD-3-Clause License (see LICENSE file)
"""Utility function to create `predictably`'s core data types from external data.

Users should use :func:`predictably.from_external_data` or call the `from_array`
or `from_dataframe` on the applicable `predictably` data type.
"""
from typing import List, TypeAlias, Union

from predictably.data.types._base import Metadata
from predictably.data.types._cross_section import CrossSection
from predictably.data.types._panel import Panel
from predictably.data.types._timeseries import Timeseries
from predictably.data.types._types import (
    SupportedDataTypes,
    raise_not_supported_external_type,
    supported_arrays,
    supported_dfs,
)

PredictablyDataType: TypeAlias = Union[CrossSection, Timeseries, Panel]

__author__: List[str] = ["RNKuhns"]
__all__: List[str] = ["from_external_data"]


def from_external_data(
    data: SupportedDataTypes, metadata: Metadata | None = None
) -> PredictablyDataType:
    """Convert your dataset to a `predictably` data type.

    - Data that has no time dimension is represented as a :class:`CrossSection`,
      the `predictably` data type for a cross-section of observations (instances).
    - Data with a time dimension, but no cross-sectional dimension is represented
      as a :class:`TimeSeries`, the `predictably` data type for univariate and
      multivariate timeseries.
    - Data with both a time dimension and cross-sectional dimension is represented
      as a :class:`Panel`, the `predictably` data type when cross-sectional
      observations (instances) are observed over time

    Parameters
    ----------
    data : pl.LazyFrame | pl.DataFrame | pd.DataFrame | np.ndarray | xa.DataArray
        The input data you want to convert to a `predictably` data type.
    metadata : Metadata, default=None
        Optional metadata about your dataset.

    Returns
    -------
    CrossSection | Timeseries | Panel
        Your data represented as the applicable `predictably` data type.

    Raises
    ------
    TypeError
        If `data` is not one of the exteranl data containers (e.g., arrays
        and dataframes) supported by `predictably`.

    See Also
    --------
    CrossSection.from_dataframe : Create a :class:`CrossSection` from a dataframe.
    CrossSection.from_array : Create a :class:`CrossSection` from an array.
    Timeseries.from_dataframe : Create a :class:`Timeseries` from a dataframe.
    Timeseries.from_array : Create a :class:`Timeseries` from an array.
    Panel.from_dataframe : Create a :class:`Panel` from a dataframe.
    Panel.from_array : Create a :class:`Panel` from an array.
    """
    if isinstance(data, supported_arrays):
        input_type_ = "array"
    elif isinstance(data, supported_dfs):
        input_type_ = "dataframe"
    else:
        raise_not_supported_external_type()

    # Discover metadata
    if metadata is None:
        metadata_ = Metadata()
    else:
        metadata_ = metadata
    has_cross_section_dim = len(metadata_.cross_section_dim_) > 0
    has_time_dim = len(metadata_.time_dim_) > 0

    out_data: PredictablyDataType
    if has_time_dim:
        # Panel data with cross-sectional and time dimensions
        if has_cross_section_dim:
            if input_type_ == "dataframe":
                out_data = Panel.from_dataframe(data, metadata=metadata_)
            else:
                out_data = Panel.from_array(data, metadata=metadata_)
        # Otherwise we have a standard timeseries
        else:
            if input_type_ == "dataframe":
                out_data = Timeseries.from_dataframe(data, metadata=metadata_)
            else:
                out_data = Timeseries.from_array(data, metadata=metadata_)
    else:
        # Even if we don't have an explicit cross-section dimension, we'll
        # treat the dataset as a cross-section if there is no time dimension
        # At this point we would have raised an error for unsupported data input
        # so we are dealing with a supported dataframe or array
        if input_type_ == "dataframe":
            out_data = CrossSection.from_dataframe(data, metadata=metadata_)
        else:
            out_data = CrossSection.from_array(data, metadata=metadata_)

    return out_data
