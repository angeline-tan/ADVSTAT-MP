'''
Created on Dec 13, 2016

@author: Janine Tan
'''
from Folder import Folder
from Word import Word
import os

trainDistinctWords = {}
distinctWords = []
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
        distinctWords = []
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
            listOfWordsInEmail = set(email)
            #count term frequencies
            for token in listOfWordsInEmail:                                     #a word in the list of words in email
                token = token.lower()
                #newWord = True
                if token not in trainDistinctWords:
                    word = Word(token)
                    word.wordInEmail = True
                    word.countLegitEmailContainingWord += 1                      #this token is in the email so counter + 1 for how many documents contains this word
                    trainDistinctWords[token] = word
                elif token in trainDistinctWords:
                    word = trainDistinctWords.get(token)
                    if word.wordInEmail == False:
                        word.countLegitEmailContainingWord +=1
                        word.wordInEmail = True
    
            for w in trainDistinctWords:
                trainDistinctWords[w].wordInEmail = False
        for wo in trainDistinctWords:
                trainDistinctWords[wo].countLegitEmailNotContainingWord = len(trainLegitEmails) - wo.countLegitEmailContainingWord

        for email in trainSpamEmails:
            email = email.split()
            listOfWordsInEmail = set(email)
            #count term frequencies
            for token in listOfWordsInEmail:                                     #a word in the list of words in email
                token = token.lower()
                #newWord = True
                if token not in trainDistinctWords:
                    word = Word(token)
                    word.wordInEmail = True
                    word.countSpamEmailContainingWord += 1                      #this token is in the email so counter + 1 for how many documents contains this word
                    trainDistinctWords[token] = word
                elif token in trainDistinctWords:
                    word = trainDistinctWords.get(token)
                    if word.wordInEmail == False:
                        word.countSpamEmailContainingWord +=1
                        word.wordInEmail = True
    
            for w in trainDistinctWords:
                trainDistinctWords[w].wordInEmail = False
        for wo in trainDistinctWords:
                trainDistinctWords[wo].countSpamEmailNotContainingWord = len(trainSpamEmails) - wo.countSpamEmailContainingWord

        print("Distinct words: ", len(trainDistinctWords))


#start
loadEmails('data\\bare\\part')

for i in range(10):
    prepareTrainingSet(i)
            
