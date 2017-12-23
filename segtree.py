# -*- coding: utf-8 -*-
"""
Created on Sat Dec 23 23:15:56 2017

@author: zcw2218
"""
class Node(object):
    def __init__(self,left = 0,right = 0):
        self.left = left
        self.right = right
        self.leftChild = None
        self.rightChild = None
        self.splitPos = -1
    

class SegmentTree(object):
    def __init__(self,T,boundaryScores,dictionary):
            
        
        def SegTree(left,right):
            if T[left:right+1] in dictionary.keys():
                return Node(left,right)

            
            node = Node()
            max = -1
            splitPos = -1
            for i in range(left,right):
                if max < boundaryScores[i]:
                    max = boundaryScores[i]
                    splitPos = i   
            #if splitPos - left > 0:
            node.leftChild = SegTree(left,splitPos)
            #if right - splitPos > 0:
            node.rightChild = SegTree(splitPos+1,right)
            node.left = left
            node.right = right
            node.splitPos = splitPos

            return node
        
        if T:
            self.root = SegTree(0,len(T)-1)
            
            
    def printleaf(self,T,boundaryScores):
        
        def print_until(node):
            if not node:
                return;
            if not node.leftChild and not node.rightChild:
                maxindex =  max(enumerate(boundaryScores[node.left:node.right+1]),key=lambda x: x[1])[0] + node.left
                if maxindex == node.right:
                    print(T[node.left:node.right+1])
                else:
                    print(T[node.left:maxindex+1])
                    print(T[maxindex:node.right+1])
                    
            print_until(node.leftChild)
            print_until(node.rightChild)
            

        
        return print_until(self.root)
    
    def listleaf(self,T,boundaryScores):
        global leaf 
        leaf = []
        def listleaf_until(node):
            
            if not node:
                return;
            if not node.leftChild and not node.rightChild:
                maxindex =  max(enumerate(boundaryScores[node.left:node.right+1]),key=lambda x: x[1])[0] + node.left
                if maxindex == node.right:
                    leaf.append(T[node.left:node.right+1])
                else:
                    leaf.append(T[node.left:maxindex+1])
                    leaf.append(T[maxindex:node.right+1])
                    
            listleaf_until(node.leftChild)
            listleaf_until(node.rightChild)
            return leaf
        
        return listleaf_until(self.root)
