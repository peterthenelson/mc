"""Representation for Middle Chinese syllables."""

import re

_BAXTER_INITIALS = sorted([
    'p', 'ph', 'b', 'm',
    't', 'th', 'd', 'n',
    'k', 'kh', 'g', 'ng',
    'x', 'h', 'y', "'",
    'ts', 'tsh', 'dz', 's', 'z',
    'tr', 'trh', 'dr', 'nr',
    'tsr', 'tsrh', 'dzr', 'sr', 'zr',
    'tsy', 'tsyh', 'dzy', 'sy', 'zy',
    'l', 'ny'], key=len, reverse=True)
_BAXTER_VOICED_OBSTRUENTS = [
    'b', 'd', 'g', 'h', 'dz', 'z', 'dr', 'dzr', 'zr', 'dzy', 'zy']
_BAXTER_SONORANTS = ['m', 'n', 'ng', 'y', 'nr', 'l', 'ny']
_BAXTER_FINALS = [] # TODO

def _split_baxter(baxter):
  baxter = baxter.strip()
  tone = 'ping'
  if baxter[-1] == 'X':
    baxter = baxter[:-1]
    tone = 'shang'
  elif baxter[-1] == 'H':
    baxter = baxter[:-1]
    tone = 'qu'
  elif baxter[-1] in ['p', 't', 'k']:
    tone = 'ru'
  for init in _BAXTER_INITIALS:
    if baxter.startswith(init):
      final = baxter[len(init):]
      #if final not in _BAXTER_FINALS:
      #  raise ValueError('Invalid final: %s' % final)
      return init, final, tone
  raise ValueError('Syllable %s does not start with a valid initial' % baxter)

class MiddleChineseSyllable(object):
  """A syllable in Middle Chinese."""

  def __init__(self, baxter):
    """Create a Middle Chinese syllable from Baxter's notation."""
    self._bax = baxter
    self._bax_init, self._bax_final, self._tone = _split_baxter(baxter)
    self._open = True
    if (self._bax_final.startswith('w') or self._bax_final.startswith('jw') or
        re.match(r'^(j?w|jo[mp]$|ju[nt]$)', self._bax_final)):
      self._open = False
    self._sonorant = self._bax_init in _BAXTER_SONORANTS
    self._voiced = (self._sonorant or
                    (self._bax_init in _BAXTER_VOICED_OBSTRUENTS))

  @property
  def baxter_initial(self):
    """Get the initial as represented in Baxter's notation."""
    return self._bax_init

  @property
  def baxter_final(self):
    """Get the final as represented in Baxter's notation."""
    return self._bax_final

  @property
  def baxter(self):
    """Get the syllable as represented in Baxter's notation."""
    return self._bax

  @property
  def tone(self):
    """Get the tone (ping, shang, qu, or ru)."""
    return self._tone

  @property
  def voiced(self):
    """Does this syllable have a voiced initial?"""
    return self._voiced

  @property
  def sonorant(self):
    """Does this syllable start with a sonorant?"""
    return self._sonorant

  @property
  def open(self):
    """Is this syllable "open" (in the Guangyun sense)?"""
    return self._open

