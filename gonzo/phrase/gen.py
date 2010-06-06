#!/usr/bin/env python
from __future__ import print_function

import fileinput
import os.path
import sys

def word_to_json(model, line):
    value = line.strip()
    if value:
        return '{"model":"%s","pk":"%s","fields":{}}' % (model, value)
    else:
        return ''

def phrase_to_json(model, line):
    try:
        (weight,value) = line.split(':',1)
        return '{"model":"%s","pk":"%s","fields":{"weight":%d}}' % (model, value.strip(), int(weight))
    except ValueError, e:
        print(e,file=sys.stderr)
        return ''
    return ''

def process_file(model, file, mapper):
    """Adds a model value, one per line."""
    try:
        return map(lambda line: mapper(model,line), open(file))
    except IOError,e:
        print('Unable to open: ' + file, file=sys.stderr)
        print(e, file=sys.stderr)
        return []

FILES=(
    ("phrase.adjective1", "adjective1.txt", word_to_json),
    ("phrase.adjective2", "adjective2.txt", word_to_json),
    ("phrase.noun1",      "noun1.txt",      word_to_json),
    ("phrase.phrase",     "phrase.txt",     phrase_to_json),
)

def main():
    """This takes a directory that includes raw data."""
    if len(sys.argv) > 1:
        dir = sys.argv[1]
    else:
        dir = 'raw_data'

    results = []
    for f in FILES:
        results.extend(process_file(f[0], os.path.join(dir, f[1]), f[2]))

    print('[\n', ',\n'.join(results), '\n]', sep='')

if __name__ == "__main__":
    main()
