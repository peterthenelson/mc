# -*- coding: utf-8 -*-
"""Converts Baxter's notation to predicted Pinyin.

python -m baxter.mc2pinyin -o /tmp/mismatches.csv
"""

import argparse
import os.path
import sys

from . import mc
from . import steps

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
      try:
        # TODO: Put the other fields somewhere.
        yield {'hanzi': r[0], 'pinyin': r[1].replace('ü', 'v'),
               'baxter': mc.MiddleChineseSyllable(r[2])}
      except ValueError as e:
        sys.stderr.write('%s\n' % e)
        continue

def summarize(msg, num, denom):
  """Summarize a ratio."""
  print '%s: %.2f (%d/%d)' % (msg, 100.0*float(num)/denom, num, denom)

def pipeline(input_file, output_file):
  """Read the MC database and try to reconstruct MSM pronunciations."""
  tone_matches1, tone_matches2, py_matches, total = 0, 0, 0, 0
  with open(output_file, 'w') as mismatches:
    for r in read_records(input_file):
      hz, py, syl = r['hanzi'], r['pinyin'], r['baxter']
      expected_pinyin = steps.expected_pinyin(syl)
      tone = py[-1]
      if tone not in '1234':
        tone = '?'
      expected_tone1 = expected_pinyin[-1]
      expected_tone2 = steps.expected_msm_tone(syl)
      if py == expected_pinyin:
        py_matches += 1
      else:
        mismatches.write('%s,%s,%s,%s,%s\n' % (hz, syl.baxter, py, expected_pinyin, expected_tone2))
      if expected_tone1 == tone:
        tone_matches1 += 1
      if (expected_tone2 == tone or
          (expected_tone2 == '?' and tone == '4')):
        tone_matches2 += 1
      total += 1
  summarize('Pinyin matches', py_matches, total)
  summarize('Tone matches #1', tone_matches1, total)
  summarize('Tone matches #2', tone_matches2, total)

def main():
  """Run full pipeline."""
  dirname = os.path.dirname(__file__)
  parser = argparse.ArgumentParser(
      description=('Attempts to reconstruct MSM pronunciation from Baxter\'s '
                   'MC data.'))
  parser.add_argument('-o', '--output_file', dest='output_file', type=str,
                      required=True, help='File to dump mismatches to.')
  args = parser.parse_args()
  pipeline(os.path.join(dirname, 'data/mc1.csv'), args.output_file)

if __name__ == '__main__':
  main()
