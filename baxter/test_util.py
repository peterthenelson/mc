"""Utilities for testing."""

import logging

class DebugOn(object):
  """Context handler to temporarily turn on debug logging."""

  def __init__(self):
    self._old_level = None

  def __enter__(self):
    self._old_level = logging.getLogger().level
    logging.getLogger().setLevel(logging.DEBUG)

  def __exit__(self, et, ev, tb):
    logging.getLogger().setLevel(self._old_level)
