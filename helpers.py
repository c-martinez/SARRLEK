import re
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

def normalize(text, parser=None):
    text = replaceDates(text)
    text = replacePunctuation(text)
    if parser is not None:
        text = parser.replacement(text)
    text = textCleanup(text)
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

def buildTermDict(df, keyColumn, nameCols):
    term_frames = []
    for key, df_key in df.groupby(keyColumn):
        # Make single list out of all nameCols
        allnames = sum( (df_key[nc].tolist() for nc in nameCols) , [])
        allnames = list(set(allnames))
        allnames = [ name for name in allnames if name!='' ]

        key = key.upper()
        key = key.replace(' ', '_')
        terms = pd.DataFrame(allnames, columns=['meanings'])
        terms['keys'] = key
        term_frames.append(terms)

    return pd.concat(term_frames, ignore_index=True)

def sparqlToTermDict(qry, endpoint="http://localhost:8890/sparql", keyColumn=None, nameCols=None):
    # Execute SPARQL query
    df = sparqlToDataframe(qry)
    df = df.fillna('')
    return buildTermDict(df, keyColumn=keyColumn, nameCols=nameCols)
