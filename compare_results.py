#!/usr/bin/env python3

from functools import lru_cache
from itertools import groupby
from lxml import etree
from glob import glob
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
    (re.compile(r'^([0-9]{9}) 24[56].. L .*\$\$a([^$]+).*\$\$b([^$]+)'),
        lambda m: [(m.group(1), 'title', m.group(2)),
                    (m.group(1), 'title', m.group(3))]),
    (re.compile(r'^([0-9]{9}) 24[56].. L .*\$\$a([^$]+)'),
        lambda m: [(m.group(1), 'title', m.group(2))]),
    (re.compile(r'^([0-9]{9}) [17]10.. L .*\$\$a([^$]+)'),
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

