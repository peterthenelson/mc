# -*- coding: utf-8 -*-
"""Brian Lawrence's steps for converting Baxter's notation to pinyin.

This will serve as a reference implementation when making other converters.
"""

import logging

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

def _medial(division, open_, init_r2):
  """Find the medial."""
  if division == 1:
    med_1 = ''
  elif division == 2:
    if init_r2 in ('g', 'k', 'h'):
      med_1 = 'i'
    else:
      med_1 = ''
  else:
    med_1 = 'i'
  if init_r2 in ('f', 'Vf', 'vw'):
    med_1 = ''
  if open_:
    med_2 = ''
  else:
    med_2 = 'u'
  if init_r2 == 'vw':
    med_2 = 'u'
  med = med_1 + med_2
  if med == 'iu':
    med = 'v'
  return med

def _final_r2(medial, final_r1, division, tone_r1):
  """Find the round-2 final."""
  final_r2 = medial + final_r1
  final_r2 = {'vang': 'wang', 'ieng': 'ing', 'ueng': 'ong', 'veng': 'iong',
              'ien': 'in', 'uen': 'un', 'ven': 'vn', 'ii': 'i', 'vi': 'ui',
              'iu': 'v', 'io': 'ia', 'ia': 'ie', 'iou': 'iu'}.get(final_r2, final_r2)
  if final_r2 == 'iai':
    if division == 2:
      final_r2 = 'ie'
    else:
      final_r2 = 'i'
  if tone_r1 == '4':
    final_r2 = {'an': 'a', 'ian': 'ie', 'uan': 'o', 'van': 've', 'en': 'e',
                'in': 'i', 'un': 'u', 'vn': 've', 'ang': 'o', 'iang': 've',
                'uang': 'uo', 'eng': 'e', 'ing': 'i', 'ong': 'u',
                'iong': 'v'}.get(final_r2, final_r2)
  return final_r2

def _substituted_final_r2(init_r2, final_r2):
  """Cleanups of the final."""
  if (init_r2 in ('zh', 'ch', 'sh', 'r') and final_r2.startswith('i') and
      final_r2 not in ('i', 'in', 'ing')):
    final_r2 = final_r2[1:]
  if init_r2 == '':
    final_r2 = {'ong': 'weng', 'un': 'wen', 'ui': 'wei', 'iu': 'you'}.get(final_r2, final_r2)
    if final_r2[:2] in ('ia', 'ie', 'io', 'iu'):
      final_r2 = 'y' + final_r2[1:]
    elif final_r2.startswith('i'):
      final_r2 = 'y' + final_r2
    elif final_r2 == 'u':
      final_r2 = 'wu'
    elif final_r2.startswith('u'):
      final_r2 = 'w' + final_r2[1:]
    elif final_r2.startswith('v'):
      final_r2 = 'yu' + final_r2[1:]
  if init_r2 in ('j', 'q', 'x', 'r') and final_r2.startswith('v'):
    final_r2 = 'u' + final_r2[1:]
  return final_r2

def expected_msm_syllable(syl):
  """Directly implementing steps in MC_to_mand.pdf."""
  logging.debug('baxter = %s', syl.baxter)
  # steps 1, 4, and 6 occur in the constructor of MiddleChineseSyllable.
  # step 2 maps initials to round-1 initials.
  init_r1 = _init_r1(syl.baxter_initial)
  logging.debug('init_r1 = %s', init_r1)
  # step 3 maps tones to round-1 tones (and changes ru final stops).
  tone_r1 = _tone_r1(syl.tone)
  logging.debug('tone_r1 = %s', tone_r1)
  # step 5 moves palatal information to final.
  final_r1 = _final_r1(syl.baxter_initial, syl.baxter_final)
  logging.debug('final_r1 = %s', final_r1)
  # step 7 determines division
  # TODO Move division into the MiddleChineseSyllable class.
  division = _division(final_r1)
  logging.debug('division = %s', division)
  # step 8 removes w's in closed syllables.
  if not syl.open:
    final_r1 = final_r1.replace('w', '')
  # step 9 changes -m to -n.
  if final_r1[-1] == 'm':
    final_r1 = final_r1[:-1] + 'n'
  logging.debug('final_r1 (after 8&9) = %s', final_r1)
  # step 10 makes f appear.
  init_r1 = _remove_f(init_r1, final_r1)
  logging.debug('init_r1 (after 10) = %s', init_r1)
  # step 11 simplifies the round-1 finals.
  final_r1 = _simplify_final_r1(final_r1, syl.baxter)
  logging.debug('final_r1 (after 11) = %s', final_r1)
  # step 12 changes Vh to v0 in division 3.
  if init_r1 == 'Vh' and division == 3:
    init_r1 = 'v0'
  logging.debug('init_r1 (after 12) = %s', init_r1)
  # step 13 calculates round-2 tones.
  tone_r2 = _tone_r2(tone_r1, init_r1)
  logging.debug('tone_r2 = %s', tone_r2)
  # step 14 calculates round-2 initials.
  init_r2 = _init_r2(init_r1, tone_r2)
  logging.debug('init_r2 = %s', init_r2)
  # step 15 finds medials.
  medial = _medial(division, syl.open, init_r2)
  logging.debug('medial = %s', medial)
  # step 16-17 creates the round-2 final.
  final_r2 = _final_r2(medial, final_r1, division, tone_r1)
  logging.debug('final_r2 = %s', final_r2)
  # step 18 palatalizes initials.
  if medial in ('i', 'v'):
    init_r2 = {'g': 'j', 'z': 'j', 'k': 'q', 'c': 'q', 'h': 'x', 's': 'x'}.get(init_r2, init_r2)
  logging.debug('init_r2 (after 18) = %s', init_r2)
  # step 19 does various cleanups of the final.
  final_r2 = _substituted_final_r2(init_r2, final_r2)
  logging.debug('final_r2 (after 19) = %s', final_r2)
  # step 20 puts it all together.
  return init_r2 + final_r2 + tone_r2

def expected_pinyin(syl):
  """Get the expected reflex in MSM, as represented in Pinyin."""
  tmp = expected_msm_syllable(syl)
  #assert tmp[-1] == expected_msm_tone(syl)
  return tmp
