'''
Created on Dec 13, 2016

@author: Janine Tan
'''
from Folder import Folder
from Word import Word
import os

trainingDistinctWords = {}
trainingSpamEmails = []
trainingLegitEmails = []
folderList = []
nWordsSpam = 0
nWordsLegit = 0

def loadEmails(path):
        print("Loading emails...")
        for i in range(1,11):
            folderPath = path + str(i)
            folder = Folder()
            print("Loading email[",i,"]...")
            for filename in os.listdir(folderPath):
                content = open(folderPath + '\\' + filename).read()
                if filename.startswith('sp'):
                    folder.addSpamEmail(content)
                else:
                    folder.addLegitimateEmail(content)

            folderList.append(folder)

def preparingTrainingSet(testingIndex):

        print("Preparing training set (find distinct words and load training spam and legit emails)...")
        
        trainingSpamEmails = []
        trainingLegitEmails = []
        trainingDistinctWords = {}
        
        #getting all the emails read except for the testing index
        for i in range(len(folderList)):
            if i != testingIndex:
                print("Preparing folder[",i,"]...")
                trainingSpamEmails += folderList[i].spamEmail
                trainingLegitEmails += folderList[i].legitEmail

        print("Spam: ", len(trainingSpamEmails))
        print("Legit: ", len(trainingLegitEmails))

        for email in trainingLegitEmails:
            email = email.split()
            tokenizedEmail = set(email)

            #count term frequencies
            for token in tokenizedEmail:
                if token in trainingDistinctWords:
                    word = trainingDistinctWords.get(token)
                    word.presentLegitCount += 1
                    word.notPresentLegitCount -= 1
                else:
                    word = Word(token)
                    word.presentLegitCount = 1  #number of times the word appeared in an email
                    word.notPresentLegitCount = len(trainingLegitEmails) - 1
                    word.presentSpamCount = 0
                    word.notPresentSpamCount = len(trainingSpamEmails)
                    trainingDistinctWords[token] = word



        for email in trainingSpamEmails:
            email = email.split()
            tokenizedEmail = set(email)
            
            for token in tokenizedEmail:
                if token in trainingDistinctWords:
                    word = trainingDistinctWords.get(token)
                    word.presentSpamCount += 1
                    word.notPresentSpamCount -= 1
                else:
                    word = Word(token)
                    word.presentSpamCount = 1
                    word.notPresentSpamCount = len(trainingSpamEmails) - 1
                    word.presentLegitCount = 0
                    word.notPresentLegitCount = len(trainingLegitEmails)
                    trainingDistinctWords[token] = word



        print("Training distinct words: ", len(trainingDistinctWords))


#start
loadEmails('data\\bare\\part')

for i in range(10):
    preparingTrainingSet(i)
            
