from flair.models import TextClassifier
from flair.data import Sentence

from gensim.models import LdaModel
from gensim.corpora.dictionary import Dictionary

from gensim.models.doc2vec import Doc2Vec

from buildlda import getLDATopics

import torch
from torchnn import classArrayToLabel

class FlairClassifier():
    def __init__(self, c_classifier_file, p_classifier_file):
        self.classifier_c = TextClassifier.load_from_file(c_classifier_file)
        self.classifier_p = TextClassifier.load_from_file(p_classifier_file)

    def classify(self, text):
        sentence = Sentence(text)

        c = self.classifier_c.predict(sentence)
        c_label = c[0].labels[0].value
        p = self.classifier_p.predict(sentence)
        p_label = p[0].labels[0].value

        return [c_label,p_label]

class LDAClassifier():
    def __init__(self, ldaModelFile, ldaDictFile, c_classifier_file, p_classifier_file):
        self.lda = LdaModel.load(ldaModelFile)
        self.cases_dict = Dictionary.load(ldaDictFile)
        self.nn_c = torch.load(c_classifier_file)
        self.nn_p = torch.load(p_classifier_file)

    def classify(self, text):
        vector = getLDATopics(text, self.cases_dict, self.lda)

        vector = torch.tensor(vector)
        c_pred = self.nn_c(vector)
        p_pred = self.nn_p(vector)

        c_label = classArrayToLabel(c_pred) + 'C'
        p_label = classArrayToLabel(p_pred) + 'P'
        return [c_label,p_label]

class W2VClassifier():
    def __init__(self, w2vModelFile, c_classifier_file, p_classifier_file):
        self.model = Doc2Vec.load(w2vModelFile)
        self.nn_c = torch.load(c_classifier_file)
        self.nn_p = torch.load(p_classifier_file)

    def classify(self, text):
        vector = self.model.infer_vector(text.split())

        vector = torch.tensor(vector)
        c_pred = self.nn_c(vector)
        p_pred = self.nn_p(vector)

        c_label = classArrayToLabel(c_pred) + 'C'
        p_label = classArrayToLabel(p_pred) + 'P'
        return [c_label,p_label]
