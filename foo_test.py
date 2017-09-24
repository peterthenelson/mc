"""Tests for foo."""

import foo
import unittest

class FooTest(unittest.TestCase):
  """Tests for foo module."""

  def test_foo(self):
    self.assertTrue(foo.fooable('foo'))
    self.assertTrue(foo.fooable('foooooooo'))
    self.assertFalse(foo.fooable('foob'))
