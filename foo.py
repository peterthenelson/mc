"""foos your bars."""

import re

def fooable(s):
  """Checks if s is fooable."""
  return re.match(r'foo+$', s)
