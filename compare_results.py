#!/usr/bin/env python3

from functools import lru_cache
from itertools import groupby
from lxml import etree
from glob import glob
from Levenshtein import distance
import re

@lru_cache(maxsize=100)
def etree_from_file(filename):
    return etree.parse(filename)

def elements(filename, xpath):
    return etree_from_file(filename).xpath(xpath,
        namespaces={'t':'http://www.tei-c.org/ns/1.0'})

def element_text(filename, xpath):
    els = elements(filename, xpath)
    if not els: return None
    return els[0].text

def construct_name(persname_element):
    return ' '.join(part.text for part in persname_element)

def metadata_from_xml(filename):
    return dict(
        title=element_text(filename, '//t:titleStmt/t:title'),
        authors=[construct_name(el) for el in elements(filename,
                    '//t:sourceDesc//t:author/t:persName')]
    )

fn_id_re = re.compile('.*/([0-9]{9})\.tei\.xml')
def record_id_from_filename(filename):
    m = fn_id_re.match(filename)
    if m: return m.group(1)
    return filename

def metadata_from_dir(dirname):
    return dict((record_id_from_filename(fn), metadata_from_xml(fn))
            for fn in glob('{}/*.xml'.format(dirname)))

seq_rules = [
    (re.compile(r'^([0-9]{9}) 245.. L .*\$\$a([^$]+).*\$\$b([^$]+)'),
        lambda m: [(m.group(1), 'title', m.group(2)),
                    (m.group(1), 'title', m.group(3))]),
    (re.compile(r'^([0-9]{9}) 245.. L .*\$\$a([^$]+)'),
        lambda m: [(m.group(1), 'title', m.group(2))]),
    (re.compile(r'^([0-9]{9}) 1[10]0.. L .*\$\$a([^$,]+), ([^$,]+)'),
        lambda m: [(m.group(1), 'authors', m.group(3) + ' ' + m.group(2))]),
    (re.compile(r'^([0-9]{9}) 1[10]0.. L .*\$\$a([^$]+)'),
        lambda m: [(m.group(1), 'authors', m.group(2))]),
]

def parse_seq_line(line):
    for pattern, handler in seq_rules:
        match = pattern.match(line)
        if match: return handler(match)
    return []

def metadata_from_triplets(triplets):
    res = {}
    for _, field, value in triplets:
        res.setdefault(field, []).append(value)
    res['title'] = ' '.join(res.get('title', []))
    return res

def metadata_from_seq(filename):
    keyfn = lambda t: t[0]
    triplets = sorted([triplet for line in open(filename)
                            for triplet in parse_seq_line(line)], key=keyfn)
    return dict((id, metadata_from_triplets(tr))
            for id, tr in groupby(triplets, keyfn))

def md_evaluate(rec1, rec2):
    title1 = (rec1.get('title', '') or '').lower()
    title2 = (rec2.get('title', '') or '').lower()
    dist = distance(title1, title2)
    return (dist/max(1, len(title1), len(title2)), title1, title2)

def compare_metadata(md1, md2):
    doc_ids = set(md1.keys()).union(md2.keys())
    md_pairs = [(md1.get(id, {}), md2.get(id, {})) for id in doc_ids]
    return sorted(md_evaluate(rec1, rec2) for rec1, rec2 in md_pairs)

def load_and_compare(input_dir):
    seqfile = glob('{}/*.seq'.format(input_dir))[0]
    teidir = '{}/tei'.format(input_dir)
    return compare_metadata(metadata_from_seq(seqfile),
                            metadata_from_dir(teidir))

def categorise_evaluation(eval):
    score = eval[0]
    if score < 0.13: return 'correct'
    if score < 0.65: return 'has changes'
    if score < 0.99: return 'incorrect'
    return 'missing'

if __name__ == '__main__':
    import sys
    diffs = load_and_compare(sys.argv[1])
    for l in diffs: print(l)
    for cat, inst in groupby(diffs, categorise_evaluation):
        print(cat, ':', len(list(inst)), 'of', len(diffs))

