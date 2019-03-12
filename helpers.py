import re
import csv
import pandas as pd

from io import StringIO
from SPARQLWrapper import SPARQLWrapper, CSV

from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.stem import WordNetLemmatizer

stop_words = set(stopwords.words('english'))
snowball_stemmer = SnowballStemmer('english')
wordnet_lemmatizer = WordNetLemmatizer()

def replacePunctuation(text):
    # Replace punctuation with tokens so we can use them in our model
    text = text.replace('.', ' PERIOD ')
    text = text.replace(',', ' COMMA ')
    text = text.replace('"', ' QUOTATION_MARK ')
    text = text.replace(';', ' SEMICOLON ')
    text = text.replace('!', ' EXCLAMATION_MARK ')
    text = text.replace('?', ' QUESTION_MARK ')
    text = text.replace('(', ' LEFT_PAREN ')
    text = text.replace(')', ' RIGHT_PAREN ')
    text = text.replace('--', ' HYPHENS ')
    text = text.replace('?', ' QUESTION_MARK ')
    text = text.replace('\n', ' NEW_LINE ')
    text = text.replace(':', ' COLON ')
    return text

def replaceDates(text):
    # Matches any 3 sequences of numbers divided by '.', '/' or '-'
    date_pattern = "(\d+\.\d+\.\d+)|(\d+\/\d+\/\d+)|(\d+\-\d+\-\d+)"
    text = re.sub(date_pattern, 'DATE', text)
    return text

def textCleanup(text):
    tokens = []
    words = text.split()
    # Stop Words removal
    words = [w for w in words if not w in stop_words]
    for word in words:
        # Process only words which are not fully upper case
        # Fully upper case words are special
        if not word.isupper():
            # Word Lemmatizer
            word = wordnet_lemmatizer.lemmatize(word)
            # Word Stemming
            word = snowball_stemmer.stem(word)
        tokens.append(word)

    return ' '.join(tokens)

def CreateHirarchy(txt):
    lst_Of_Sen = txt.split("PERIOD")
    hirarchy_1 = []
    hirarchy_2 = []
    hirarchy_3 = []
    others = []

    for sen in lst_Of_Sen:
        if ("LUNG_MASS" or "LUNG_CARCINOMA" or "LUNG_NODULE" or "LUNG_CARCINOMA") in sen:
            hirarchy_1.append(sen)
            continue
        if ("RIGHT_LUNG" or "LEFT_LUNG" or "LUNG" or "LUNG_NON_SMALL_CELL" or "LUNG_SMALL_CELL") in sen:
            hirarchy_2.append(sen)
            continue
        if ("LESION " or "MASS" or "CHEST_MASS" or "CARCINOMA" or "CONTRAST_ENHANCED_CT_SCAN") in sen:
            hirarchy_3.append(sen)
            continue
        others.append(sen)
    return hirarchy_1, hirarchy_2, hirarchy_3, others


def Structurize_report(hirarchy_1, hirarchy_2, hirarchy_3, others):
    Structured_Report = ''

    for i in hirarchy_1:
        Structured_Report = Structured_Report + i + " DOT "
    for i in hirarchy_2:
        Structured_Report = Structured_Report + i + " DOT "
    for i in hirarchy_3:
        Structured_Report = Structured_Report + i + " DOT "
    for i in others:
        Structured_Report = Structured_Report + i + " DOT "

    return Structured_Report


def normalize(text, parser=None, structurize=False):
    text = replaceDates(text)
    text = replacePunctuation(text)
    if parser is not None:
        text = parser.replacement(text)
    text = textCleanup(text)
    if structurize:
        text = Structurize_report(CreateHirarchy(text))
    return text


# SPARQL helpers
def sparqlToDataframe(qry, endpoint="http://localhost:8890/sparql"):
    # Execute SPARQL query
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(qry)
    sparql.setReturnFormat(CSV)
    res = sparql.queryAndConvert()
    resAsStr = res.decode('utf-8')
    return pd.read_csv(StringIO(resAsStr))

def wordsToSingleToken(words):
    words = words.upper()
    words = words.replace(' ', '_')
    return words

def buildTermDict(df, keyColumn, nameCols):
    term_frames = []
    for key, df_key in df.groupby(keyColumn):
        # Make single list out of all nameCols
        allnames = sum( (df_key[nc].tolist() for nc in nameCols) , [])
        allnames = list(set(allnames))
        allnames = [ name for name in allnames if name!='' ]

        terms = pd.DataFrame(allnames, columns=['meanings'])
        terms['keys'] = wordsToSingleToken(key)
        term_frames.append(terms)

    return pd.concat(term_frames, ignore_index=True)

def sparqlToTermDict(qry, endpoint="http://localhost:8890/sparql", keyColumn=None, nameCols=None):
    # Execute SPARQL query
    df = sparqlToDataframe(qry)
    df = df.fillna('')
    return buildTermDict(df, keyColumn=keyColumn, nameCols=nameCols)

class SentenceIterator(object):
    def __init__(self, datafile, encoding, row2record):
        '''
        row2record   A function which takes a row and the row number from the CSV file,
                     and returns a record in the format the consumer intends to use it.
        '''
        csvfile = open(datafile, encoding=encoding)
        self.index = 0
        self.csvreader = csv.reader(csvfile, delimiter=',')
        self.row2record = row2record

    def __iter__(self):
        return self

    def __next__(self):
        try:
            row = next(self.csvreader)
            self.index += 1
            if self.index % 1000 == 0:
                print('.', end='', flush=True)
            # return TaggedDocument(row[1].split(), [self.index])
            return self.row2record(row, self.index)
        except:
            raise StopIteration
