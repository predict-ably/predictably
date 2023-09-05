#!/usr/bin/env python3 -u
# copyright: predict-ably, BSD-3-Clause License (see LICENSE file)
"""Base class `predictably`'s core data types.

All `predictably` data types should inherit from ``BasePredictablyDataType``.
"""
from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any, Literal, Sequence, overload

if TYPE_CHECKING:
    import numpy as np
    import pandas as pd
    import xarray as xa

if sys.version_info < (3, 11):
    from typing_extensions import Self
else:
    from typing import Self

import attrs
import polars as pl

from predictably._base import BaseObject
from predictably.data.types._types import (
    SupportedArrays,
    SupportedDataFrames,
    SupportedDataTypes,
    check_supported_external_type,
    raise_not_supported_external_type,
)

__author__: list[str] = ["RNKuhns"]
__all__: list[str] = [
    "BasePredictablyDataType",
    "Metadata",
    "SupportedArrays",
    "SupportedDataFrames",
]


@attrs.define(kw_only=True, slots=False)
class Metadata:  # numpydoc ignore=PR02
    """Define metadata for `predictably` data types.

    Used to provide predictably's data types information about your dataset.

    Parameters
    ----------
    field_names : sequence[str], default=None
        The name of all the fields in the input data. For a dataset that does
        not store field names (e.g., ``numpy.ndarray``) it should be a list of
        the applicable names.
    cross_section_dim : sequence[str], default=None
        The name of the cross-section dimension in the input data. This could be:

        - The name of the the column(s) that define cross-sectional instances,
        - The name of an array dimension that define the cross-sectional dimension, or
        - The name of the dataframe index level that defines the cross-sectional
          dimension.

    time_dim : str, default=None
        The name of the time dimension in the input data. This could be:

        - The name of the the column that defines the time dimension,
        - The name of an array dimension that defines the time dimension, or
        - The name of the dataframe index level that defines the time dimension.

    additional_metadata : dict[str, Any], default=None
        Mapping of additional metadata names to values.

    Attributes
    ----------
    cross_section_dim_ : list[str]
        The names of the data's cross-section dimension(s).
    time_dim_ : list[str]
        The name of the data's time-dimension.
    data_fields_ : list[str]
        The name of the data's fields that aren't cross-sectional or time dimensions.
    """

    field_names: Sequence[str] | None = None
    cross_section_dim: Sequence[str] | None = None
    time_dim: str | None = None
    additional_metadata: dict[str, Any] | None = None
    # These are the attrs.fields used to capture post-init attributes that
    # represent cleaned version of user param arguments
    cross_section_dim_: list[str] = attrs.field(init=False, repr=False, default=None)
    time_dim_: list[str] = attrs.field(init=False, repr=False, default=None)
    data_fields_: list[str] = attrs.field(init=False, repr=False, default=None)

    def __attrs_post_init___(self) -> None:
        """One-time post initialization variable augmentation.

        Used to determine the columns that are not cross-section or time-series IDs.
        """
        if self.cross_section_dim is None:
            self.cross_section_dim_ = []
        elif isinstance(self.cross_section_dim, str):
            self.cross_section_dim_ = [self.cross_section_dim]
        else:
            self.cross_section_dim_ = list(self.cross_section_dim)
        if self.time_dim is None:
            self.time_dim_ = []
        elif isinstance(self.time_dim, str):
            self.time_dim_ = [self.time_dim]
        else:
            self.time_dim_ = list(self.time_dim)

        if self.field_names is None:
            self.data_fields_ = []
        else:
            self.data_fields_ = [
                c
                for c in self.field_names
                if c not in self.cross_section_dim_ and c not in self.time_dim_
            ]


