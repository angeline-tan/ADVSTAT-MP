'''
Created on Dec 13, 2016

@author: Janine Tan
'''
from Folder import Folder
from Word import Word
import os

distinctWords = {}
spamEmails = []
legitEmails = []
folderList = []
nWordsSpam = 0
nWordsLegit = 0

def loadEmails(path):
        print("Loading emails...")
        for i in range(1,11):
            partPath = path + str(i)
            partFolder = Folder()
            print("Loading email[",i,"]...")
            for filename in os.listdir(partPath):
                content = open(partPath + '\\' + filename).read()
                if filename.startswith('sp'):
                    partFolder.addSpamEmail(content)
                else:
                    partFolder.addLegitimateEmail(content)

            folderList.append(partFolder)

def prepareTrainingSet(testingIndex):
        distinctWords = {}
        spamEmails = []
        legitEmails = []
        
        print("Find distinct words and load training spam and legit emails...")
        #getting all the emails read except for the testing index
        for i in range(len(folderList)):
            if i != testingIndex:
                print("Folder",i)
                spamEmails += folderList[i].spamEmail
                legitEmails += folderList[i].legitEmail

        print("Spam: ", len(spamEmails))
        print("Legit: ", len(legitEmails))

        for email in legitEmails:
            email = email.split()
            splittedEmail = set(email)

            #count term frequencies
            for token in splittedEmail:
                if token in distinctWords:
                    word = distinctWords.get(token)
                    word.presentLegitCount += 1
                    word.notPresentLegitCount -= 1
                else:
                    word = Word(token)
                    word.presentLegitCount = 1  #number of times the word appeared in an email
                    word.notPresentLegitCount = len(legitEmails) - 1
                    word.presentSpamCount = 0
                    word.notPresentSpamCount = len(spamEmails)
                    distinctWords[token] = word



        for email in spamEmails:
            email = email.split()
            splittedEmail = set(email)
            
            for token in splittedEmail:
                if token in distinctWords:
                    word = distinctWords.get(token)
                    word.presentSpamCount += 1
                    word.notPresentSpamCount -= 1
                else:
                    word = Word(token)
                    word.presentSpamCount = 1
                    word.notPresentSpamCount = len(spamEmails) - 1
                    word.presentLegitCount = 0
                    word.notPresentLegitCount = len(legitEmails)
                    distinctWords[token] = word



        print("Distinct words: ", len(distinctWords))


#start
loadEmails('data\\bare\\part')

for i in range(10):
    prepareTrainingSet(i)
            
