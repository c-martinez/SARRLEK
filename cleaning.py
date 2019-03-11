"""Cleaning up script.

Usage:
  cleaning.py --in=<infile> --out=<outfile> [--structurize] [--augment-data]

Options:
  --in=<infile>    Input file with radiology reports
                   Input file is expected to have two columns: one with the
                   report id, and another with the report text.
  --out=<outfile>  Output file with cleaned radiology reports.
  --structurize    Apply additional structurize step.
  --augment-data    Apply data augmentation step.
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
    structurize = arguments['--structurize']
    augmentData = arguments['--augment-data']

    print('Loading data...')
    rawfile = open(datafile, 'rb').read()
    encodeInfo = chardet.detect(rawfile[:50000])
    print('encodeInfo: ',encodeInfo)
    df_cases = pd.read_csv(datafile, encoding=encodeInfo['encoding'], names=['id', 'transcript'])

    print('Loading dictionaries...')
    full_parser = CleverParser('Data/clever_base_terminology.txt')
    full_parser.addTermDictionary('Data/clever_ext_leonard.txt')
    full_parser.addTermDictionary('Data/clever_ext_lung_synonyms.txt')

    parentParser = CleverParser('Data/clever_ext_parent.txt')
    granPaParser = CleverParser('Data/clever_ext_grandparent.txt')

    duplicateIds = df_cases.duplicated('id')
    if len(df_cases[duplicateIds]) > 0:
        print('WARNING: duplicate IDs were found on  %s'%datafile)
        duplicateIdsList = df_cases[duplicateIds]['id'].tolist()
        duplicateSet = list(set(duplicateIdsList))

        for dupId in duplicateSet[:5]:
            nDups = len(df_cases[df_cases['id']==dupId])
            print('   ID %d has %d ocurrences'%(dupId, nDups))

    print('Applying text normalization...')
    df_cases['normalized'] = df_cases['transcript'].apply(lambda text: normalize(text, full_parser))
    df_cases.drop(columns='transcript', inplace=True)

    noDataAugmentation = True
    if augmentData:
        print('Applying data expansion...')

        print('Saving base data...')
        df_cases.to_csv(outfile, columns=['id', 'normalized'], header=False, index=False, quoting=csv.QUOTE_NONNUMERIC, encoding=encodeInfo['encoding'])

        with open(outfile, 'a', encoding=encodeInfo['encoding']) as fout:
            print('Saving extended data')
            for index, row in df_cases.iterrows():
                sentence = row['normalized']
                allreps = parentParser.getAllPossibleReplacements(sentence, includeOriginal=True)
                allreps+= granPaParser.getAllPossibleReplacements(sentence)

                extended_cases_data = [ { 'id': row['id'], 'normalized': rep} for rep in allreps ]
                df_extended = pd.DataFrame(extended_cases_data)

                if index % 100 == 0:
                    print('.', end='', flush=True)
                df_extended.to_csv(fout, columns=['id', 'normalized'], header=False, index=False, quoting=csv.QUOTE_NONNUMERIC)

    else:
        print('Applying finalizing normalization...')
        ancestorNormalizer = lambda sentence: parentParser.replacement(granPaParser.replacement(sentence))

        df_cases['normalized'] = df_cases['normalized'].apply(ancestorNormalizer)

        print('Saving clean data...')
        df_cases.to_csv(outfile, columns=['id', 'normalized'], header=False, index=False, quoting=csv.QUOTE_NONNUMERIC, encoding=encodeInfo['encoding'])
