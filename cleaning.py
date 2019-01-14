"""Cleaning up script.

Usage:
  cleaning.py --in=<infile> --out=<outfile>

Options:
  --in=<infile>    Input file with radiology reports
                   Input file is expected to have two columns: one with the
                   report id, and another with the report text.
  --out=<outfile>  Output file with cleaned radiology reports
"""
from docopt import docopt

import pandas as pd
import chardet
import csv

from cleverparser import CleverParser
from helpers import normalize


if __name__ == '__main__':
    arguments = docopt(__doc__)

    datafile = arguments['--in']
    outfile = arguments['--out']

    print('Loading data...')
    rawfile = open(datafile, 'rb').read()
    encodeInfo = chardet.detect(rawfile[:10000])
    df_cases = pd.read_csv(datafile, encoding=encodeInfo['encoding'], names=['id', 'transcript'])

    print('Loading dictionaries...')
    full_parser = CleverParser('Data/clever_base_terminology.txt')
    full_parser.addTermDictionary('Data/clever_ext_leonard.txt')

    print('Applying text normalization...')
    df_cases['normalized'] = df_cases['transcript'].apply(lambda text: normalize(text, full_parser))

    print('Saving clean data...')
    df_cases.to_csv(outfile, columns=['id', 'normalized'], header=False, index=False, quoting=csv.QUOTE_NONNUMERIC)
