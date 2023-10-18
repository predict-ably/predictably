#!/usr/bin/env python3 -u
# copyright: predict-ably, BSD-3-Clause License (see LICENSE file)
# Elements of predictably.validate reuse code developed for skbase. These elements
# are copyrighted by the skbase developers, BSD-3-Clause License. For
# conditions see https://github.com/sktime/skbase/blob/main/LICENSE
"""The base class used throughout `predictably`.

`predictably` classes typically inherit from ``BaseClass``.
"""
import collections
import inspect
import re
import sys
from copy import deepcopy
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Union,
)

if sys.version_info < (3, 11):
    from typing_extensions import Self
else:
    from typing import Self

import attrs

from predictably import get_config
from predictably._config import _CONFIG_REGISTRY
from predictably._core._exceptions import NotFittedError
from predictably._core._pprint._object_html_repr import _object_html_repr
from predictably.utils._iter import _format_seq_to_str

__author__: List[str] = ["RNKuhns"]
__all__: List[str] = ["BaseEstimator", "BaseObject"]


@attrs.define(kw_only=True, slots=False, repr=False)
class BaseObject:
    """Base class for `predictably` classes with tag and config management.

    All classes in `predictably` that use the tag interface or allow users
    to override the global configuration should inherit from ``BaseClass``.
    """

    _tags: ClassVar[Dict[str, Any]] = {}
    _config: ClassVar[Dict[str, Any]] = {}
    _tags_dynamic: Dict[str, Any] = attrs.field(
        init=False, repr=False, alias="_tags_dynamic", factory=dict
    )
    _config_dynamic: Dict[str, Any] = attrs.field(
        init=False, repr=False, alias="_config_dynamic", factory=dict
    )

    @classmethod
    def _get_init_signature(cls) -> List[inspect.Parameter]:
        """Get class init signature.

        Useful in parameter inspection.

        Returns
        -------
        List[str]
            The inspected parameter objects (including defaults).

        Raises
        ------
        RuntimeError if cls has varargs in __init__.
        """
        # fetch the constructor
        init = cls.__init__
        if init is object.__init__:
            # No explicit constructor to introspect
            return []

        # introspect the constructor arguments to find the model parameters
        # to represent
        init_signature = inspect.signature(init)

        # Consider the constructor parameters excluding 'self'
        parameters = [
            p
            for p in init_signature.parameters.values()
            if p.name != "self" and p.kind != p.VAR_KEYWORD
        ]
        for p in parameters:
            if p.kind == p.VAR_POSITIONAL:
                raise RuntimeError(
                    "scikit-learn compatible estimators should always "
                    "specify their parameters in the signature"
                    " of their __init__ (no varargs)."
                    " %s with constructor %s doesn't "
                    " follow this convention." % (cls, init_signature)
                )

        return parameters

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
        if init_only:
            parameters = sorted([p.name for p in cls._get_init_signature()])
        else:
            parameters = sorted(attrs.fields_dict(cls).keys())

        return parameters

    @classmethod
    def _get_param_defaults(cls, init_only: bool = True) -> Dict[str, Any]:
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
        parameters = attrs.fields_dict(cls)
        default_params = {
            k: parameters[k].default for k in cls._get_param_names(init_only=init_only)
        }
        return default_params

    def get_params(self, deep: bool = True) -> Dict[str, Any]:
        """Get a dict of parameters values for this object.

        Returns the instances direct parameters and optionally (when ``deep is True``)
        the parameters of any instance parameters that have values implementing
        `get_params`.

        Parameters
        ----------
        deep : bool, default=True
            Whether to return parameters of components.

            * If True, will return a dict of parameter names and values for this object,
              including parameters of components (i.e., BaseObject-valued parameters).
            * If False, will return a dict of parameter name and values for this object,
              but not include parameters of components.

        Returns
        -------
        params
            Instances parameters and their values.

            * Always returns all parameters of this object and the values passed at
              object construction.
            * If ``deep=True``, also contains keys-value pairs of component parameters
              parameters of components are indexed as `[componentname]__[paramname]`
              all parameters of `componentname` appear as `paramname` with its value.
              This will also include arbitrary levels of component recursion,
              e.g., `[componentname]__[componentcomponentname]__[paramname]`, etc.

        Raises
        ------
        AttributeError :
            If the object does not assign all init parameters to attributes with the
            same name.
        """
        parameters = self._get_param_names(init_only=True)
        missing_params = [p for p in parameters if not hasattr(self, p)]
        if missing_params:
            param_str = "parameter" if len(missing_params) == 1 else "parameters"
            missing_param_str = _format_seq_to_str(missing_params, last_sep="and")
            msg = "BaseObject's should assign all init parameters to an attribute "
            msg += f"with the same name.\n `BadObject` {param_str} {missing_param_str}"
            msg += " did not follow this convention."
            raise AttributeError(msg)

        params = {key: getattr(self, key) for key in parameters}

        if deep:
            deep_params = {}
            for key, value in params.items():
                if hasattr(value, "get_params"):
                    deep_items = value.get_params().items()
                    deep_params.update({f"{key}__{k}": val for k, val in deep_items})
            params.update(deep_params)

        return params

    def set_params(self, **params: Any) -> Self:
        """Set the parameters of this object.

        The method works on simple estimators as well as on nested objects.
        The latter have parameters of the form ``<component>__<parameter>`` so
        that it's possible to update each component of a nested object.

        Parameters
        ----------
        **params : dict
            BaseObject parameters.

        Returns
        -------
        self
            Reference to self (after parameters have been set).
        """
        if not params:
            # Simple optimization to gain speed (inspect is slow)
            return self
        valid_params = self.get_params(deep=True)

        nested_params: collections.defaultdict[str, Any] = collections.defaultdict(
            dict
        )  # grouped by prefix
        for key, value in params.items():
            key, delim, sub_key = key.partition("__")
            if key not in valid_params:
                raise ValueError(
                    "Invalid parameter %s for object %s. "
                    "Check the list of available parameters "
                    "with `object.get_params().keys()`." % (key, self)
                )

            if delim:
                nested_params[key][sub_key] = value
            else:
                setattr(self, key, value)
                valid_params[key] = value

        self.reset()

        # recurse in components
        for key, sub_params in nested_params.items():
            valid_params[key].set_params(**sub_params)

        return self

    @classmethod
    def _get_class_flags(cls, flag_attr_name: str = "_tags") -> Dict[str, Any]:
        """Get class flags from estimator class and all its parent classes.

        Utility method to return class flags that are the not overridden
        by `_set_flags`.

        Parameters
        ----------
        flag_attr_name : str, default = "_tags"
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
            if hasattr(parent_class, flag_attr_name):
                # Need the if here because mixins might not have _more_flags
                # but might do redundant work in estimators
                # (i.e. calling more flags on BaseEstimator multiple times)
                more_flags = getattr(parent_class, flag_attr_name)
                collected_flags.update(more_flags)

        return deepcopy(collected_flags)

    @classmethod
    def _get_class_flag(
        cls,
        flag_name: str,
        flag_value_default: Any = None,
        flag_attr_name: str = "_tags",
        raise_error: bool = False,
    ) -> Any:
        """Get flag value from estimator class.

        Utility method to return a specific object flags.

        Parameters
        ----------
        flag_name : str
            Name of flag to be retrieved.
        flag_value_default : Any, default=None
            Default/fallback value if flag is not found.
        flag_attr_name : str, default = "_tags"
            Name of the flag attribute that is read. For example, the object's
            tags or config.
        raise_error : bool, default=False
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
        collected_flags = cls._get_class_flags(flag_attr_name=flag_attr_name)

        flag_value = collected_flags.get(flag_name, flag_value_default)

        if raise_error and flag_name not in collected_flags.keys():
            flag_ = flag_attr_name.lstrip("_").title()
            raise ValueError(f"{flag_} with name {flag_name} could not be found.")

        return flag_value

    def _get_flags(self, flag_attr_name: str = "_tags") -> Dict[str, Any]:
        """Get flags from estimator class and dynamic flag overrides.

        Utility method to return all object flags including any overrides performed
        by `_set_flags`.

        Parameters
        ----------
        flag_attr_name : str, default = "_flags"
            Name of the flag attribute that is read.

        Returns
        -------
        dict
            Dictionary of name : value pairs. The collected flags
            are first collected from `flag_attr_name` via nested inheritance. Then
            any overrides of the class tags are collected from [flag_attr_name]_dynamic
            object attribute.
        """
        collected_flags = self._get_class_flags(flag_attr_name=flag_attr_name)
        if hasattr(self, f"{flag_attr_name}_dynamic"):
            collected_flags.update(getattr(self, f"{flag_attr_name}_dynamic"))

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
        raise_error : bool, default=True
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
        collected_flags = self._get_flags(flag_attr_name=flag_attr_name)

        flag_value = collected_flags.get(flag_name, flag_value_default)

        if raise_error and flag_name not in collected_flags.keys():
            flag_ = flag_attr_name.lstrip("_").title()[:-1]
            raise ValueError(f"{flag_} with name {flag_name} could not be found.")

        return flag_value

    def _set_flags(self, flag_attr_name: str = "_tags", **flag_dict: Any) -> Self:
        """Set dynamic flags to given values.

        Utility method to override an object's flag values.

        Parameters
        ----------
        flag_attr_name : str, default = "_tags"
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
        dynamic_flags = f"{flag_attr_name}_dynamic"
        if hasattr(self, dynamic_flags):
            getattr(self, dynamic_flags).update(flag_update)
        else:
            setattr(self, dynamic_flags, flag_update)

        return self

    def _clone_flags(
        self,
        obj: "BaseObject",
        flag_names: Optional[Union[str, Sequence[str]]] = None,
        flag_attr_name: str = "_tags",
    ) -> Self:
        """Update object with flags from another object.

        Updated flags are applied as dynamic override. Any flags in this object but
        not the other object are not overridden. Any flags in the other object but not
        this object are added. Flags in both objects are updated to reflect the values
        of the other object.

        Parameters
        ----------
        obj : :class:`BaseObject`
            The object whose parameters should be cloned.
        flag_names : str | list[str], default=None
            Name(s) of subset of flags to clone. If None then all flags are cloned.
        flag_attr_name : str, default = "_flags"
            Name of the flag attribute that is read.

        Returns
        -------
        self
            Reference to self.

        Notes
        -----
        Changes object state by setting flag values in flag_set from object as
        dynamic flags in self.
        """
        flags_est = deepcopy(obj._get_flags(flag_attr_name=flag_attr_name))

        # if flag_set is not passed, default is all flags in object
        flag_names_: Iterable[str]
        if flag_names is None:
            flag_names_ = flags_est.keys()
        # if flag_set is passed, intersect keys with flags in object
        elif isinstance(flag_names, str):
            flag_names_ = [flag_names]
        else:
            flag_names_ = flag_names

        update_dict = {key: flags_est[key] for key in flag_names_ if key in flags_est}

        self._set_flags(flag_attr_name=flag_attr_name, **update_dict)

        return self

    @classmethod
    def _get_class_tags(cls) -> Dict[str, Any]:
        """Get all class tag names and values.

        Any tag overrides made on the instance are ignored.

        Returns
        -------
        dict
            Dictionary of name : value pairscollected from the class attribute "_tags"
            via nested inheritance.
        """
        return cls._get_class_flags(flag_attr_name="_tags")

    @classmethod
    def _get_class_tag(
        cls, tag_name: str, tag_value_default: Any = None, raise_error: bool = False
    ) -> Any:
        """Get value of an individual tag.

        Returns value of tag before any instance tag overrides.

        Parameters
        ----------
        tag_name : str
            Name of tag to be retrieved.
        tag_value_default : Any, default=None
            Default/fallback value if tag is not found.
        raise_error : bool, default=False
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
        return cls._get_class_flag(
            flag_attr_name="_tags",
            flag_name=tag_name,
            flag_value_default=tag_value_default,
            raise_error=raise_error,
        )

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
        return self._get_flags(flag_attr_name="_tags")

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
        raise_error : bool, default=True
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

    def _clone_tags(
        self, obj: "BaseObject", tag_names: Optional[Union[str, Sequence[str]]] = None
    ) -> Self:
        """Update the tags of this object by cloning the tags from another object.

        The cloned tags are applied as dynamic overrides. Any tags in this object
        that are not in the new object will not be updated, but tags in the other
        object will be added to this object.

        Parameters
        ----------
        obj : :class:`BaseObject`
            The object whose tags should be cloned.
        tag_names : str | sequence[str], default=None
            Name(s) of subset of tags to clone. If None then all tags in object
            are cloned.

        Returns
        -------
        Self
            Reference to self.

        Notes
        -----
        Changes object state by setting tag values in tag_set from object as
        dynamic tags in self.
        """
        return self._clone_flags(obj=obj, flag_names=tag_names, flag_attr_name="_tags")

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
        local_config = self._get_flags(flag_attr_name="_config").copy()

        # We make sure we don't return an invalid configuration value.
        # In this case, we'll fallback to the default value if an invalid value
        # was set as the local override of the global config
        for config_param_, config_value in local_config.items():
            if config_param_ in _CONFIG_REGISTRY:
                msg = "Invalid value encountered for global configuration parameter "
                msg += f"{config_param_}. Using global parameter configuration value.\n"
                config_value = _CONFIG_REGISTRY[
                    config_param_
                ].get_valid_param_or_default(
                    config_value, default_value=config[config_param_], msg=msg
                )
                local_config[config_param_] = config_value
        config.update(local_config)

        if config_param is None:
            config_params_ = config
        else:
            config_param_tuple: tuple[str, ...]
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
        self._set_flags(flag_attr_name="_tags", **tag_dict)

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
        self._set_flags(flag_attr_name="_config", **config_dict)

        return self

    def reset(self) -> Self:
        """Re-initialize the object to a post-init state.

        Using reset, runs __init__ with current values of hyper-parameters
        (result of get_params). This Removes any object attributes, except:

            - hyper-parameters = arguments of __init__
            - object attributes containing double-underscores, i.e., the string "__"

        Class and object methods, and class attributes are also unaffected.

        Returns
        -------
        self
            Instance of class reset to a clean post-init state but retaining
            the current hyper-parameter values.

        Notes
        -----
        Equivalent to sklearn.clone but overwrites self. After self.reset()
        call, self is equal in value to `type(self)(**self.get_params(deep=False))`
        """
        # retrieve parameters to copy them later
        params = self.get_params(deep=False)

        # delete all object attributes in self
        attrs = [attr for attr in dir(self) if "__" not in attr]
        cls_attrs = list(dir(type(self)))
        self_attrs = set(attrs).difference(cls_attrs)
        for attr in self_attrs:
            delattr(self, attr)

        # run init with a copy of parameters self had at the start
        self.__init__(**params)  # type: ignore

        return self

    def is_composite(self) -> bool:
        """Check if the object is composed of other BaseObjects.

        A composite object is an object which contains objects, as parameters. This
        is determined by inspecting the values of the instance parameters.

        Returns
        -------
        bool
            Whether an object has any parameters whose values are BaseObjects.
        """
        params = self.get_params(deep=False)
        composite = any(isinstance(x, BaseObject) for x in params.values())

        return composite

    def _components(self, base_class: Optional[type] = None) -> dict[str, Any]:
        """Return references to all state changing BaseObject type attributes.

        This *excludes* the blue-print-like components passed in the __init__.

        Caution: this method returns *references* and not *copies*. Writing to
        the reference will change the object's attribute.

        Parameters
        ----------
        base_class : type, default=None
            Type to use when determining components. Returned components will
            only be those that are subclasses of the specified `base_class`.
            `base_class` must be subclass of `BaseObject`.

        Returns
        -------
        dict[str, Any]
            Mapping of object attribute names that are objects inheritting from
            `base_class` whose name does not contain the string "__".

        Raises
        ------
        TypeError
            If `base_class` is not None or a class that subclasses BaseObject.
        """
        if base_class is None:
            base_class = BaseObject
        if not (inspect.isclass(base_class) and issubclass(base_class, BaseObject)):
            msg = "`base_class` must be None or a class that subclasses "
            msg += f"BaseObject, but found {type(base_class)}"
            raise TypeError(msg)

        # retrieve parameter names to exclude them later
        param_names = self._get_param_names()

        # retrieve all attributes that are BaseObject descendants
        attrs = [attr for attr in dir(self) if "__" not in attr]
        cls_attrs = list(dir(type(self)))
        self_attrs = set(attrs).difference(cls_attrs).difference(param_names)

        comp_dict = {x: getattr(self, x) for x in self_attrs}
        comp_dict = {x: y for (x, y) in comp_dict.items() if isinstance(y, base_class)}

        return comp_dict

    def __repr__(self, n_char_max: int = 700) -> str:
        """Represent class as string.

        This follows the scikit-learn implementation for the string representation
        of parameterized objects.

        Parameters
        ----------
        n_char_max : int
            Maximum (approximate) number of non-blank characters to render. This
            can be useful in testing.

        Returns
        -------
        str
            String representation of the object.
        """
        from predictably._core._pprint._pprint import _BaseObjectPrettyPrinter

        n_max_elements_to_show = 30  # number of elements to show in sequences
        # use ellipsis for sequences with a lot of elements
        pp = _BaseObjectPrettyPrinter(
            compact=True,
            indent=1,
            indent_at_name=True,
            n_max_elements_to_show=n_max_elements_to_show,
            changed_only=self._get_config()["print_changed_only"],
        )  # type: ignore

        repr_ = pp.pformat(self)

        # Use bruteforce ellipsis when there are a lot of non-blank characters
        n_nonblank = len("".join(repr_.split()))
        if n_nonblank > n_char_max:
            lim = n_char_max // 2  # apprx number of chars to keep on both ends
            regex = r"^(\s*\S){%d}" % lim
            # The regex '^(\s*\S){%d}' matches from the start of the string
            # until the nth non-blank character:
            # - ^ matches the start of string
            # - (pattern){n} matches n repetitions of pattern
            # - \s*\S matches a non-blank char following zero or more blanks
            left_match = re.match(regex, repr_)
            right_match = re.match(regex, repr_[::-1])
            left_lim = left_match.end() if left_match is not None else 0
            right_lim = right_match.end() if right_match is not None else 0

            if "\n" in repr_[left_lim:-right_lim]:
                # The left side and right side aren't on the same line.
                # To avoid weird cuts, e.g.:
                # categoric...ore',
                # we need to start the right side with an appropriate newline
                # character so that it renders properly as:
                # categoric...
                # handle_unknown='ignore',
                # so we add [^\n]*\n which matches until the next \n
                regex += r"[^\n]*\n"
                right_match = re.match(regex, repr_[::-1])
                right_lim = right_match.end() if right_match is not None else 0

            ellipsis = "..."
            if left_lim + len(ellipsis) < len(repr_) - right_lim:
                # Only add ellipsis if it results in a shorter repr
                repr_ = repr_[:left_lim] + "..." + repr_[-right_lim:]

        return repr_

    @property
    def _repr_html_(self) -> Callable[[], str]:
        """HTML representation of BaseObject.

        This is redundant with the logic of `_repr_mimebundle_`. The latter
        should be favorted in the long term, `_repr_html_` is only
        implemented for consumers who do not interpret `_repr_mimbundle_`.

        Returns
        -------
        Callable
            The inner html representation of the class.
        """
        if self._get_config()["display"] != "diagram":
            raise AttributeError(
                "_repr_html_ is only defined when the "
                "`display` configuration option is set to 'diagram'."
            )
        return self._repr_html_inner

    def _repr_html_inner(self) -> str:
        """Return HTML representation of class.

        This function is returned by the @property `_repr_html_` to make
        `hasattr(BaseObject, "_repr_html_") return `True` or `False` depending
        on `self.get_config()["display"]`.

        Returns
        -------
        str
            String representation of the object.
        """
        return _object_html_repr(self)

    def _repr_mimebundle_(self, **kwargs: Any) -> dict[str, Any]:
        """Mime bundle used by jupyter kernels to display instances of BaseObject.

        Captures the standard string representation and based on configuration
        the html "block" representation of the class.

        Parameters
        ----------
        **kwargs : Any
            The keyword arguments to pass.

        Returns
        -------
        dict[str, Any]
            Dictionary containing the string and html ("block") representation of the
            class.
        """
        output = {"text/plain": repr(self)}
        if self._get_config()["display"] == "diagram":
            output["text/html"] = _object_html_repr(self)
        return output


@attrs.define(kw_only=False, slots=False, repr=False)
class BaseEstimator(BaseObject):
    """Base class for estimators with scikit-learn and sktime design patterns.

    Extends BaseObject to include basic functionality for fittable estimators.
    """

    _is_fitted: bool = attrs.field(
        init=False, repr=False, alias="_is_fitted", default=False, eq=False
    )

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
