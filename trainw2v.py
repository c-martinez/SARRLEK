"""Train neural network on W2V vectors.

Usage:
  trainw2v.py --w2v-vectors=<vecfile> --in-classes=<classes> --prog-classifier=<classifier> --cancer-classifier=<classifier>

Options:
  --w2v-vectors=<vecfile>  Vector representation of reports
  --in-classes=<classes>   Input file with classification of radiology reports. Should have 3 columns: Id,Cancer,Progression
  --prog-classifier=<classifier>    Produced torch classifier for progression
  --cancer-classifier=<classifier>  Produced torch classifier for cancer
"""
from docopt import docopt

from buildw2v import VECTOR_SIZE
from torchnn import DataLoader, TorchNN

if __name__ == '__main__':
    arguments = docopt(__doc__)

    w2vVectors = arguments['--w2v-vectors']
    classesfile = arguments['--in-classes']
    progClassifierFileName = arguments['--prog-classifier']
    cancerClassifierFileName = arguments['--cancer-classifier']

    print('Preparing data...')
    print(classesfile)
    c_loader = DataLoader(w2vVectors, 'Cancer', classesfile)
    p_loader = DataLoader(w2vVectors, 'Prog'  , classesfile)

    print('Building networks...')
    c_classifier = TorchNN(c_loader, VECTOR_SIZE)
    p_classifier = TorchNN(p_loader, VECTOR_SIZE)

    print('Training networks <ADD MORE EPOCHS ?>...')
    c_classifier.train(1)
    p_classifier.train(1)

    print('Saving classifiers...')
    c_classifier.saveModel(cancerClassifierFileName)
    p_classifier.saveModel(progClassifierFileName)
