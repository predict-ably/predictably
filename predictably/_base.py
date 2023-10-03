#!/usr/bin/env python3 -u
# copyright: predict-ably, BSD-3-Clause License (see LICENSE file)
# Elements of predictably.validate reuse code developed for skbase. These elements
# are copyrighted by the skbase developers, BSD-3-Clause License. For
# conditions see https://github.com/sktime/skbase/blob/main/LICENSE
"""The base class used throughout `predictably`.

`predictably` classes typically inherit from ``BaseClass``.
"""
import inspect
import sys
from copy import deepcopy
from typing import Any, ClassVar, Dict, List, Optional, Sequence, Union

if sys.version_info < (3, 11):
    from typing_extensions import Self
else:
    from typing import Self

import attrs

from predictably import get_config
from predictably._config import _CONFIG_REGISTRY
from predictably._exceptions import NotFittedError

__author__: List[str] = ["RNKuhns"]
__all__: List[str] = []


@attrs.define(kw_only=True, slots=False)
class BaseObject:
    """Base class for `predictably` classes with tag and config management.

    All classes in `predictably` that use the tag interface or allow users
    to override the global configuration should inherit from ``BaseClass``.
    """

    _tags: ClassVar[Dict[str, Any]] = {}
    _config: ClassVar[Dict[str, Any]] = {}

    @classmethod
    def _get_param_names(cls, init_only: bool = True) -> List[str]:
        """Get object's parameter names.

        Optionally allow only return names of an ``attrs.field`` that is set to be
        part of the object's initialization.

        Parameters
        ----------
        init_only : bool, default=True
            Whether to only return ``attrs.field`` that are set to be part of the
            object's initialization.

            - If True, only values of an ``attrs.field`` that is set to be part of
              the object's initialization are returned.
            - If False, the values of any ``attrs.field`` defined on the object are
              returned.

        Returns
        -------
        list[str]
            Alphabetically sorted list of parameter names of cls.
        """
        return sorted(attrs.fields_dict(BaseObject).keys())

    @classmethod
    def get_param_defaults(cls, init_only: bool = True) -> Dict[str, Any]:
        """Get object's parameter defaults.

        Optionally allow only return names of an ``attrs.field`` that is set to be
        part of the object's initialization.

        Parameters
        ----------
        init_only : bool, default=True
            Whether to only return ``attrs.field`` that are set to be part of the
            object's initialization.

            - If True, only values of an ``attrs.field`` that is set to be part of
              the object's initialization are returned.
            - If False, the values of any ``attrs.field`` defined on the object are
              returned.

        Returns
        -------
        dict[str, Any]
            Mapping of parameter names to their default values.
        """
        parameters = attrs.fields_dict(BaseObject)
        default_paramms = {k: parameters[k].default for k in cls._get_param_names()}
        return default_paramms

    def _init_flags(self, flag_name: str = "_tags") -> Self:
        """Create dynamic flag dictionary in class instance.

        Should be called in __init__ of the host class to create attributes
        with format [flag_name]_dynamic that are set to an empty dict value.

        Parameters
        ----------
        flag_name : str, default = "_flags"
            Name of the flag attribute to be created in the instance.

        Returns
        -------
        Self
            Reference to self.
        """
        setattr(self, f"{flag_name}_dynamic", {})
        return self

    @classmethod
    def _get_class_flags(cls, flag_name: str = "_tags") -> Dict[str, Any]:
        """Get class flags from estimator class and all its parent classes.

        Utility method to return class flags that are the not overridden
        by `_set_flags`.

        Parameters
        ----------
        flag_name : str, default = "_tags"
            Name of the flag attribute that is read.

        Returns
        -------
        dict
            Dictionary of name : value pairs. Collected from the
            class attribute via nested inheritance.
        """
        collected_flags = {}
        # We exclude the basic Python object.
        for parent_class in reversed(inspect.getmro(cls)[:-1]):
            if hasattr(parent_class, flag_name):
                # Need the if here because mixins might not have _more_flags
                # but might do redundant work in estimators
                # (i.e. calling more flags on BaseEstimator multiple times)
                more_flags = getattr(parent_class, flag_name)
                collected_flags.update(more_flags)

        return deepcopy(collected_flags)

    def _get_flags(self, flag_name: str = "_tags") -> Dict[str, Any]:
        """Get flags from estimator class and dynamic flag overrides.

        Utility method to return all object flags including any overrides performed
        by `_set_flags`.

        Parameters
        ----------
        flag_name : str, default = "_flags"
            Name of the flag attribute that is read.

        Returns
        -------
        dict
            Dictionary of name : value pairs. The collected flags
            are first collected from `flag_name` via nested inheritance. Then
            any overrides of the class tags are collected from [flag_name]_dynamic
            object attribute.
        """
        collected_flags = self._get_class_flags(flag_name=flag_name)

        if hasattr(self, f"{flag_name}_dynamic"):
            collected_flags.update(getattr(self, f"{flag_name}_dynamic"))

        return deepcopy(collected_flags)

    def _get_flag(
        self,
        flag_name: str,
        flag_value_default: Any = None,
        flag_attr_name: str = "_tags",
        raise_error: bool = True,
    ) -> Any:
        """Get flag value from estimator class and dynamic flag overrides.

        Utility method to return a specific object flags including any overrides
        performed by `_set_flags`.

        Parameters
        ----------
        flag_name : str
            Name of flag to be retrieved.
        flag_value_default : Any, default=None
            Default/fallback value if flag is not found.
        flag_attr_name : str, default = "_tags"
            Name of the flag attribute that is read. For example, the object's
            tags or config.
        raise_error : bool
            Whether a `ValueError` is raised when the flag is not found.

        Returns
        -------
        flag_value :
            Value of the `flag_name` flag in self. If not found, returns an error if
            raise_error is True, otherwise it returns `flag_value_default`.

        Raises
        ------
        ValueError
            If `flag_name` is not in the flag keys and `raise_error` is `True`.
        """
        collected_flags = self._get_flags(flag_name=flag_attr_name)

        flag_value = collected_flags.get(flag_name, flag_value_default)

        if raise_error and flag_name not in collected_flags.keys():
            raise ValueError(f"Tag with name {flag_name} could not be found.")

        return flag_value

    def _set_flags(self, flag_name: str = "_tags", **flag_dict: Any) -> Self:
        """Set dynamic flags to given values.

        Utility method to override an object's flag values.

        Parameters
        ----------
        flag_name : str, default = "_tags"
            Name of the flag attribute that is read.
        **flag_dict : dict
            Dictionary of name : value pairs.

        Returns
        -------
        Self
            Reference to self.

        Notes
        -----
        Changes object state by setting flag values in flag_dict as dynamic flags
        in self.
        """
        flag_update = deepcopy(flag_dict)
        dynamic_flags = f"{flag_name}_dynamic"
        if hasattr(self, dynamic_flags):
            getattr(self, dynamic_flags).update(flag_update)
        else:
            setattr(self, dynamic_flags, flag_update)

        return self

    def _get_tags(self) -> Dict[str, Any]:
        """Get all tag names and values.

        Returns class tags after any instance tag overrides.

        Returns
        -------
        dict
            Dictionary of name : value pairs. Tags are first collected from the
            class attribute via nested inheritance. Then any instance overrides
            are collected from the instance.
        """
        return self._get_flags(flag_name="_tags")

    def _get_tag(
        self, tag_name: str, tag_value_default: Any = None, raise_error: bool = True
    ) -> Any:
        """Get value of an individual tag.

        Returns value of tag after any instance tag overrides.

        Parameters
        ----------
        tag_name : str
            Name of tag to be retrieved.
        tag_value_default : Any, default=None
            Default/fallback value if tag is not found.
        raise_error : bool
            Whether a ValueError is raised when the tag is not found.

        Returns
        -------
        Any
            Value of the `tag_name` tag in self. If not found, returns an error if
            `raise_error` is True, otherwise it returns `tag_value_default`.

        Raises
        ------
        ValueError
            If `flag_name` is not in the flag keys and `raise_error` is `True`.
        """
        return self._get_flag(
            flag_name=tag_name,
            flag_value_default=tag_value_default,
            flag_attr_name="_tags",
            raise_error=raise_error,
        )

    def _get_config(
        self, config_param: Optional[Union[str, Sequence[str]]] = None
    ) -> Dict[str, Any]:
        """Get configuration parameters impacting the object.

        The configuration is retrieved in the following order:

        - `predictably` global configuration,
        - the class's local configuration set at class definition via ``_config``
          class variable or the objects ``set_config`` parameter.

        Parameters
        ----------
        config_param : str | sequence[str]
            The subset of configuration parameters to return.

        Returns
        -------
        dict[str, Any]
            Mapping of the object's config parameters and assigned values.
        """
        # Configuration is collected in a specific order from global to local
        # Start by collecting skbase's global config
        config = get_config().copy()

        # Then get the local config for any optional instance config overrides
        local_config = self._get_flags(flag_name="_config").copy()

        # We make sure we don't return an invalid configuration value.
        # In this case, we'll fallback to the default value if an invalid value
        # was set as the local override of the global config
        for config_param, config_value in local_config.items():
            if config_param in _CONFIG_REGISTRY:
                msg = "Invalid value encountered for global configuration parameter "
                msg += f"{config_param}. Using global parameter configuration value.\n"
                config_value = _CONFIG_REGISTRY[
                    config_param
                ].get_valid_param_or_default(
                    config_value, default_value=config[config_param], msg=msg
                )
                local_config[config_param] = config_value
        config.update(local_config)

        if config_param is None:
            config_params_ = config
        else:
            if isinstance(config_param, str):
                config_param_tuple = (config_param,)
            else:
                config_param_tuple = tuple(config_param)

            config_params_ = {p: config[p] for p in config_param_tuple if p in config}

        return config_params_

    def _set_tags(self, **tag_dict: Any) -> Self:
        """Override instance tag values.

        Utility method to override an object's tag values.

        Parameters
        ----------
        **tag_dict : dict
            Dictionary of tag name: tag value pairs.

        Returns
        -------
        Self
            Reference to self.

        Notes
        -----
        Changes object state by setting tag values in tag_dict as dynamic tags in self.
        """
        self._set_flags(flag_name="_tags", **tag_dict)

        return self

    def _set_config(self, **config_dict: Any) -> Self:
        """Override configuration parameters impacting the object.

        Utility method to override an object's config values. This will override
        the `predictably` global configuration for the object.

        Parameters
        ----------
        **config_dict : dict
            Dictionary of config name: config value pairs.

        Returns
        -------
        Self
            Reference to self.

        Notes
        -----
        Changes object state by setting config values in `config_dict` as dynamic
        tags in self.
        """
        self._set_flags(flag_name="_config", **config_dict)

        return self


