# -*- coding: utf-8 -*-
"""
Created on Tue Sep 04 14:56:30 2018

@author: Chaitanya Kulkarni
@modified : Leonard Wee 04 Sept 2018 - so we can run this in Tata
"""

#Python code to illustrate parsing of XML files
# importing the required modules
import csv
import requests
import xml.etree.ElementTree
import pickle
import glob
import re


#Gets the string of the single report from uima.cas.Sofa
def GetString(loc):
    strg = []
    e = xml.etree.ElementTree.parse(loc)
    dom = e.findall('uima.cas.Sofa')
    for atype in dom:
        strg.append(atype.get('sofaString'))
    return strg[0]

#Gets the tokens from org.apache.ctakes.typesystem.type.syntax.WordToken
def getTokens(loc):
    tokens = []
    e = xml.etree.ElementTree.parse(loc)
    dom = e.findall('org.apache.ctakes.typesystem.type.syntax.WordToken')
    for atype in dom:
        tokens.append(atype.get('normalizedForm'))
    return tokens

#Check if it is closely related to any probable cancer terms
def PossibleCancerTerms(tokens):
    terms = ['growth', 'mass', 'nodul.*', 'lesion.*']
    for token in tokens:
        token = token.lower()
        if re.match("|".join(terms), token):
            return True
    return False

#Check if it is closely related to any probable cancer terms
def CancerTerms(tokens):
    terms = ['tumo.*r', '^ca$', 'cancer.*', 'neoplas.*','malignan.*','^carcinoma$']
    for token in tokens:
        token = token.lower()
        if re.match("|".join(terms), token):
            return True
    return False

#Get the begin and end of NP from org.apache.ctakes.typesystem.type.syntax.NP and gets chunks using the strings gotten before.
def getNPChunks(loc, strg):
    NP_chunk = []
    e = xml.etree.ElementTree.parse(loc)
    dom = e.findall('org.apache.ctakes.typesystem.type.syntax.NP')
    for atype in dom:
        if atype.get('chunkType') == "NP":
            start = int(atype.get('begin'))
            end = int(atype.get('end'))
            NP_chunk.append(strg[start : end])
    return NP_chunk

if __name__ == '__main__':
    #set the path to the split data files
    inputData = 'C:/Users/leonard.wee/OneDrive - Maastro - Clinic/Running_Grants/SARRLEK/chunk_process_filter/Data/*.xml'
    processed_loc = 'C:/Users/leonard.wee/OneDrive - Maastro - Clinic/Running_Grants/SARRLEK/chunk_process_filter/Processed/'

    All_xml = glob.iglob(inputData, recursive=True)
    XML_tokens = []
    for j, filename in enumerate(All_xml):
        XML_tokens = getTokens(filename)
        if CancerTerms(XML_tokens)|PossibleCancerTerms(XML_tokens) :
            strg = GetString(filename)
            NP_chunks = getNPChunks(filename, strg)
            for i, chunk in enumerate(NP_chunks):
                #--------------------- @Chaitanya :
                #--------------------- I think here we need to check if part or all of the chunk
                #--------------------- matches something in the CLEVER dictionary
                #--------------------- and if so substitute the part that matches
                with open(processed_loc + "chunk_" + str(j) + "_" + str(i) + ".pkl", "wb") as output_file:
                    #----------------- @Chaitanya :
                    #----------------- I assume writing each chunk in its own j_i pickle will be
                    #----------------- useful later when we do the chunk entropy to filter out all
                    #----------------- of the extremely frequent and extremely rare chunks?
                    pickle.dump(chunk, output_file)
                    output_file.close()
        else:
            pass
