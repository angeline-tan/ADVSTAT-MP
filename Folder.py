'''
Created on Dec 13, 2016

@author: Janine Tan
'''
class Folder:
    def __init__(self):
        self.spamEmail = []
        self.legitEmail = []

    def addSpamEmail(self, email):
        self.spamEmail.append(email)

    def addLegitimateEmail(self, email):
        self.legitEmail.append(email)