import pandas as pd
import trie_search

from itertools import combinations

class CleverParser():
    def __init__(self, cleverfile=None):
        self.__wordColumn__ = 'word'
        self.__tokenColumn__ = 'token'
        self.clever = pd.DataFrame(columns=[self.__wordColumn__, 'token'])
        if cleverfile:
            self.addTermDictionary(cleverfile)

    def addTermDictionary(self, cleverfile):
        cleverDf = pd.read_csv(cleverfile, sep='|', names=[self.__wordColumn__, self.__tokenColumn__], skiprows=1, usecols=[1,2])
        self.addTermDataFrame(cleverDf)

    def addTermDataFrame(self, cleverDf):
        assert self.__wordColumn__ in cleverDf.columns, "'%s' column missing from DataFrame"%self.__wordColumn__
        assert self.__tokenColumn__ in cleverDf.columns, "'%s' column missing from DataFrame"%self.__tokenColumn__
        self.clever = pd.concat([self.clever, cleverDf], ignore_index=True)
        clever_words = self.clever[self.__wordColumn__].tolist()
        self.trie = trie_search.TrieSearch(clever_words)

    def getTokenForWord(self, word):
        ''' NOTE: words are assumed to be unique ! '''
        tag = self.clever[self.clever[self.__wordColumn__]==word][self.__tokenColumn__].tolist()[0]
        return tag

    def replacement(self, sentence):
        replacements = self._getReplacements(sentence)
        newSentence = self._applyReplacements(replacements, sentence)
        return newSentence

    def getAllPossibleReplacements(self, sentence, includeOriginal=False):
        all_replacements = self._getReplacements(sentence)
        allPossible = [ sentence ] if includeOriginal else []

        for r in range(len(all_replacements)):
            for subsetReplacement in combinations(all_replacements, r+1):
                newSentence = self._applyReplacements(subsetReplacement, sentence)
                allPossible.append(newSentence)
        return allPossible

    def _getReplacements(self, sentence):
        replacements = []

        # Trie finds us a word from clever terminology in a sentence, and the index
        # in the sentence where it is located. We search for the longest matching
        # pattern, so if the sentence contains 'family member', the trie will match
        # for 'family member' and not just 'family'.
        for word,index in self.trie.search_longest_patterns(sentence):
            newWord = self.getTokenForWord(word)
            insertPoint = (index, index+len(word))
            replacements.append((insertPoint, newWord))
            # We keep track of where in the sentence we want to replace the word, and
            # by which word we want to replace.
        return replacements

    def _applyReplacements(self, replacements, sentence):
        # If no replacements are found, we keep the initial sentence
        newSentence = sentence

        replacements = sorted(replacements)
        # We cut the sentence at the points where we found a replacement
        for i in range(len(replacements)):
            insertPoint, newWord = replacements[i]

            # We take the beginning of the sentence
            if i==0:
                newSentence = sentence[:insertPoint[0]]

            # ... append the clever token
            newSentence += newWord

            # ... and append the part of the sentence until the next matching point
            if i<len(replacements)-1:
                nextInsertPoint,_ = replacements[i+1]
                newSentence += sentence[insertPoint[1]:nextInsertPoint[0]]
            else:
                # ... or until the end of the sentence if this is the last matching point
                newSentence += sentence[insertPoint[1]:]
        return newSentence
