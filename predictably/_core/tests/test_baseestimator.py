#!/usr/bin/env python3 -u
# copyright: predictably developers, BSD-3-Clause License (see LICENSE file)
# Elements of these tests re-use code developed for skbase. These elements
# are copyrighted by the skbase developers, BSD-3-Clause License. For
# conditions see https://github.com/sktime/skbase/blob/main/LICENSE
"""Tests for BaseEstimator class.

tests in this module:

    - test_baseestimator_inheritance: Test BaseEstimator inherits from BaseObject.
    - test_has_is_fitted: Test that BaseEstimator has is_fitted interface.
    - test_has_check_is_fitted: Test that BaseEstimator has check_is_fitted interface.
    - test_is_fitted: Test that is_fitted property returns _is_fitted as expected.
    - test_check_is_fitted_raises_error_when_unfitted: Test check_is_fitted raises
      an error when an estimator is unfitted an ``raise_error is True``.
"""

__author__ = ["RNKuhns"]
import inspect

import pytest

from predictably._core._base import BaseEstimator, BaseObject
from predictably._core._exceptions import NotFittedError


@pytest.fixture
def fixture_estimator():
    """Pytest fixture of BaseEstimator class."""
    return BaseEstimator


@pytest.fixture
def fixture_estimator_instance():
    """Pytest fixture of BaseEstimator instance."""
    return BaseEstimator()


def test_baseestimator_inheritance(fixture_estimator, fixture_estimator_instance):
    """Check BaseEstimator correctly inherits from BaseObject."""
    estimator_is_subclass_of_baseobejct = issubclass(fixture_estimator, BaseObject)
    estimator_instance_is_baseobject_instance = isinstance(
        fixture_estimator_instance, BaseObject
    )
    assert (
        estimator_is_subclass_of_baseobejct
        and estimator_instance_is_baseobject_instance
    ), "`BaseEstimator` does not correctly inherit from `BaseObject`."


def test_has_is_fitted(fixture_estimator_instance):
    """Test BaseEstimator has `is_fitted` property."""
    has_private_is_fitted = hasattr(fixture_estimator_instance, "_is_fitted")
    has_is_fitted = hasattr(fixture_estimator_instance, "is_fitted")
    assert (
        has_private_is_fitted and has_is_fitted
    ), "BaseEstimator does not have `is_fitted` property;"


def test_has_check_is_fitted(fixture_estimator_instance):
    """Test BaseEstimator has `check_is_fitted` method."""
    has_check_is_fitted = hasattr(fixture_estimator_instance, "check_is_fitted")
    is_method = inspect.ismethod(fixture_estimator_instance.check_is_fitted)
    assert (
        has_check_is_fitted and is_method
    ), "`BaseEstimator` does not have `check_is_fitted` method."


def test_is_fitted(fixture_estimator_instance):
    """Test BaseEstimator `is_fitted` property returns expected value."""
    expected_value_unfitted = (
        fixture_estimator_instance.is_fitted == fixture_estimator_instance._is_fitted
    )
    assert (
        expected_value_unfitted
    ), "`BaseEstimator` property `is_fitted` does not return `_is_fitted` value."


def test_check_is_fitted_raises_error_when_unfitted(fixture_estimator_instance):
    """Test BaseEstimator `check_is_fitted` method raises an error."""
    name = fixture_estimator_instance.__class__.__name__
    match = f"This instance of {name} has not been fitted yet. Please call `fit` first."
    with pytest.raises(NotFittedError, match=match):
        fixture_estimator_instance.check_is_fitted()

    # Verify false returned on unfitted estimator when raise_error is False
    assert fixture_estimator_instance.check_is_fitted(raise_error=False) is False

    fixture_estimator_instance._is_fitted = True
    assert fixture_estimator_instance.check_is_fitted() is True
