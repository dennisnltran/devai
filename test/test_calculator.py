#!/usr/bin/env python3
"""
A test tool for calculator.
"""

from calculator import add, subtract

def test_add_positive_numbers():
    assert add(1, 2) == 3

def test_add_negative_numbers():
    assert add(-1, 1) == 0

def test_subtract_positive_numbers():
    assert subtract(2, 1) == 1

def test_subtract_negative_numbers():
    assert subtract(-1, -1) == 0