@attrs.define(kw_only=False, slots=False)
class BaseEstimator(BaseObject):
    """Base class for estimators with scikit-learn and sktime design patterns.

    Extends BaseObject to include basic functionality for fittable estimators.
    """

    _is_fitted: bool = attrs.field(
        init=False, repr=False, alias="_is_fitted", default=False
    )

    def __attrs_pre_init__(self) -> None:
        """Execute prior to init.

        Used to make sure attrs is executing __init__ of parent(s).
        """
        super().__init__()

    @property
    def is_fitted(self) -> bool:
        """Whether `fit` has been called.

        Inspects object's `_is_fitted` attribute that should initialize to False
        during object construction, and be set to True in calls to an object's
        `fit` method.

        Returns
        -------
        bool
            Whether the estimator has been `fit`.
        """
        return self._is_fitted

    def check_is_fitted(self, raise_error: bool = True) -> bool:
        """Check if the estimator has been fitted.

        Inspects object's `_is_fitted` attribute that should initialize to False
        during object construction, and be set to True in calls to an object's
        `fit` method.

        Parameters
        ----------
        raise_error : bool, default=True
            Whether to raise an error if estimator is not fitted.

            - If ``raise_error is True`` (default) then an error is raised if the
              estimator is not fitted.
            - Otherwise, returns True or False indicating if the estimator has been fit.

        Returns
        -------
        bool
            Whether the estimator has been fit.

        Raises
        ------
        NotFittedError
            If the estimator has not been fitted yet.
        """
        if not self.is_fitted and raise_error:
            raise NotFittedError(
                f"This instance of {self.__class__.__name__} has not been fitted yet. "
                f"Please call `fit` first."
            )
        else:
            return self.is_fitted
