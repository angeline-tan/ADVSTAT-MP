import os
import math
from decimal import *
from collections import Counter

trainDistinctWords = {}
trainSpamEmails = []
trainLegitEmails = []
folderList = []
topTrainDistinctWords = {}

class Term:
    def __init__(self, content):
        self.content = content
        self.mutualInfo = 0

        self.countLegitEmailContainingWord = 0
        self.countLegitEmailNotContainingWord = 0
        
        self.countSpamEmailContainingWord = 0
        self.countSpamEmailNotContainingWord = 0
        
class Folder:
    def __init__(self):
        self.spamEmail = []
        self.legitEmail = []

    def addSpamEmail(self, email):
        self.spamEmail.append(email)

    def addLegitimateEmail(self, email):
        self.legitEmail.append(email)
        
def loadEmailsPerFolder(path):
        for i in range(1,11):
            folderPath = path + str(i)
            folder = Folder()
            print("Loading Emails in Folder ", i)
            for filename in os.listdir(folderPath):
                content = open(folderPath + '\\' + filename).read()
                if filename.startswith('sp'):
                    folder.addSpamEmail(content)
                else:
                    folder.addLegitimateEmail(content)

            folderList.append(folder)

def getDistinctWordsInTrainingSet(testingIndex):
        global trainDistinctWords
        global trainSpamEmails
        global trainLegitEmails
        
        trainDistinctWords = {}
        trainSpamEmails = []
        trainLegitEmails = []
        
        listOfWordsInEmail = []
        listOfWordsInLegitEmail = []
        listOfWordsInSpamEmail = []
        
        print("Finding distinct words and counting frequency")
        for i in range(len(folderList)):
            if i != testingIndex:
                print("Processing Emails in Folder ",i)
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
            word = Term(token)
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
                word = Term(token)
                word.countSpamEmailContainingWord = count  
                trainDistinctWords[token] = word
            else : 
                word = trainDistinctWords.get(token)
                word.countSpamEmailContainingWord = count 
        
        for wo in trainDistinctWords:
                trainDistinctWords[wo].countLegitEmailNotContainingWord = len(trainLegitEmails) - trainDistinctWords[wo].countLegitEmailContainingWord
        
        for wo in trainDistinctWords:
                trainDistinctWords[wo].countSpamEmailNotContainingWord = len(trainSpamEmails) - trainDistinctWords[wo].countSpamEmailContainingWord
        
        print("Distinct words: ", len(trainDistinctWords))

def selectFeatures(numAttribute):
        print("Performing feature selection for ", numAttribute, "attribute")
        global trainDistinctWords
        global topTrainDistinctWords
        
        topTrainDistinctWords = {}
        
        for k in trainDistinctWords:
            trainDistinctWords[k].mutualInfo = getMutualInfo(trainDistinctWords[k])

        topTrainDistinctWords = sorted(trainDistinctWords.items(), key=lambda x:x[1].mutualInfo, reverse = True)[:numAttribute]


        topTrainDistinctWords = {x[0]: x[1] for x in topTrainDistinctWords}

def getMutualInfo(word):
        totalResults = word.countLegitEmailContainingWord + word.countLegitEmailNotContainingWord + word.countSpamEmailContainingWord + word.countSpamEmailNotContainingWord

        try:
            # P(x=0,c=spam)
            mutualInfo = (word.countSpamEmailNotContainingWord / totalResults) * math.log((word.countSpamEmailNotContainingWord * totalResults) / ((word.countSpamEmailNotContainingWord + word.countLegitEmailNotContainingWord) * (word.countSpamEmailNotContainingWord + word.countSpamEmailContainingWord)), 2)

        except (ZeroDivisionError, ValueError):
            mutualInfo = 0.0
   
        try:
            # P(x=0,c=legitimate)
            mutualInfo += (word.countLegitEmailNotContainingWord / totalResults) * math.log((word.countLegitEmailNotContainingWord * totalResults) / ((word.countLegitEmailNotContainingWord + word.countSpamEmailNotContainingWord) * (word.countLegitEmailNotContainingWord + word.countLegitEmailContainingWord)), 2)

        except (ZeroDivisionError, ValueError):
            mutualInfo += 0.0
        
        try:
            # P(x=1,c=spam)
            mutualInfo += (word.countSpamEmailContainingWord / totalResults) * math.log((word.countSpamEmailContainingWord * totalResults) / ((word.countSpamEmailContainingWord + word.countLegitEmailContainingWord) * (word.countSpamEmailContainingWord + word.countSpamEmailNotContainingWord)), 2)
        except (ZeroDivisionError, ValueError):
            mutualInfo += 0.0
       
        try:
            # P(x=1,c=legitimate)
            mutualInfo += (word.countLegitEmailContainingWord / totalResults) * math.log((word.countLegitEmailContainingWord * totalResults) / ((word.countLegitEmailContainingWord + word.countSpamEmailContainingWord) * (word.countLegitEmailContainingWord + word.countLegitEmailNotContainingWord)), 2)
        except (ZeroDivisionError, ValueError):
            mutualInfo += 0.0

        return mutualInfo

