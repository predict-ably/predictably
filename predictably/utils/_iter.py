#!/usr/bin/env python3 -u
# copyright: predict-ably, BSD-3-Clause License (see LICENSE file)
# Elements of predictably.utils reuse code developed for skbase. These elements
# are copyrighted by the skbase developers, BSD-3-Clause License. For
# conditions see https://github.com/sktime/skbase/blob/main/LICENSE
"""Utility functionality for working with sequences."""  # numpydoc ignore=ES01
import collections
import re
from typing import Any, List, Optional, Sequence, Union

__author__: List[str] = ["RNKuhns"]
__all__: List[str] = [
    "_format_seq_to_str",
    "_remove_single",
    "_remove_type_text",
    "_scalar_to_seq",
]


def _remove_single(x: Sequence[Any]) -> Any:
    """Remove tuple wrapping from singleton.

    If the input has length 1, then the single value is extracted from the input.
    Otherwise, the input is returned unchanged.

    Parameters
    ----------
    x : Sequence
        The sequence to remove a singleton value from.

    Returns
    -------
    Any
        The singleton value of x if x[0] is a singleton, otherwise x.

    Examples
    --------
    >>> from predictably.utils._iter import _remove_single
    >>> _remove_single([1])
    1
    >>> _remove_single([1, 2, 3])
    [1, 2, 3]
    """
    if len(x) == 1:
        return x[0]
    else:
        return x


def _scalar_to_seq(scalar: Any, sequence_type: Optional[type] = None) -> Sequence[Any]:
    """Convert a scalar input to a sequence.

    If the input is already a sequence it is returned unchanged. Unlike standard
    Python, a string is treated as a scalar instead of a sequence.

    Parameters
    ----------
    scalar : Any
        A scalar input to be converted to a sequence.
    sequence_type : type, default=None
        A sequence type (e.g., list, tuple) that is used to set the return type. This
        is ignored if `scalar` is already a sequence other than a str (which is
        treated like a scalar type for this function instead of sequence of
        characters).

        - If None, then the returned sequence will be a tuple containing a single
          scalar element.
        - If `sequence_type` is a valid sequence type then the returned
          sequence will be a sequence of that type containing the single scalar
          value.

    Returns
    -------
    Sequence
        A sequence of the specified `sequence_type` that contains just the single
        scalar value.

    Examples
    --------
    >>> from predictably.utils._iter import _scalar_to_seq
    >>> _scalar_to_seq(7)
    (7,)
    >>> _scalar_to_seq("some_str")
    ('some_str',)
    >>> _scalar_to_seq("some_str", sequence_type=list)
    ['some_str']
    >>> _scalar_to_seq((1, 2))
    (1, 2)
    """
    # We'll treat str like regular scalar and not a sequence
    if isinstance(scalar, collections.abc.Sequence) and not isinstance(scalar, str):
        return scalar
    elif sequence_type is None:
        return (scalar,)
    elif (
        issubclass(sequence_type, collections.abc.Sequence)
        and sequence_type != Sequence
    ):
        # Note calling (scalar,) is done to avoid str unpacking
        return sequence_type((scalar,))  # type: ignore
    else:
        raise ValueError(
            "`sequence_type` must be a subclass of collections.abc.Sequence."
        )


def _remove_type_text(input_: Union[str, type]) -> str:
    """Remove <class > wrapper from printed type str.

    If the input doesn't have the wrapper <class > text it is returned unchanged.

    Parameters
    ----------
    input_ : str | type
        The input to remove <class > wrapper when printing class.

    Returns
    -------
    str
        The text version of the class without the <class > wrapper.

    Examples
    --------
    >>> from predictably.utils._iter import _remove_type_text
    >>> _remove_type_text(int)
    'int'
    >>> _remove_type_text("<class 'int'>")
    'int'
    >>> _remove_type_text("int")
    'int'
    >>> _remove_type_text("ForwardRef('pd.DataFrame')")
    'pd.DataFrame'
    """
    if not isinstance(input_, str):
        input_ = str(input_)

    m = re.match("^<class '(.*)'>$", input_)

    if m:
        return m[1]

    else:
        m_forward_ref = re.match(r"^ForwardRef\('(.*)'\)", input_)
        if m_forward_ref:
            return m_forward_ref[1]
        else:
            return input_


def _format_seq_to_str(
    seq: Union[Any, Sequence[Any]],
    sep: str = ", ",
    last_sep: Optional[str] = None,
    remove_type_text: bool = False,
) -> str:
    """Format a sequence to a string of delimited elements.

    This is useful to format sequences into a pretty printing format for
    creating error messages or warnings.

    Parameters
    ----------
    seq : Any | Sequence[Any]
        The input sequence to convert to a str of the elements separated by `sep`.
    sep : str
        The separator to use when creating the str output.
    last_sep : str, default=None
        The separator to use prior to last element.

        - If None, then `sep` is used. So (7, 9, 11) return "7", "9", "11" for
          ``sep=", "``.
        - If last_sep is a str, then it is used prior to last element. So
          (7, 9, 11) would be "7", "9" and "11" if ``last_sep="and"``.

    remove_type_text : bool, default=False
        Whether to remove the <class > text wrapping the class type name, when
        formatting types.

        - If True, then input sequence [list, tuple] returns "list, tuple"
        - If False, then input sequence [list, tuple] returns
          "<class 'list'>, <class 'tuple'>".

    Returns
    -------
    str
        The sequence of inputs converted to a string. For example, if `seq`
        is (7, 9, "cart") and ``last_sep is None`` then the output is "7", "9", "cart".

    Examples
    --------
    >>> from predictably.utils._iter import _format_seq_to_str
    >>> seq = [1, 2, 3, 4]
    >>> _format_seq_to_str(seq)
    '1, 2, 3, 4'
    >>> _format_seq_to_str(seq, last_sep="and")
    '1, 2, 3 and 4'
    >>> _format_seq_to_str(seq, last_sep="or")
    '1, 2, 3 or 4'
    """
    if isinstance(seq, str):
        return seq
    # Allow casting of scalars to strings
    elif isinstance(seq, (int, float, bool)):
        return str(seq)
    elif isinstance(seq, type):
        if remove_type_text:
            return _remove_type_text(str(seq))
        else:
            return str(seq)
    elif not isinstance(seq, collections.abc.Sequence):
        msg = "`seq` must be a sequence or scalar str, int, float, bool or type."
        msg += f"\nBut found {type(seq)}."
        raise TypeError(msg)

    seq_str = [str(e) for e in seq]
    if remove_type_text:
        seq_str = [_remove_type_text(s) for s in seq_str]

    if last_sep is None:
        output_str = sep.join(seq_str)
    else:
        if len(seq_str) == 1:
            output_str = _remove_single(seq_str)
        else:
            output_str = sep.join(e for e in seq_str[:-1])
            output_str = output_str + f" {last_sep} " + seq_str[-1]

    return output_str
