'''
Created on Dec 13, 2016

@author: Janine Tan
'''
class Word:
    def __init__(self, content):
        self.content = content
        self.mutualInfo = 0
    
        self.countLegitEmailContainingWord = 0
        self.countLegitEmailNotContainingWord = 0
        
        self.countSpamEmailContainingWord = 0
        self.countSpamEmailNotContainingWord = 0
        
        self.wordInEmail = False
