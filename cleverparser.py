import pandas as pd
import trie_search

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
        tag = self.clever[self.clever[self.__wordColumn__]==word][self.__tokenColumn__].tolist()[0]
        return tag

    def replacement(self, sentence):
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
        replacements = sorted(replacements)

        # If no replacements are found, we keep the initial sentence
        newSentence = sentence

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
