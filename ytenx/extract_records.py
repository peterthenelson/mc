# -*- coding: utf-8 -*-
"""Extracts numbered ytenx guangyun records from html pages."""

import argparse
import json
import os
import os.path
import re
from lxml import html

FILE_REGEX = r'(\d+).html$'

def get_record_id(fname):
  """Get the (numeric) record id from the filename."""
  m = re.match(FILE_REGEX, fname)
  if not m:
    raise ValueError(
        'Input directory file did not match %r: %s' % (FILE_REGEX, fname))
  return int(m.group(1))

def text(elem):
  """Extract all text from an element (and strip leading and trailing space)."""
  return ''.join(txt for txt in elem.xpath('.//text()')).strip()

class FieldSpec(object):
  """FieldSpec declaratively specified how to process a td into a field."""

  def __init__(self, header, store, func=None):
    """Initialize a FieldSpec."""
    self._header = header
    self._store = store
    self._func = func

  def _matches(self, td_header):
    if isinstance(self._header, basestring):
      return self._header == text(td_header)
    else:
      return self._header(td_header)

  def _process_and_store(self, td_value, record):
    if self._func:
      val = self._func(td_value)
    else:
      val = text(td_value)
    if self._store:
      record[self._store] = val

  def __repr__(self):
    return 'FieldSpec(%r, %r, %r)' % (self._header, self._store, self._func)

  def extract(self, td_header, td_value, record):
    """Extract the value for the field from the td element.

    Returns: True if the row was matched; False otherwise.
    """
    if self._matches(td_header):
      self._process_and_store(td_value, record)
      return True
    return False

def _apply_field_specs(specs, td_header, td_value, record):
  """Apply FieldSpecs until one matches, returning its index."""
  for i, s in enumerate(specs):
    if s.extract(td_header, td_value, record):
      return i
  return None

class TableSpec(object):
  """TableSpec declaratively specifies how to process a 2-column html table."""

  def __init__(self, field_specs, allow_missing=False, allow_extra=False):
    """Initialize a TableSpec."""
    self._field_specs = field_specs
    self._allow_missing = allow_missing
    self._allow_extra = allow_extra

  def extract(self, t, record):
    """Process a table into a record according to the specification."""
    unmatched, matched = list(self._field_specs), []
    for tr in t.xpath('./tr'):
      tds = tr.xpath('./td')
      if len(tds) != 2:
        raise ValueError(
            'Expected a two column table; got row with %d: %s' % (
                len(tds), text(tr)))
      td_header, td_value = tds
      i = _apply_field_specs(unmatched, td_header, td_value, record)
      if i is None:
        if self._allow_extra:
          continue
        raise ValueError('Row not matched by any FieldSpecs: %s' % text(tr))
      matched.append(unmatched.pop(i))
    if unmatched and not self._allow_missing:
      raise ValueError('FieldSpecs not matched by any rows: %r' % unmatched)

def open_or_closed(td):
  """Check whether it is open (kaikou) or closed (hekou)."""
  txt = text(td)
  if txt == u'開口':
    return True
  elif txt == u'合口':
    return False
  raise ValueError(u'Expected 開口 or 合口; got %s' % txt)

GY_TABLE = TableSpec(
    [FieldSpec(u'小韻', 'hanzi'),
     FieldSpec(u'序號', 'number', func=lambda td: int(text(td))),
     FieldSpec(u'反切', 'fanqie'),
     FieldSpec(u'聲母', 'initial'),
     FieldSpec(u'韻母', 'final_full'),
     FieldSpec(u'韻目', 'final'),
     FieldSpec(u'調', 'tone'),
     FieldSpec(u'等', 'grade'),
     FieldSpec(u'呼', 'open', func=open_or_closed),
     FieldSpec(u'韻系', 'row'),  # TODO Is this what it means?
     FieldSpec(u'韻攝', 'she'),
     FieldSpec(u'廣韻目次', 'section')])

def extract_records(input_dir, output_file):
  """Extracts guangyun records from a directory of ytenx html files."""
  print 'input_dir: %s, output_file: %s' % (input_dir, output_file)
  records = {}
  for fname in os.listdir(input_dir):
    print 'Processing file %s' % fname
    record = {'id': get_record_id(fname)}
    with open(os.path.join(input_dir, fname)) as f:
      tree = html.parse(f)
    tables = tree.xpath('//table')
    if len(tables) != 4:
      raise ValueError(
          'Expected 4 table elements in the html of %s, got %d' % (fname,
                                                                   len(tables)))
    gy_entry, romanization1, romanization2, containing_chars = tables
    GY_TABLE.extract(gy_entry, record)
    # TODO Other tables
    _, _, _ = romanization1, romanization2, containing_chars
    # TODO Post-processing/validation (id == number, section is consistent)
    records[record['id']] = record
  with open(output_file, 'w') as f:
    json.dump(records, f)
  print 'Done.'

def main():
  """Runs the pipeline with the given command line arguments."""
  parser = argparse.ArgumentParser(
      description='Extracts numbered ytenx guangyun records from html pages.')
  parser.add_argument('-i', '--input_dir', dest='input_dir', type=str,
                      required=True, help='Directory with numbered html files.')
  parser.add_argument('-o', '--output_file', dest='output_file', type=str,
                      required=True, help='File to dump json output to.')
  args = parser.parse_args()
  extract_records(args.input_dir, args.output_file)

if __name__ == '__main__':
  main()
