import csv
import numpy as np
import pandas as pd

import torch
import torch.nn as nn

def classLabelToArray(label):
    '''
    NC or NP  --> [ 0, 1 ]
    C  or P   --> [ 1, 0 ]
    '''
    return [ 0., 1. ] if 'N' in label else [ 1., 0. ]

def classArrayToLabel(arr):
    '''
    [ 0, 1 ] --> NC or NP
    [ 1, 0 ] -->  C  or P
    '''
    # return [ 0., 1. ] if 'N' in label else [ 1., 0. ]
    return 'N' if arr[0] < arr[1] else ''

class DataLoader():
    def __init__(self, ldaVectors, clsLabel, classesfile):
        self.ldaVectors = ldaVectors
        self.clsLabel = clsLabel
        self.df_classes = pd.read_csv(classesfile, sep=',', names=['ID', 'Cancer', 'Prog'])
        self.gt_ids = self.df_classes['ID'].unique()
        self._doInit()

    def getClassForID(self, id, cls):
        try:
            return self.df_classes[self.df_classes['ID']==id][cls].tolist()[0]
        except:
            return None

    def _doInit(self):
        csvfile = open(self.ldaVectors, 'r')
        self.reader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)

    def _readNext(self):
        for id_str, vec_str in self.reader:
            id = int(id_str)
            if id in self.gt_ids:
                vec_str = vec_str.replace('\n', '')
                vec_str = vec_str[1:-1]

                vec = np.fromstring(vec_str, sep=' ')
                cls = self.getClassForID(id, self.clsLabel)
                # return vec, cls
                return vec, classLabelToArray(cls)
        raise Exception

    def getNext(self):
        try:
            return self._readNext()
        except:
            self._doInit()
            return self._readNext()

    def getTorchBatch(self, batchSize):
        vectors, classes = zip(*[ self.getNext() for i in range(batchSize) ])
        vectors = torch.tensor(vectors, dtype=torch.float)
        classes = torch.tensor(classes, dtype=torch.float)
        return vectors, classes

class TorchNN():
    def __init__(self, loader, inVectorSize, batch_size = 10):
        # Defining input size, hidden layer size, output size and batch size respectively
        self.n_in = inVectorSize   # Vector size
        self.batch_size = batch_size
        self.loader = loader
        n_out = 2   # 2 classes
        n_h  = 50

        # Create a model
        self.model = nn.Sequential(nn.Linear(self.n_in, n_h),
                             nn.ReLU(),
                             nn.Linear(n_h, n_out),
                             nn.Sigmoid())

        # Construct the loss function
        self.criterion = nn.MSELoss()

        # Construct the optimizer (Stochastic Gradient Descent in this case)
        self.optimizer = torch.optim.SGD(self.model.parameters(), lr=0.01)

    def train(self, nEpochs=500):
        # Gradient Descent
        for epoch in range(nEpochs):
            x, y = self.loader.getTorchBatch(self.batch_size)

            # Forward pass: Compute predicted y by passing x to the model
            y_pred = self.model(x)

            # Compute and print loss
            loss = self.criterion(y_pred, y)
            # print('epoch: ', epoch,' loss: ', loss.item())

            # Zero gradients, perform a backward pass, and update the weights.
            self.optimizer.zero_grad()

            # perform a backward pass (backpropagation)
            loss.backward()

            # Update the parameters
            self.optimizer.step()

    def saveModel(self, filename):
        torch.save(self.model, filename)
