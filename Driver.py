import os
import math
from decimal import *
from collections import Counter

trainDistinctWords = {}
trainSpamEmails = []
trainLegitEmails = []
folderList = []
topTrainDistinctWords = {}

class Word:
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

        for key in topTrainDistinctWords:
            if key in emailContent:
                dict_testingData[key] = 1
            else :
                dict_testingData[key] = 0

        for key in topTrainDistinctWords:
            # if key in self.trainingDistinctWords:
            word = topTrainDistinctWords[key]
            power = dict_testingData[key]

            prob_t_s = (1 + word.countSpamEmailContainingWord) / (2 + len(trainSpamEmails))
            prob_t_l = (1 + word.countLegitEmailContainingWord) / (2 + len(trainLegitEmails))

            probWord_isPresentSpam *= (math.pow(prob_t_s, power) * math.pow(1-prob_t_s, 1-power))
            probWord_isPresentLegit *= (math.pow(prob_t_l, power) * math.pow(1-prob_t_l, 1-power))

        return (probIsSpam * probWord_isPresentSpam) / (probIsSpam * probWord_isPresentSpam + probIsLegit * probWord_isPresentLegit)

#start
loadEmailsPerFolder('data\\bare\\part')

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
            
for x in range(50,750,50):
    for y in threshold_list:
            print("Number of Attribute: ", x, "Threshold: ", y)
            print("AVG Spam Precision", (result_list["spamPrecision" + str(x) + str(y)]/10) *100)
            print ("AVG Spam Recall", (result_list["spamRecall" + str(x) + str(y)]/10) *100)
            print ("AVG Weighted Accuracy", (result_list["weightedAccuracy" + str(x) + str(y)]/10) *100)
            print ("AVG Baseline Weighted Accuracy", (result_list["baselineWeightedAccuracy" + str(x) + str(y)]/10) *100) 
            print ("AVG TCR", result_list["TCR" + str(x) + str(y)] /10)
            print()
            