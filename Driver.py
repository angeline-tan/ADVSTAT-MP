import os
#from __builtin__ import file

#import nltk

SPAM = 'sp'
LEGITIMATE = "lg"

# 1 string = 1 email
testData = [] #testing emails
emailContents = []
#bareEmails = []
#lemmEmails = []
#lemm_stopEmails = []
#stopEmails = []
spamEmails = []
legitEmails = []
wordBank = []

# loads jth part of an email folder j (part 1 of folder 1 (bare))
def loadEmails(i, j):
    if i == 1:
        path = 'data\\bare\\part' + str(j) + '\\'
    elif i == 2:
        path = 'data\\lemm\\part' + str(j) + '\\'
    elif i == 3:
        path = 'data\\lemm_stop\\part' + str(j) + '\\'
    else:
        path = 'data\\stop\\part' + str(j) + '\\'
    file_list = os.listdir(path)
    
    for filename in file_list:
        file = open(path + filename, 'r')
        content = file.read()
        
        if filename.startswith(SPAM):
            spamEmails.append(file)
        else:
            legitEmails.append(file)
        #print content
        #if i == 1:
            #bareEmails.append(content)
        #elif i == 2:
            #lemmEmails.append(content)
        #elif i == 3:
            #lemm_stopEmails.append(content)
        #else:
            #stopEmails.append(content)
        if j == 1:
            testData.append(content) # to be used later for the validation & training part
        emailContents.append(content)
        #print ("***********************************\n")
        file.close()
        

# iterates through all emails and gets each word, ignores duplicates
def createWordList():
    for i in range(0, emailContents.__len__()):
        emailContents[i]

# ----------------------- MAIN ----------------------------
# loads emails from all folders (bare, lemm, lemm_stop, stop)
for i in range(1, 5):
    if i == 1:
        print("Loading bare folder")
    elif i == 2:
        print("Loading lemm folder")
    elif i == 3:
        print("Loading lemm_stop folder")
    else:
        print("Loading stop folder")
    for j in range(1, 11):
        print("  Loading part" + str(j))
        loadEmails(i, j)

