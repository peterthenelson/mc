# -*- coding: utf-8 -*-
"""Converts Baxter's notation to predicted Pinyin."""

import os.path
import sys

import mc

def read_records(fname):
  """Read records from Baxter's 7-column CSV."""
  with open(fname) as f:
    for i, line in enumerate(f):
      # Skip header
      if not i:
        continue
      line = line.strip()
      if not line:
        continue
      r = line.split(',')
      if len(r) != 7:
        raise ValueError('Expected 7 fields, got %d on line %d: %s' % (
            len(r), i, line))
      if not (r[0].strip() and r[1].strip() and r[2].strip()):
        sys.stderr.write(
            'Missing required field in line %d; skipping: %s\n' % (i, line))
        continue
      # TODO: Put the other fields somewhere.
      yield {'hanzi': r[0], 'pinyin': r[1], 'baxter': r[2]}

def parse_records(raw_records):
  """Parse the sequence of raw records."""
  for r in raw_records:
    try:
      yield r['hanzi'], r['pinyin'], mc.MiddleChineseSyllable(r['baxter'])
    except ValueError as e:
      sys.stderr.write('%s\n' % e)
      continue

def expected_msm_tone(syl):
  """Get the expected tone in MSM."""
  tone = '?'
  if syl.tone == 'ping':
    tone = '1'
    if syl.voiced:
      tone = '2'
  elif syl.tone == 'shang':
    tone = '3'
    if syl.voiced and not syl.sonorant:
      tone = '4'
  elif syl.tone == 'qu':
    tone = '4'
  elif syl.voiced:
    tone = '2'
    if syl.sonorant:
      tone = '4'
  return tone

def _init_r1(bax_init):
  """Round 1 initial from the baxter initial."""
  return {
      'p': 'b', 'ph': 'p', 'b': 'Vp', 'm': 'vm',
      't': 'd', 'th': 't', 'd': 'Vt', 'n': 'vn',
      'k': 'g', 'kh': 'k', 'g': 'Vk', 'ng': 'v0',
      'x': 'h', 'h': 'Vh', 'y': 'v0', "'": '0',
      'ts': 'z', 'tsh': 'c', 'dz': 'Vc', 's': 's', 'z': 'Vs',
      'tr': 'zh', 'trh': 'ch', 'dr': 'Vch', 'nr': 'vn',
      'tsr': 'zh', 'tsrh': 'ch', 'dzr': 'Vch', 'sr': 'sh', 'zr': 'Vsh',
      'tsy': 'zh', 'tsyh': 'ch', 'dzy': 'Vch', 'sy': 'sh', 'zy': 'Vsh',
      'l': 'l', 'ny': 'r'}[bax_init]

def _tone_r1(bax_tone):
  """Round 1 tone from the baxter tone."""
  return {'ping': '1', 'shang': '2', 'qu': '3', 'ru': '4'}[bax_tone]

def _final_r1(bax_init, bax_final):
  """Round 1 final from the baxter final."""
  final_r1 = bax_final
  final_r1 = final_r1[:-1] + {'p': 'm', 't': 'n', 'k': 'ng'}.get(
      final_r1[-1], final_r1[-1])
  if 'y' in bax_init and not final_r1.startswith('j'):
    final_r1 = 'j' + final_r1
  return final_r1

def _division(final_r1):
  division = 1
  if 'ae' in final_r1 or 'ea' in final_r1:
    division = 2
  elif final_r1[0] in 'ji' or final_r1.startswith('wi'):
    division = 3
  elif final_r1[0] == 'e' or final_r1.startswith('we'):
    division = 4
  return division

def _remove_f(init_r1, final_r1):
  """Remove f's."""
  if final_r1 in ['jowng', 'juwng', 'j+j', 'joj', 'ju',
                  'jon', 'jun', 'jang', 'juw']:
    if init_r1 in ['b', 'p']:
      init_r1 = 'f'
    elif init_r1 == 'Vp':
      init_r1 = 'Vf'
    elif init_r1 == 'vm' and final_r1 not in ['jowng', 'juwng']:
      init_r1 = 'vw'
  return init_r1