def naiveBayes(emailData):
        emailData = emailData.split()
        distinctWordsTesting = {} # list of distinct words for testing
        totalTrainedEmails = len(trainSpamEmails) + len(trainLegitEmails)
        spamProbabilityofEmail = len(trainSpamEmails) / totalTrainedEmails
        legitProbabilityOfEmail = len(trainLegitEmails) / totalTrainedEmails
        wordProbabilityIsInSpam = 1.0
        wordProbabilityIsInLegit = 1.0
        
        #identify when a word appears in a document
        for token in topTrainDistinctWords:
            if token not in emailData:
                distinctWordsTesting[token] = 0
            else :
                distinctWordsTesting[token] = 1

        for token in topTrainDistinctWords:
            power = distinctWordsTesting[token]
            word = topTrainDistinctWords[token]

            probTLegit = (1 + word.countLegitEmailContainingWord) / (2 + len(trainLegitEmails))
            probTSpam = (1 + word.countSpamEmailContainingWord) / (2 + len(trainSpamEmails))

            wordProbabilityIsInLegit *= (math.pow(probTLegit, power) * math.pow(1-probTLegit, 1-power))
            wordProbabilityIsInSpam *= (math.pow(probTSpam, power) * math.pow(1-probTSpam, 1-power))

        return (wordProbabilityIsInSpam * spamProbabilityofEmail) / (wordProbabilityIsInSpam * spamProbabilityofEmail + wordProbabilityIsInLegit *legitProbabilityOfEmail)

#start
def getCertainResult(folderName, numAttribute, thresh):
    spamPrecision = 0
    spamRecall = 0
    baselineWeightedAccuracy = 0
    weightedAccuracy = 0
    TCR = 0
    threshold_lambda = thresh
    threshold = threshold_lambda /(1+threshold_lambda)
    
    loadEmailsPerFolder('data\\'+ folderName+'\\part')
    for i in range(10):
        getDistinctWordsInTrainingSet(i)
        
        print("Test Folder: ", i)
        
        selectFeatures(numAttribute)
        SpamCategSpam = 0 #spam email categorized as spam
        SpamCategLegit = 0 #spam email categorized as legit
        LegitCategSpam = 0 #legit email categorized as spam
        LegitCategLegit = 0 #legit email categorized as legit
    
        spamSize = len(folderList[i].spamEmail)
        legitSize = len(folderList[i].legitEmail)
            
        for email in folderList[i].spamEmail:
            result = naiveBayes(email)
            if result > threshold: #isSpam
                SpamCategSpam += 1
            else: #isLegit
                SpamCategLegit += 1
    
        for email in folderList[i].legitEmail:
            result = naiveBayes(email)
            if result > threshold: #isSpam
                LegitCategSpam += 1
            else:
                LegitCategLegit += 1
    
        spamPrecision += SpamCategSpam / (SpamCategSpam + LegitCategSpam)
        spamRecall += SpamCategSpam / (SpamCategSpam+SpamCategLegit)
        weightedAccuracy += (threshold_lambda * LegitCategLegit + SpamCategSpam)/ (threshold_lambda * legitSize + spamSize)
        baselineWeightedAccuracy += (threshold_lambda * legitSize)/(threshold_lambda * legitSize + spamSize)
        TCR += spamSize / (threshold_lambda* LegitCategSpam + SpamCategLegit)
        
    print()
    print("Result: ")
    print("Folder Name: " + folderName)
    print("Number of Attribute: ", numAttribute, "Threshold: ", thresh)
    print ("AVG Spam Recall", (spamRecall/10) *100)
    print("AVG Spam Precision", (spamPrecision/10) *100)
    print ("AVG Weighted Accuracy", (weightedAccuracy/10) *100)
    print ("AVG Baseline Weighted Accuracy", (baselineWeightedAccuracy/10) *100) 
    print ("AVG TCR", TCR /10)
    print()
        
