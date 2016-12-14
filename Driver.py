'''
Created on Dec 13, 2016

@author: Janine Tan
'''
from Folder import Folder
from Word import Word
import os
import math
from decimal import *
from collections import Counter

trainDistinctWords = {}
distinctWords = []
trainSpamEmails = []
trainLegitEmails = []
folderList = []


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
        global trainDistinctWords
        global distinctWords
        global trainSpamEmails
        global trainLegitEmails
        
        listOfWordsInEmail = []
        listOfWordsInLegitEmail = []
        listOfWordsInSpamEmail = []
        
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
            for token in listOfWordsInEmail:
                listOfWordsInLegitEmail.append(token.lower())

        ctrLegit = Counter(listOfWordsInLegitEmail)
        
        for token, count in ctrLegit.items():
            word = Word(token)
            word.countLegitEmailContainingWord = count
            trainDistinctWords[token] = word
   
        listOfWordsInEmail = []
            
        for email in trainSpamEmails:
            email = email.split()
            listOfWordsInEmail = set(email)
            for token in listOfWordsInEmail:
                listOfWordsInSpamEmail.append(token.lower())
        
        ctrSpam = Counter(listOfWordsInSpamEmail)
        
        for token, count in ctrSpam.items():
            if token not in trainDistinctWords:
                word = Word(token)
                word.countSpamEmailContainingWord = count  
                trainDistinctWords[token] = word
            else : 
                word = trainDistinctWords.get(token)
                word.countSpamEmailContainingWord = count 
        
        for wo in trainDistinctWords:
                trainDistinctWords[wo].countLegitEmailNotContainingWord = len(trainLegitEmails) - trainDistinctWords[wo].countLegitEmailContainingWord
        
        for wo in trainDistinctWords:
                trainDistinctWords[wo].countSpamEmailNotContainingWord = len(trainSpamEmails) - trainDistinctWords[wo].countSpamEmailContainingWord
        
        '''
        for k in trainDistinctWords:
            print("WORD: " + trainDistinctWords[k].content)
            print("NUmber of Legit Email Containing the word: " + str(trainDistinctWords[k].countLegitEmailContainingWord))
            print("NUmber of Legit Email Not Containing the word: " + str(trainDistinctWords[k].countLegitEmailNotContainingWord))
            print("NUmber of Spam Email Containing the word: " + str(trainDistinctWords[k].countSpamEmailContainingWord))
            print("NUmber of Spam Email Not Containing the word: " + str(trainDistinctWords[k].countSpamEmailNotContainingWord))
        '''
        
        
        print("Distinct words: ", len(trainDistinctWords))

def selectFeatures():
        print("Extracting features/ feature selections..................................")
        global trainDistinctWords
        
        trainDistinctWords =  getRelevantWords(trainDistinctWords)
        
def getRelevantWords(distinctWords):
        for k in distinctWords:
            distinctWords[k].mutualInfo = getMutualInfo(distinctWords[k])

        distinctWords = sorted(distinctWords.items(), key=lambda x:x[1].mutualInfo, reverse = True)[:50]


        distinctWords = {x[0]: x[1] for x in distinctWords}
        print("after convert back to dictionary..........................")

        for i in distinctWords:
            print(distinctWords[i].content,distinctWords[i].mutualInfo)

        return distinctWords

def getMutualInfo(distinctWord):
    
        totalResults = distinctWord.countLegitEmailContainingWord + distinctWord.countLegitEmailNotContainingWord + distinctWord.countSpamEmailContainingWord + distinctWord.countSpamEmailNotContainingWord

        try:
            # P(x=0,c=spam)
            mutualInfo = (distinctWord.countSpamEmailNotContainingWord/totalResults)*\
                         math.log((distinctWord.countSpamEmailNotContainingWord * totalResults)/\
                                    ((distinctWord.countSpamEmailNotContainingWord + distinctWord.countLegitEmailNotContainingWord)*(distinctWord.countSpamEmailNotContainingWord + distinctWord.countSpamEmailContainingWord)),2)

        except (ZeroDivisionError, ValueError):
            mutualInfo = 0.0
   
        try:
            # P(x=0,c=legitimate)
            mutualInfo += (distinctWord.countLegitEmailNotContainingWord/totalResults) *\
                          math.log((distinctWord.countLegitEmailNotContainingWord * totalResults) /\
                                     ((distinctWord.countLegitEmailNotContainingWord+distinctWord.countSpamEmailNotContainingWord) * (distinctWord.countLegitEmailNotContainingWord + distinctWord.countLegitEmailContainingWord)),2)

        except (ZeroDivisionError, ValueError):
            mutualInfo += 0.0
        
        try:
            # P(x=1,c=spam)
            mutualInfo += (distinctWord.countSpamEmailContainingWord / totalResults) *\
                          math.log((distinctWord.countSpamEmailContainingWord * totalResults)/\
                                     ((distinctWord.countSpamEmailContainingWord+distinctWord.countLegitEmailContainingWord) * (distinctWord.countSpamEmailContainingWord + distinctWord.countSpamEmailNotContainingWord)),2)
        except (ZeroDivisionError, ValueError):
            mutualInfo += 0.0
       
        try:
            # P(x=1,c=legitimate)
            mutualInfo += (distinctWord.countLegitEmailContainingWord/totalResults) *\
                          math.log((distinctWord.countLegitEmailContainingWord * totalResults)/\
                                     ((distinctWord.countLegitEmailContainingWord+distinctWord.countSpamEmailContainingWord) * (distinctWord.countLegitEmailContainingWord + distinctWord.countLegitEmailNotContainingWord)),2)
        except (ZeroDivisionError, ValueError):
            mutualInfo += 0.0

        return mutualInfo