_ROUND_1_SIMPLIFICATIONS = (
    (('owng', 'uwng', 'jowng', 'juwng'), 'ong'),
    (('aewng', 'ang', 'jang'), 'ang'),
    (('aeng', 'eang', 'jaeng', 'jieng', 'jeng', 'eng', 'ong', 'ing', 'jing'), 'eng'),
    (('an', 'aen', 'ean', 'jaen', 'jen', 'jien', 'jon', 'en'), 'an'),
    (('on', 'in', 'jin', 'j+n', 'jun'), 'en'),
    (('je', 'jie', 'ij', 'jij', 'i', 'ji', 'j+j'), 'i'),
    (('u', 'jo', 'ju'), 'u'),
    (('oj', 'aj', 'eaj', 'ea', 'aej', 'jej', 'jiej', 'joj', 'ej'), 'ai'),
    (('a', 'ja'), 'o'),
    (('ae', 'jae'), 'a'),
    (('aw', 'aew', 'jew', 'jiew', 'ew'), 'ao'),
    (('uw', 'juw', 'jiw'), 'ou'))

def _simplify_final_r1(final_r1, bax):
  """Simplify the round 1 finals."""
  for possibilities, output in _ROUND_1_SIMPLIFICATIONS:
    if final_r1 in possibilities:
      return output
  raise ValueError('Unexpected final: %s (from %s)' % (final_r1, bax))

def _tone_r2(tone_r1, init_r1):
  """Get second round tone."""
  tone_r2 = tone_r1
  if tone_r1 == '1' and init_r1[0] not in 'vV':
    tone_r2 = '2'
  elif tone_r1 == '2':
    if init_r1[0] == 'V':
      tone_r2 = '4'
    else:
      tone_r2 = '3'
  elif tone_r1 == '4' and init_r1[0] == 'V':
    tone_r2 = '2'
  return tone_r2

def _init_r2(init_r1, tone_r2):
  """Get second round initial."""
  init_r2 = init_r1
  if init_r1[0] == 'V':
    if tone_r2 in ['2', '3', '4']:
      init_r2 = {'p': 'b', 't': 'd', 'k': 'g', 'h': 'h', 'f': 'f',
                 'c': 'z', 's': 's', 'ch': 'zh', 'sh': 'sh'}[init_r1[1:]]
    else:
      assert tone_r2 == '1'
      init_r2 = init_r1[1:]
  elif init_r1[0] == 'v':
    init_r2 = init_r1[1:]
  if init_r2 in ['w', '0']:
    init_r2 = ''
  return init_r2

def step_based_conversion(syl):
  """Blindly following steps to convert to pinyin."""
  # steps 1, 4, and 6 occur in the constructor.
  # step 2 maps initials to round-1 initials.
  init_r1 = _init_r1(syl.baxter_initial)
  # step 3 maps tones to round-1 tones (and changes ru final stops).
  tone_r1 = _tone_r1(syl.tone)
  # step 5 moves palatal information to final.
  final_r1 = _final_r1(syl.baxter_initial, syl.baxter_final)
  # step 7 determines division
  # TODO Move division into the MiddleChineseSyllable class.
  division = _division(final_r1)
  # step 8 removes w's in closed syllables.
  if not syl.open:
    final_r1 = final_r1.replace('w', '')
  # step 9 changes -m to -n.
  if final_r1[-1] == 'm':
    final_r1 = final_r1[:-1] + 'n'
  # step 10 makes f appear.
  init_r1 = _remove_f(init_r1, final_r1)
  # step 11 simplifies the round-1 finals.
  final_r1 = _simplify_final_r1(final_r1, syl.baxter)
  # step 12 changes Vh to v0 in division 3.
  if init_r1 == 'Vh' and division == 3:
    init_r1 = 'v0'
  # step 13 calculates round-2 tones.
  tone_r2 = _tone_r2(tone_r1, init_r1)
  #if self.expected_msm_tone() not in ['?', tone_r2]:
  #  sys.stderr.write('Tone mismatch for %s; tone_r2 = %s, expected = %s\n' % (
  #      syl.bax, tone_r2, self.expected_msm_tone()))
  # step 14 calculates round-2 initials.
  init_r2 = _init_r2(init_r1, tone_r2)
  # TODO steps until 20.
  _ = init_r2
  return ''

def expected_pinyin(syl):
  """Get the expected reflex in MSM, as represented in Pinyin."""
  return step_based_conversion(syl) + expected_msm_tone(syl) # TODO

def main():
  """Run full pipeline."""
  dirname = os.path.dirname(__file__)
  tone_counts = {}
  matches, total = 0, 0
  for r in parse_records(read_records(os.path.join(dirname, 'data/mc1.csv'))):
    _, py, syl = r
    # Exercise this incomplete code.
    _ = expected_pinyin(syl)
    if py[-1] not in '1234':
      continue
    expected, actual = expected_msm_tone(syl), py[-1]
    counts = tone_counts.setdefault(expected, {})
    counts[actual] = counts.get(actual, 0) + 1
    matches += int(expected == actual)
    total += 1
  print tone_counts
  print 100 * float(matches)/total

if __name__ == '__main__':
  main()
