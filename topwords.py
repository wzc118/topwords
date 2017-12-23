# -*- coding: utf-8 -*-
"""
Created on Sat Dec 23 23:15:07 2017

@author: zcw2218
"""
import re
from collections import Counter
from pandas import DataFrame
from pandas import Series
import pandas as pd
import numpy as np
import math
from decimal import *
import sys
from LimitStack import *
from segtree import *
from DPcache import *
pd.set_option('precision', 18)

def Prepocessing(Inputfile):
    f = open(Inputfile,encoding='UTF-8')
    texts = []
    for line in f:
        text = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——，。、~@#￥%……&*（）－ ～ “”：； \ ≧ ▽ ≦ )-《》！＂＂．？】【]+|[0-9]+|[a-zA-Z]"," ",line).split()
        for seg in text:
            texts.append(seg)
    f.close() 
    
    return texts

def Dictionary(texts,taul,tauF,useProbThld):
    permutations = []
    for text in texts:
        for i in range(1,taul+1):
            for j in range(len(text)):
                if j+i <= len(text):
                    permutations.append(text[j:j+i])

    cnt = Counter(permutations)
    puredict = {k:v for k,v in cnt.items() if len(k) == 1 or v >= tauF}
    sumcount = sum(list(puredict.values()))
    puredict.update((k,Decimal(v/sumcount)) for k,v in puredict.items())
    puredict = {k:v for k,v in puredict.items() if len(k) == 1 or v >= useProbThld}
    sumPrunedFreq = sum(list(puredict.values()))
    puredict.update((k,Decimal(v/sumPrunedFreq)) for k,v in puredict.items())
    
    return puredict 

def DPLikelihoodsBackward(T,dictionary,taul):
    #backward likelihoods: P(T_[>=m]|D,\theta)
    likelihoods = [Decimal(0)]*(len(T)+1)
    likelihoods[len(T)] = Decimal(1)
    
    #dynamic programming from text tail to head
    for m in range(len(T)-1,-1,-1):
        tLimit = taul if (m + taul < len(T)) else (len(T) - m)
        sum = 0
        for t in range(1,tLimit+1):
            candidateWord = T[m:m+t]
            if candidateWord in dictionary.keys():
                sum += Decimal(dictionary[candidateWord]*likelihoods[m+t])
            else:
                sum = sum
        likelihoods[m] = sum
  
    return likelihoods
            
def DPLikelihoodsForward(T,dictionary,taul):
    #forward likelihoods: P(T_[<=m]|D,\theta)
        likelihoods = [Decimal(0)]*(len(T)+1)
        likelihoods[0] = Decimal(1)
        
        #dynamic programming from text head to tail
        for m in range(1,len(T)+1):
            tLimit = taul if (m-taul >= 0) else m
            sum = 0
            for t in range(1,tLimit+1):
                candidateWord = T[m-t:m]
                if candidateWord in dictionary.keys():
                    sum += Decimal(dictionary[candidateWord]*likelihoods[m-t])
                else:
                    sum = sum 
            likelihoods[m] = sum
        
        return likelihoods
            
            
def DPExpectations(T,dictionary,likelihoods,taul):
    #expectations of word use frequency: n_i(T_[>=m])
    niTs = DPcache(dictionary)
    riTs = DPcache(dictionary)
    
    #dynamic programming from text tail to head
    for m in range(len(T)-1,-1,-1):
        tLimit = taul if (m + taul < len(T)) else (len(T) - m)
        # get all possible cuttings for T_m with one word in head and rest in tail
        cuttings = []
        for t in range(1,tLimit+1):
            candidateWord = T[m:m+t]
            if candidateWord in dictionary.keys():
                rho = Decimal(dictionary[candidateWord]*likelihoods[m+t]/likelihoods[m])
                cuttings.append([candidateWord,t,rho])

        niTs.pushn(cuttings,taul)
        #riTs.pushr(cuttings,taul)

    return (list(map(lambda x,y:[x,y],niTs.top().keys(),niTs.top().values())))

                
        
            
