# -*- coding: utf-8 -*-
"""
Created on Sat Dec 23 23:18:22 2017

@author: zcw2218
"""
from LimitStack import *
class DPcache():
    def __init__(self,dictionary):
        self.dict = {}
        self.dictionary = dictionary
        
        
    def __str__(self):
        return str(self.dict) 
        
    #Push the mth cuttings 
    def pushn(self,cuttings,taul):
        #add words to cache if they first appear in our view
        for cutting in cuttings:
            if cutting[0] not in self.dict.keys():
                self.dict[cutting[0]] = LimitStack(taul,0) 

        for word in self.dict:
            sum = 0
            #self.stack = self.dict[word]
            for cutting in cuttings:
                if word == cutting[0]:
                    sum += cutting[2]*(1+self.dict[word].get(cutting[1]-1))
                else:
                    sum += cutting[2]*self.dict[word].get(cutting[1]-1)

            self.dict[word].push(sum)

    def pushr(self,cuttings,taul):
        #add words to cache if they first appear in our view
        for cutting in cuttings:
            if cutting[0] not in self.dict.keys():
                self.dict[cutting[0]] = LimitStack(taul,0)
       

        for word in self.dict:
            sum = 0
            #self.stack = self.dict[word]
            for cutting in cuttings:
                if word == cutting[0]:
                    sum += cutting[2]
                else:
                    sum += cutting[2]*self.dict[word].get(cutting[1]-1)
            #print(word,cutting,sum,self.dict[word])
            self.dict[word].push(sum)
            
            
    def cacheprint(self):
        for k,v in self.dict.items():
            print('{k}:{v}'.format(k = k, v = v))
            
            
    def top(self):
        return {k:v.top() for k,v in self.dict.items()}