def getAllResult():
    folderNames = ['bare', 'lemm', 'lemm_stop', 'stop']
    
    for n in folderNames:
        loadEmailsPerFolder('data\\' + n + '\\part')
    
        threshold_list = [1, 9, 999]
        result_list = {}
        
        for i in range(10):
            getDistinctWordsInTrainingSet(i)
            print("Test Folder: ", i)
            
            for x in range(50,750,50):
                selectFeatures(x)
                SpamCategSpam = 0 #spam email categorized as spam
                SpamCategLegit = 0 #spam email categorized as legit
                LegitCategSpam = 0 #legit email categorized as spam
                LegitCategLegit = 0 #legit email categorized as legit
            
                spamSize = len(folderList[i].spamEmail)
                legitSize = len(folderList[i].legitEmail)
                
                for y in threshold_list:
                    if i == 0:
                        spamPrecision = 0
                        spamRecall = 0
                        baselineWeightedAccuracy = 0
                        weightedAccuracy = 0
                        TCR = 0
                    else:
                        spamPrecision = result_list["spamPrecision" + str(x) + str(y)]
                        spamRecall = result_list["spamRecall" + str(x) + str(y)]
                        weightedAccuracy = result_list["weightedAccuracy" + str(x) + str(y)]
                        baselineWeightedAccuracy = result_list["baselineWeightedAccuracy" + str(x) + str(y)]
                        TCR = result_list["TCR" + str(x) + str(y)]
                        
                    threshold_lambda = y
                    threshold = threshold_lambda /(1+threshold_lambda)
                    for email in folderList[i].spamEmail:
                        result = naiveBayes(email)
                        if result > threshold: #isSpam
                            SpamCategSpam += 1
                        else: #isLegit
                            SpamCategLegit += 1
                
                    for email in folderList[i].legitEmail:
                        result = naiveBayes(email)
                        if result > threshold: #isSpam
                            LegitCategSpam += 1
                        else:
                            LegitCategLegit += 1
                
                    spamPrecision += SpamCategSpam / (SpamCategSpam + LegitCategSpam)
                    spamRecall += SpamCategSpam / (SpamCategSpam+SpamCategLegit)
                    weightedAccuracy += (threshold_lambda * LegitCategLegit + SpamCategSpam)/ (threshold_lambda * legitSize + spamSize)
                    baselineWeightedAccuracy += (threshold_lambda * legitSize)/(threshold_lambda * legitSize + spamSize)
                    TCR += spamSize / (threshold_lambda* LegitCategSpam + SpamCategLegit)
                    
                    result_list["spamPrecision" + str(x) + str(y)] = spamPrecision
                    result_list["spamRecall" + str(x) + str(y)] = spamRecall
                    result_list["weightedAccuracy" + str(x) + str(y)] = weightedAccuracy
                    result_list["baselineWeightedAccuracy" + str(x) + str(y)] = baselineWeightedAccuracy
                    result_list["TCR" + str(x) + str(y)] = TCR
        print()
        print("Folder Name: " + n)            
        for x in range(50,750,50):
            for y in threshold_list:
                    print("Number of Attribute: ", x, "Threshold: ", y)
                    print ("AVG Spam Recall", (result_list["spamRecall" + str(x) + str(y)]/10) *100)
                    print("AVG Spam Precision", (result_list["spamPrecision" + str(x) + str(y)]/10) *100)
                    print ("AVG Weighted Accuracy", (result_list["weightedAccuracy" + str(x) + str(y)]/10) *100)
                    print ("AVG Baseline Weighted Accuracy", (result_list["baselineWeightedAccuracy" + str(x) + str(y)]/10) *100) 
                    print ("AVG TCR", result_list["TCR" + str(x) + str(y)] /10)
                    print()
                    
getCertainResult('bare',50, 1)
getCertainResult('stop',50, 1)
getCertainResult('lemm',100, 1)
getCertainResult('lemm_stop',100, 1)
getCertainResult('bare',200, 9)
getCertainResult('stop',200, 9)
getCertainResult('lemm',100, 9)
getCertainResult('lemm_stop',100, 9)
getCertainResult('bare',200, 999)
getCertainResult('stop',200, 999)
getCertainResult('lemm',300, 999)
getCertainResult('lemm_stop',300, 999)

#getAllResult()
                