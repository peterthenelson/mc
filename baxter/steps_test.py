# -*- coding: utf-8 -*-
"""Tests for steps module.

NOTE: Errors can be debugged using test_util.DebugOn

from . import test_util

with test_util.DebugOn():
  statement_that_calls_logging_debug()
"""

import unittest

from . import mc
from . import steps

class StepsTest(unittest.TestCase):
  """Tests some specific input and output pairs."""

  def expect_pinyin(self, bax, py):
    """Assertion that the pinyin is successfully reconstructed."""
    actual = steps.expected_pinyin(mc.MiddleChineseSyllable(bax))
    if py != actual:
      self.fail('Expected pinyin for %r to be %r; got %r' % (
          bax, py, actual))

  def test_smoketest(self):
    """Example given by Brian along w/initial steps."""
    self.expect_pinyin('trhik', 'chi4')

  def test_v_spelling(self):
    """'v' (i.e., 'ü') is spelled 'u' after 'j', 'q', and 'x'."""
    self.expect_pinyin('khjuX', 'qu3')

  def test_r_with_v(self):
    """Test some syllables with r initials."""
    self.expect_pinyin('nyo', 'ru2')
    self.expect_pinyin('nyu', 'ru2')
    self.expect_pinyin('nywen', 'ruan2')
    self.expect_pinyin('nywin', 'run2')
