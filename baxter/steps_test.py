# -*- coding: utf-8 -*-
"""Tests for steps module."""

import unittest

from . import mc
from . import steps

class StepsTest(unittest.TestCase):
  """Tests some specific input and output pairs."""

  def test_smoketest(self):
    """Example given by Brian along w/initial steps."""
    self.assertEqual(steps.expected_pinyin(mc.MiddleChineseSyllable('trhik')),
                     'chi4')

  def test_v_spelling(self):
    """'v' (i.e., 'ü') is spelled 'u' after 'j', 'q', and 'x'."""
    self.assertEqual(steps.expected_pinyin(mc.MiddleChineseSyllable('khjuX')),
                     'qu3')
