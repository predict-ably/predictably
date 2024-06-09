#!/usr/bin/env python3 -u
# copyright: predict-ably, BSD-3-Clause License (see LICENSE file)
"""Class to hold information on a configurable parameter settings.

Used to store information about predictably's global configuration.
"""
import collections
import warnings
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple, Union

from predictably.utils._iter import _format_seq_to_str

__author__: List[str] = ["RNKuhns"]
__all__: List[str] = ["GlobalConfigParamSetting"]


@dataclass
class GlobalConfigParamSetting:
    """Metadata about a given for a given config parameter.

    Also provides utility methods to retrieve information about the global
    parameter.
    """

    name: str
    expected_type: Union[type, Tuple[type]]
    default_value: Any
    allowed_values: Optional[Union[Tuple[Any, ...], List[Any]]]

    def _get_values(self, param: str) -> Tuple[Any, ...]:
        """Get values of specified parameter.

        Utility function to retrieve the values assigned to the specified parameter
        as a tuple.

        Parameters
        ----------
        param : str
            The name of the parameter whose values should be retrieved.

        Returns
        -------
        tuple
            Values assigned to `param`.
        """
        param_values = getattr(self, param)
        if param_values is None:
            return ()
        elif isinstance(param_values, collections.abc.Iterable) and not isinstance(
            self.allowed_values, str
        ):
            return tuple(param_values)
        else:
            return (param_values,)

    def get_allowed_values(self) -> Tuple[Any, ...]:
        """Get global parameter's `allowed_values`.

        Returns an empty tuple if `allowed_values` is None.

        Returns
        -------
        tuple
            Allowable values if any.
        """
        return self._get_values("allowed_values")

    def get_expected_type(self) -> Tuple[type, ...]:
        """Get global parameter's `expected_type`.

        Returns an empty tuple if `expected_type` is None.

        Returns
        -------
        tuple
            Allowable values if any.
        """
        return self._get_values("expected_type")

    def is_valid_param_value(self, value: Any) -> bool:
        """Validate that a global configuration value is valid.

        Verifies that the value set for a global configuration parameter is valid
        based on the its configuration settings.

        Parameters
        ----------
        value : Any
            The value that is validated against the parameter's allowed_values.

        Returns
        -------
        bool
            Whether a parameter value is valid.
        """
        valid_param: bool
        if not isinstance(value, self.expected_type) or (
            self.allowed_values is not None and value not in self.get_allowed_values()
        ):
            valid_param = False
        else:
            valid_param = True
        return valid_param

    def get_valid_param_or_default(
        self, value: Any, default_value: Any = None, msg: str = ""
    ) -> Any:
        """Retrieve validated `value` for global parameter.

        Returns default if it is not valid.

        Parameters
        ----------
        value : Any
            The configuration parameter value to set.
        default_value : Any, default=None
            An optional default value to use to set the configuration parameter
            if `value` is not valid based on defined expected type and allowed
            values. If None, and `value` is invalid then the classes `default_value`
            parameter is used.
        msg : str, default=""
            An optional message to be used as start of the UserWarning message.

        Returns
        -------
        Any
            The value of the parameter to be retrieved. A default value is used
            if the provided value is invalid for the parameter.
        """
        if self.is_valid_param_value(value):
            return value
        else:
            expected_type_str = _format_seq_to_str(
                self.get_expected_type(), last_sep="or", remove_type_text=True
            )
            msg += f"When setting global config values for `{self.name}`, the values "
            msg += f"should be of type {expected_type_str}.\n"
            if self.allowed_values is not None:
                values_str = _format_seq_to_str(
                    self.get_allowed_values(), last_sep="or", remove_type_text=True
                )
                msg += f"Allowed values should be one of {values_str}. "
            msg += f"But found {value}."
            warnings.warn(msg, UserWarning, stacklevel=2)
            return default_value if default_value is not None else self.default_value