def updateDictionary(texts,dictionary,taul):
#calculating the likelihoods (P(T|theta)) and expectations (niS and riS)
    likelihoodsum = 0
    expectation = []
    count = 0
    for text in texts:
        likelihoods = DPLikelihoodsBackward(text,dictionary,taul)
        likelihoodsum += likelihoods[0]
        count += 1
        expectation.extend(DPExpectations(text,dictionary,likelihoods,taul))
        
    expectations = pd.DataFrame(expectation,columns=['word','nis'])
    nis = expectations['nis'].groupby(expectations['word']).sum().reset_index()
    niSum = expectations['nis'].sum()
    nis['nis'] = nis['nis'].apply(lambda x : Decimal(x/niSum))
    thetaS = dict(zip(nis.word,nis.nis))
    #ris = expectations[expectations['word'].apply(lambda x: len(x) > 1)].reset_index(drop=True)
    #print(ris.sort_values('ris',ascending = False).head(5))
    #ris['s'] = ris['ris'].apply(lambda x: - math.log(Decimal(1)- x))
    #ris = ris['ris'].groupby(ris['word']).sum().reset_index().sort_values('ris',ascending=False) 
    #phiS = dict(zip(ris.word,ris.ris))
    avglikelihood = likelihoodsum/count
    
    return (thetaS,avglikelihood)
    
def pruneDictionary(thetaS,useProbThld):
# prune thetaS by use probability threshold
    prunedThetaS =  {k:v for k,v in thetaS.items() if len(k) == 1 or v >= useProbThld}
    sumPrunedWordTheta = sum(list(prunedThetaS.values()))
    prunedThetaS.update((k,Decimal(v/sumPrunedWordTheta)) for k,v in prunedThetaS.items())
    
    
    return (prunedThetaS)

def PESegment(texts,dictionary,wordBoundaryThld,taul):
    fo = open("turntotext.txt","a",encoding='utf-8')
    for text in texts:
        #calculating the P(T|theta) forwards and backwards respectively
        forwardLikelihoods = DPLikelihoodsForward(text,dictionary,taul)
        backwardLikelihoods = DPLikelihoodsBackward(text,dictionary,taul)
        #calculating the boundary scores of text
        boundaryScores = [forwardLikelihoods[k]*backwardLikelihoods[k]/backwardLikelihoods[0] for k in range(1,len(text)+1)]
        if wordBoundaryThld > 0:
            fo.writelines(["%s " % item  for item in TextSegmentor(text, boundaryScores, wordBoundaryThld)])
        else:
            fo.writelines(["%s " % item  for item in SegmentTree(text,boundaryScores,dictionary).listleaf(text,boundaryScores)])
    fo.close()
            
        
def TextSegmentor(T, boundaryScores, wordBoundaryThld):
    boundaryindex  = [i for i,j in enumerate(boundaryScores) if j >= wordBoundaryThld]
    #return text itself if it has only one character
    if len(T) <= 1:
        return T.split()
    splitResult = lindexsplit(T,*boundaryindex)
    return splitResult

   
def lindexsplit(some_list, *args):

    if args:
        args = (0,) + tuple(data+1 for data in args) + (len(some_list)+1,)

    my_list = []
    for start, end in zip(args, args[1:]):
        my_list.append(some_list[start:end])
    return my_list


def main():
    ###initialization
    taul = 4 # threshold of word length
    tauF = 2 # threshold of word frequency
    useProbThld = 1.0*10**(-6) #word use probability (theta) threshold
    wordBoundaryThld = 0
    
    # preprocess the input corpus
    texts = Prepocessing('testnew.txt')
    #generate the overcomplete dictionary
    dictionary = Dictionary(texts,taul,tauF,useProbThld)
    #initialize the loop variables
    iteration = 1
    converged = False
    lastLikelihood = -1.0
    convergeTol = 1.0*10**(-3)
    numIterations = 5
    ###EM loop
    while(converged != True and iteration <= numIterations):
        #update and prune the dictionary
        (thetaS,avglikelihood) = updateDictionary(texts,dictionary,taul)
        dictionary = pruneDictionary(thetaS,useProbThld)
        # info of current iteration
        print("Iteration {0}, likelihood:{1}, dictionary:{2}".format(iteration,avglikelihood,len(dictionary)))
        # test the convergence condition
        if lastLikelihood > 0 and abs((avglikelihood - lastLikelihood)/lastLikelihood <convergeTol):
            converged = True
        # prepare for the next iteration
        lastLikelihood = avglikelihood
        iteration += 1
        
        
    PESegment(texts,dictionary,wordBoundaryThld,taul)
        
if __name__ == "__main__":
    main()
