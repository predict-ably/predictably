#!/usr/bin/env python3 -u
# copyright: predictably developers, BSD-3-Clause License (see LICENSE file)
# Elements of predictably.validate reuse code developed for skbase. These elements
# are copyrighted by the skbase developers, BSD-3-Clause License. For
# conditions see https://github.com/sktime/skbase/blob/main/LICENSE
"""Predictably Exceptions.

Custom exceptions used to raise useful error messages in `predictably`.
"""


class ForwardRefError(TypeError):
    """Error to be raised when attempt to evaluate forward reference fails.

    Should be used when raising an error when trying to evaluate arguments of forward
    reference annotations within a function and it is not possible to do so.
    """

    pass


class NotFittedError(ValueError, AttributeError):
    """Exception class to raise if estimator is used before fitting.

    This class inherits from both ValueError and AttributeError to help with
    exception handling.

    References
    ----------
    [1] scikit-learn's NotFittedError
    [2] sktime's NotFittedError
    [3] skbase's NotFittedError
    """