@attrs.define(kw_only=False, slots=False)
class BasePredictablyDataType(BaseObject):  # numpydoc ignore=PR02
    """Base class for `predictably` data types.

    Provides core functionality for declaring and interacting with a dataset in
    `predictably`.

    Parameters
    ----------
    dataframe : pl.LazyFrame | pl.DataFrame | pd.DataFrame
        The input dataframe to declare as the concrete data type.
    metadata : predictably.Metadata
        Metadata about the input `dataframe`.

    Attributes
    ----------
    lazyframe : pl.LazyFrame
        Representation of the input data as a ``polars.LazyFrame``.
    """

    dataframe: SupportedDataFrames
    metadata: Metadata
    lazyframe: SupportedDataFrames = attrs.field(init=False, repr=False, default=None)

    def __attrs_post_init__(self) -> None:
        """One-time post initialization variable augmentation.

        Used to convert input data to a lazyframe.
        """
        if self.dataframe is not None:
            self.lazyframe = self._to_lazyframe(self.dataframe)
        else:
            self.lazyframe = None

    @classmethod
    def _generate_metadata(
        cls, data: SupportedDataTypes, metadata: Metadata | None = None
    ) -> Metadata:
        """Create Metadata corresponding to the user input.

        This method will be overwritten by child classes.

        Parameters
        ----------
        data : pl.LazyFrame | pl.DataFrame | pd.DataFrame | np.ndarray | xa.DataArray
            The data to generate metadata for.
        metadata : MetaData, default=None
            Metadata about the input array.

            - If None, `predictably` will try to discover metadata about the input data.
            - If `metadata` does not include all metadata attributes, then
              `predictably` will try to discover the values.
            - Otherwise, the provided `metadata` will be returned unchanged.

        Returns
        -------
        Metadata
            The metadata about the input dataframe.
        """
        raise NotImplementedError()

    @classmethod
    def _array_to_dataframe(
        cls, array: SupportedArrays, metadata: Metadata
    ) -> pl.LazyFrame:
        """Convert input array into a ``polars.LazyFrame``.

        This method will be overwritten by child classes.

        Parameters
        ----------
        array : np.ndarray | xa.DataArray
            The array to convert to a dataframe.
        metadata : MetaData
            Metadata about the input array.

            - If None, `predictably` will try to discover the needed metadata to convert
              the input `array` to a dataframe.
            - If `metadata` does not include all attributes needed for the `array` to
              dataframe conversion, then `predictably` will try to discover the values
              for applicable attributes without metadata.
            - Otherwise, the provided `metadata` will be used in the `array` to
              dataframe conversion.

        Returns
        -------
        pl.LazyFrame
            A ``polars.LazyFrame`` representing the data in the input array.
        """
        raise NotImplementedError()

    @classmethod
    def from_dataframe(
        cls, df: SupportedDataFrames, metadata: Metadata | None = None
    ) -> Self:
        """Create a `predictably` data type from a dataframe.

        Users should use this method to create a new data object instead of
        instantiating the class directly.

        Parameters
        ----------
        df : pl.LazyFrame | pl.DataFrame | pd.DataFrame
            The input dataframe.
        metadata : MetaData, default=None
            Metadata about the input dataframe.

            - If None, `predictably` will try to discover metadata about the input data.
            - If `metadata` does not include all optional attributes, then `predictably`
              will try to discover the values for applicable attributes without
              metadata.
            - Otherwise, the provided `metadata` and `df` will be used to construct
              an instance of the data type.

        Returns
        -------
        Self
            Constructs an instance of self.

        See Also
        --------
        from_array : To create `predictably` data type from an array.
        """
        df = check_supported_external_type(df, type_="dataframe")
        metadata = cls._generate_metadata(df, metadata=metadata)
        return cls(df, metadata)  # type: ignore[call-arg]

    @classmethod
    def from_array(
        cls, array: SupportedArrays, metadata: Metadata | None = None
    ) -> Self:
        """Create `predictably` data type from an array.

        Users should use this method to create a new data object instead of
        instantiating the class directly.

        Parameters
        ----------
        array : np.ndarray | xa.DataArray
            The array to convert to a dataframe.
        metadata : MetaData, default=None
            Metadata about the input dataframe.

            - If None, `predictably` will try to discover metadata about the input data.
            - If `metadata` does not include all optional attributes, then `predictably`
              will try to discover the values for applicable attributes without
              metadata.
            - Otherwise, the provided `metadata` and `df` will be used to construct
              an instance of the data type.

        Returns
        -------
        Self
            Constructs an instance of self.

        See Also
        --------
        from_dataframe : To create `predictably` data type from a dataframe.
        """
        array = check_supported_external_type(array, type_="array")
        metadata = cls._generate_metadata(array, metadata=metadata)
        df = cls._array_to_dataframe(array, metadata=metadata)
        return cls(df, metadata)  # type: ignore[call-arg]

    def _to_lazyframe(self, df: SupportedDataFrames) -> pl.LazyFrame:
        """Convert input dataframe to ``polars.LazyFrame``.

        Applies internal logic to convert input data types to ``polars.LazyFrame``.

        Parameters
        ----------
        df : pl.LazyFrame | pl.DataFrame | pd.DataFrame
            The input dataframe.

        Returns
        -------
        pl.LazyFrame
            A ``polars.LazyFrame`` representing the data in the input dataframe.
        """
        if isinstance(df, pl.LazyFrame):
            return df
        elif isinstance(df, pl.DataFrame):
            return df.lazy()
        elif isinstance(df, pd.DataFrame):
            return pl.from_pandas(df).lazy()
        elif hasattr(df, "__dataframe__"):
            return pl.from_dataframe(df, allow_copy=True).lazy()
        else:
            raise_not_supported_external_type(type_="dataframe")

    @overload
    def to_dataframe(
        self, output_type: Literal["polars"]
    ) -> pl.LazyFrame:  # numpydoc ignore=GL08
        ...  # pragma: no cover

    @overload
    def to_dataframe(
        self, output_type: Literal["polars_df"]
    ) -> pl.DataFrame:  # numpydoc ignore=GL08
        ...  # pragma: no cover

    @overload
    def to_dataframe(
        self, output_type: Literal["pandas"]
    ) -> pd.DataFrame:  # numpydoc ignore=GL08
        ...  # pragma: no cover

    def to_dataframe(
        self, output_type: Literal["polars", "polars_df", "pandas"] = "polars"
    ) -> SupportedDataFrames:
        """Convert data to the specified dataframe type.

        `output_type` must be one of the 3rd party array types that is supported
        by `predictably`.

        Parameters
        ----------
        output_type : {"polars", "polars_df", "pandas"}, default="polars"
            The type of array the `predictably` datatype should be converted to.

        Returns
        -------
        pl.LazyFrame | pl.DataFrame | pd.DataFrame
            Data as requested dataframe type.

        See Also
        --------
        to_array : Output `predictably` data type to a specified array type.
        """
        raise NotImplementedError()

    @overload
    def to_array(
        self, output_type: Literal["numpy"]
    ) -> np.ndarray:  # numpydoc ignore=GL08
        ...  # pragma: no cover

    @overload
    def to_array(
        self, output_type: Literal["xarray"]
    ) -> xa.DataArray:  # numpydoc ignore=GL08
        ...  # pragma: no cover

    def to_array(
        self, output_type: Literal["numpy", "xarray"] = "numpy"
    ) -> SupportedArrays:
        """Convert data to the specified array type.

        `output_type` must be one of the 3rd party array types that is supported
        by `predictably`.

        Parameters
        ----------
        output_type : {"numpy", "xarray"}, default="numpy"
            The type of array the `predictably` datatype should be converted to.

        Returns
        -------
        np.ndarray | xa.DataArray
            Data as requested array type.

        See Also
        --------
        to_dataframe : Output `predictably` data type to a specified dataframe type.
        """
        raise NotImplementedError()
