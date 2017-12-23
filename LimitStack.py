# -*- coding: utf-8 -*-
"""
Created on Sat Dec 23 23:19:54 2017

@author: zcw2218
"""
class LimitStack():
    def __init__(self,size,initValue):
        self.size = size
        self.stack = [initValue]*size
        self.head = size -1
        
    def __str__(self):
        return str(self.stack)
        
    def push(self,ele):
        self.head = 0 if (self.head + 1 >= self.size) else self.head + 1
        self.stack[self.head] = ele
            
    def top(self):
        return self.stack[self.head]
        
    def get(self,idx):
        #Get the element of certain index (index 0 starts from the last pushed element)
        if (idx >= 0 and idx < self.size):
            pos = (self.size+self.head-idx) if (self.head-idx < 0) else (self.head - idx)
        
        return self.stack[pos]
            
    def printget(self,idx):
        print(self.get(idx))
