#!/usr/bin/env python3

from lxml import etree

def attributes(el):
    for attr in el.keys(): yield '{}/{}'.format(el.tag, attr)

def elements(el):
    if (el.text or '').strip() or len(el): yield el.tag
    yield from attributes(el)
    for child in el: yield from elements(child)

def elements_from_files(filenames):
    for filename in filenames:
        for el in elements(etree.parse(filename).getroot()):
            yield (filename, el)

if __name__ == '__main__':
    import sys
    for fn, el in elements_from_files(sys.argv[1:]): print(fn, el)

