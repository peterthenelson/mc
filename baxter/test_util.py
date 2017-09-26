"""Utilities for testing."""

import functools
import logging

def debug(f):
  """Decorator that turns on debug logging for the duration of the function."""
  @functools.wraps(f)
  def decorated_function(*args, **kwargs):
    """Call f inside of DebugOn context manager."""
    with DebugOn():
      return f(*args, **kwargs)
  return decorated_function

class DebugOn(object):
  """Context handler to temporarily turn on debug logging."""

  def __init__(self):
    self._old_level = None

  def __enter__(self):
    self._old_level = logging.getLogger().level
    logging.getLogger().setLevel(logging.DEBUG)

  def __exit__(self, et, ev, tb):
    logging.getLogger().setLevel(self._old_level)
