'''
Created on Dec 13, 2016

@author: Janine Tan
'''
from Folder import Folder
from Word import Word
import os

trainDistinctWords = {}
trainSpamEmails = []
trainLegitEmails = []
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

def prepareTrainingSet(testingIndex):
        trainDistinctWords = {}
        trainSpamEmails = []
        trainLegitEmails = []
        
        print("Find distinct words and load training spam and legit emails...")
        #getting all the emails read except for the testing index
        for i in range(len(folderList)):
            if i != testingIndex:
                print("Folder",i)
                trainSpamEmails += folderList[i].spamEmail
                trainLegitEmails += folderList[i].legitEmail

        print("Spam: ", len(trainSpamEmails))
        print("Legit: ", len(trainLegitEmails))

        for email in trainLegitEmails:
            email = email.split()
            splittedEmail = set(email)   

            #count term frequencies
            for token in splittedEmail:
                if token in trainDistinctWords:
                    word = trainDistinctWords.get(token)
                    word.presentLegitCount += 1
                    word.notPresentLegitCount -= 1
                else:
                    word = Word(token)
                    word.presentLegitCount = 1  #number of times the word appeared in an email
                    word.notPresentLegitCount = len(trainLegitEmails) - 1
                    word.presentSpamCount = 0
                    word.notPresentSpamCount = len(trainSpamEmails)
                    trainDistinctWords[token] = word



        for email in trainSpamEmails:
            email = email.split()
            splittedEmail = set(email)
            
            for token in splittedEmail:
                if token in trainDistinctWords:
                    word = trainDistinctWords.get(token)
                    word.presentSpamCount += 1
                    word.notPresentSpamCount -= 1
                else:
                    word = Word(token)
                    word.presentSpamCount = 1
                    word.notPresentSpamCount = len(trainSpamEmails) - 1
                    word.presentLegitCount = 0
                    word.notPresentLegitCount = len(trainLegitEmails)
                    trainDistinctWords[token] = word



        print("Distinct words: ", len(trainDistinctWords))


#start
loadEmails('data\\bare\\part')

for i in range(10):
    prepareTrainingSet(i)
            
