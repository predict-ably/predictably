#!/usr/bin/env python3 -u
# copyright: predictably developers, BSD-3-Clause License (see LICENSE file)
"""Predictably Exceptions.

Custom exceptions used to raise useful error messages in `predictably`.
"""


class ForwardRefError(TypeError):
    """Error to be raised when attempt to evaluate forward reference fails.

    Should be used when raising an error when trying to evaluate arguments of forward
    reference annotations within a function and it is not possible to do so.
    """

    pass
