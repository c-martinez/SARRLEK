import pandas as pd
import trie_search

class CleverParser():
    def __init__(self, cleverfile):
        self.clever = pd.read_csv(cleverfile, sep='|', names=['id', 'word', 'token'])
        clever_words = self.clever['word'].tolist()
        self.trie = trie_search.TrieSearch(clever_words)

    def getTokenForWord(self, word):
        tag = self.clever[self.clever['word']==word]['token'].tolist()[0]
        return tag

    def trieReplacement(self, sentence):
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