def computeNaiveBayes(emailContent):
        #Naive Bayes: Multinomial NB, TF attributes
        emailContent = emailContent.split()
        dict_testingData = {} # dictionary of distinct words in testing data
        total_trainingEmails = len(trainSpamEmails) + len(trainLegitEmails)
        probIsSpam = len(trainSpamEmails) / total_trainingEmails
        probIsLegit = len(trainLegitEmails) / total_trainingEmails
        probWord_isPresentSpam = 1.0
        probWord_isPresentLegit = 1.0

        
        #determine whther term appeared in document

        for key in trainDistinctWords:
            if key in emailContent:
                dict_testingData[key] = 1
            else :
                dict_testingData[key] = 0

        for key in trainDistinctWords:
            # if key in self.trainingDistinctWords:
            word = trainDistinctWords[key]
            power = dict_testingData[key]

            prob_t_s = (1 + word.countSpamEmailContainingWord) / (2 + len(trainSpamEmails))
            prob_t_l = (1 + word.countLegitEmailContainingWord) / (2 + len(trainLegitEmails))

            probWord_isPresentSpam *= (math.pow(prob_t_s, power) * math.pow(1-prob_t_s, 1-power))
            probWord_isPresentLegit *= (math.pow(prob_t_l, power) * math.pow(1-prob_t_l, 1-power))

        return (probIsSpam * probWord_isPresentSpam) / (probIsSpam * probWord_isPresentSpam + probIsLegit * probWord_isPresentLegit)

#start
loadEmails('data\\lemm_stop\\part')

threshold_lambda = 999
threshold = threshold_lambda /(1+threshold_lambda)

sPrecision = 0
sRecall = 0
wAcc_b = 0
wErr_b = 0
wAcc = 0
wErr = 0
TCR = 0

for i in range(10):
    prepareTrainingSet(i)
    selectFeatures()
    
    SpamCategSpam = 0 #spam email categorized as spam
    SpamCategLegit = 0 #spam email categorized as legit
    LegitCategSpam = 0 #legit email categorized as spam
    LegitCategLegit = 0 #legit email categorized as legit

    print("Classifying testing data...[", i ,"]")

    spamSize = len(folderList[i].spamEmail)
    legitSize = len(folderList[i].legitEmail)
    print("testing size:",  spamSize + legitSize)

    for email in folderList[i].spamEmail:
        result = computeNaiveBayes(email)
        if result > threshold: #isSpam
            SpamCategSpam += 1
        else: #isLegit
            SpamCategLegit += 1

    for email in folderList[i].legitEmail:
        result = computeNaiveBayes(email)
        if result > threshold: #isSpam
            LegitCategSpam += 1
        else:
            LegitCategLegit += 1

    sPrecision += SpamCategSpam / (SpamCategSpam + LegitCategSpam)
    sRecall += SpamCategSpam / (SpamCategSpam+SpamCategLegit)
    wAcc += (threshold_lambda * LegitCategLegit + SpamCategSpam)/ (threshold_lambda * legitSize + spamSize)
    wErr += (threshold_lambda * LegitCategSpam + SpamCategLegit)/ (threshold_lambda * legitSize + spamSize)
    wAcc_b += (threshold_lambda * legitSize)/(threshold_lambda * legitSize + spamSize)
    wErr_b += spamSize / (threshold_lambda * legitSize + spamSize)
    TCR += wErr_b / wErr


print("AVG Spam Precision: ", sPrecision/10)
print("AVG Spam Precision(1-E): ", 1-wErr/10)
print("AVG Spam Recall: ", sRecall/10)
print("AVG wAcc: ", wAcc/10)
print("AVG wErr: ", wErr/10)
print("AVG wAcc_b: ", wAcc_b/10)
print("AVG wErr_b: ", wErr_b/10)
print("AVG TCR: ", TCR/10)