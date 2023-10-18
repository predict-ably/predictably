#!/usr/bin/env python3 -u
# copyright: predict-ably, BSD-3-Clause License (see LICENSE file)
"""`predictably`'s core cross section data type.

Users should not instantiate the `CrossSection` class directly. Use the `from_array`
or `from_dataframe` methods or the ``predictably.from_external_data`` functional
interface.
"""
from __future__ import annotations

import attrs
import polars as pl

from predictably.data.types._base import BasePredictablyDataType, Metadata
from predictably.data.types._types import SupportedArrays, SupportedDataTypes

__author__: list[str] = ["RNKuhns"]
__all__: list[str] = []


@attrs.define(kw_only=True, slots=False)
class CrossSection(BasePredictablyDataType):  # numpydoc ignore=PR02
    """`predictably` cross-sectional data type.

    Provides core functionality for declaring and interacting with a dataset a
    cross-section dataset in `predictably`.

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

    @classmethod
    def _generate_metadata(
        cls, data: SupportedDataTypes, metadata: Metadata | None = None
    ) -> Metadata:
        """Create Metadata corresponding to the input data.

        Discovers metadata from the input dataframe.

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
        raise NotImplementedError

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
