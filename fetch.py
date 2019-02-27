#!/usr/bin/env python3

# Script to fetch PDF documents based on MARC records.
#
# You need to provide the following command line arguments:
#
# 1. A .seq file of MARC records
# 2. A directory for storing the PDFs (will be created if it doesn't exist)
#
# The PDF files will be named <recid>.pdf where <recid> is the record ID. If
# the URL in the MARC 856 field leads to an HTML landing page (as is usually
# the case with document repositories like DSpace), the real PDF URL will be
# looked up from the meta element with the name "citation_pdf_url".

import sys
import os
import os.path

import requests
from bs4 import BeautifulSoup

if len(sys.argv) != 3:
    print("Usage: {} <seqfile> <outputdir>".format(sys.argv[0]))
    sys.exit(1)

INPUT=sys.argv[1]
OUTDIR=sys.argv[2]

def parse_html(recid, url, resp):
    soup = BeautifulSoup(resp.content, "lxml")
    meta = soup.find('meta', attrs={'name':'citation_pdf_url'})
    if meta:
        fetch(recid, meta['content'])
    else:
        print("no meta found")

def store_pdf(recid, url, resp):
    if not os.path.exists(OUTDIR):
        os.mkdir(OUTDIR)
    fname = os.path.join(OUTDIR, recid + ".pdf")
    with open(fname, 'wb') as fd:
        for chunk in resp.iter_content(chunk_size=1024):
            fd.write(chunk)

def fetch(recid, url):
    print("fetching {}: {}".format(recid, url))
    try:
        resp = requests.get(url, stream=True)
    except Exception as e:
        print("Got exception: {}, skipping".format(e))
        return
    if resp.status_code != requests.codes.ok:
        print("Got status {}, skipping".format(resp.status_code))
        return
    ctype = resp.headers['content-type']
    if 'text/html' in ctype:
        parse_html(recid, url, resp)
    elif 'application/pdf' in ctype:
        store_pdf(recid, url, resp)


def read_file(fn):
    with open(fn) as seq:
        for line in seq:
            line = line.strip()
            recid = line[:9]
            fld = line[10:13]
            if fld != '856':
                continue
            if 'Linkki verkkoaineistoon' not in line and 'Yhteenveto-osa' not in line and 'Digitoitu julkaisu' not in line:
                continue
            subfields = {sf[0]: sf[1:] for sf in line.split('$$')[1:]}
            if 'u' not in subfields:
                continue
            url = subfields['u'].split()[0]
            if not (url.startswith('http://') or url.startswith('https://')):
                continue
            if os.path.exists(os.path.join(OUTDIR, recid + ".pdf")):
                print("{} already exists, skipping".format(recid))
                continue
            fetch(recid,url)

read_file(INPUT)
