"""Train neural network on LDA topics.

Usage:
  trainlda.py --lda-vectors=<vecfile> --in-classes=<classes> --prog-classifier=<classifier> --cancer-classifier=<classifier>

Options:
  --lda-vectors=<vecfile>  Vector representation of reports
  --in-classes=<classes>   Input file with classification of radiology reports. Should have 3 columns: Id,Cancer,Progression
  --prog-classifier=<classifier>    Produced torch classifier for progression
  --cancer-classifier=<classifier>  Produced torch classifier for cancer
"""
from docopt import docopt

from buildlda import N_TOPICS
from torchnn import DataLoader, TorchNN

if __name__ == '__main__':
    arguments = docopt(__doc__)

    ldaVectors = arguments['--lda-vectors']
    classesfile = arguments['--in-classes']
    progClassifierFileName = arguments['--prog-classifier']
    cancerClassifierFileName = arguments['--cancer-classifier']

    print('Preparing data...')
    print(classesfile)
    c_loader = DataLoader(ldaVectors, 'Cancer', classesfile)
    p_loader = DataLoader(ldaVectors, 'Prog'  , classesfile)

    print('Building networks...')
    c_classifier = TorchNN(c_loader, N_TOPICS)
    p_classifier = TorchNN(p_loader, N_TOPICS)

    print('Training networks <ADD MORE EPOCHS ?>...')
    c_classifier.train(1)
    p_classifier.train(1)

    print('Saving classifiers...')
    c_classifier.saveModel(cancerClassifierFileName)
    p_classifier.saveModel(progClassifierFileName)
