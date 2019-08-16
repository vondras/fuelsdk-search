# -*- coding: utf-8 -*-

import pytest
from fuelsdk_search.skeleton import fib

__author__ = "Clayton VonDras"
__copyright__ = "Clayton VonDras"
__license__ = "mit"


def test_fib():
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(7) == 13
    with pytest.raises(AssertionError):
        fib(-10)
