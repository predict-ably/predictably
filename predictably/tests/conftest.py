"""Common functionality for skbase unit tests."""
from copy import deepcopy
from typing import Any, ClassVar, Dict, List, Optional

import attrs

from predictably._core._base import BaseEstimator, BaseObject

__all__: List[str] = ["Parent", "Child"]
__author__: List[str] = ["RNKuhns"]

PREDICTABLY_BASE_CLASSES = (BaseObject, BaseEstimator)


# Fixture class for testing tag system
@attrs.define(kw_only=True, slots=False, repr=False)
class Parent(BaseObject):
    """Parent class to test BaseObject's usage."""

    _tags: ClassVar[Dict[str, Any]] = {"A": "1", "B": 2, "C": 1234, "3": "D"}

    a: str = "something"
    b: int = 7
    c: Optional[int] = None

    def some_method(self):
        """To be implemented by child class."""
        pass


# Fixture class for testing tag system, child overrides tags
@attrs.define(kw_only=True, slots=False, repr=False)
class Child(Parent):
    """Child class that is child of FixtureClassParent."""

    _tags: ClassVar[Dict[str, Any]] = {"A": 42, "3": "E"}
    __author__: ClassVar[List[str]] = ["Someone", "Someone Else"]

    def some_method(self):
        """Child class' implementation."""
        pass

    def some_other_method(self):
        """To be implemented in the child class."""
        pass


@attrs.define(kw_only=True, slots=False, repr=False)
class CompositionDummy(BaseObject):
    """Potentially composite object, for testing."""

    foo: Any = 11
    bar: Any = 84
    foo_: Optional[int] = attrs.field(
        alias="foo_", init=False, default=None, repr=False
    )

    def __attrs_post_init__(self):
        """Execute code after init."""
        self.foo_ = deepcopy(self.foo)

    @classmethod
    def get_test_params(cls, parameter_set="default"):
        """Return testing parameter settings for the estimator.

        Parameters
        ----------
        parameter_set : str, default="default"
            Name of the set of test parameters to return, for use in tests. If no
            special parameters are defined for a value, will return `"default"` set.

        Returns
        -------
        params : dict or list of dict, default = {}
            Parameters to create testing instances of the class
            Each dict are parameters to construct an "interesting" test instance, i.e.,
            `MyClass(**params)` or `MyClass(**params[i])` creates a valid test instance.
            `create_test_instance` uses the first (or only) dictionary in `params`
        """
        params1 = {"foo": 42}
        params2 = {"foo": CompositionDummy(126)}
        return [params1, params2]
