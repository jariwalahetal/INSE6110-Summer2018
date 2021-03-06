import matplotlib.pyplot as plt
import numpy as np
import tarfile
import os
import re
from datetime import datetime
from bs4 import BeautifulSoup

# Sklearn library for metrics
from sklearn.metrics import accuracy_score, confusion_matrix

# Sklearn library for preprocessing
from sklearn.model_selection import train_test_split, GridSearchCV

# Bag of words vectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

from sklearn.neighbors import KNeighborsClassifier

from sklearn.pipeline import Pipeline
import warnings
import csv

from stemming.porter2 import stem

SpamCounts = 0
HamCounts = 0
TotalCounts = 0

BagOfWords = ['offer','free','dollar','win','order','business','lottery', 'mail']
BagOfWordsCount = [0,0,0,0,0,0,0,0]
BagOfWordsCountForCount = [0,0,0,0,0,0,0,0]


PreprocessFileName1 = "IntermediatePreprocessDataForSpamAssassin.csv"
MAX_TRIAL = 7

def parse_prefix(line, fmt):
    try:
        t = datetime.strptime(line, fmt)
    except ValueError as v:
        if len(v.args) > 0 and v.args[0].startswith('unconverted data remains: '):
            line = line[:-(len(v.args[0]) - 26)]
            t = datetime.strptime(line, fmt)
        else:
            raise
    return t

def Get_URLS(string):
    # findall() has been used
    # with valid conditions for urls in string
    url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)
    return url

def Get_Time(string, trial,org):
    stringDate = string.replace(',', '', 100).replace(';','',100).strip()
    if(trial > 1):
        #remove timezone info
        stringDate = stringDate.split('(', 1)[0].strip()
        dateParts = stringDate.split(' ')
        stringDate = ' '.join(dateParts[:-1])

    if(trial == MAX_TRIAL):
        #print(org)
        return "XXXXXXXXXX"

    try:
        datetime_object = parse_prefix(stringDate, '%d %b %Y %X')
        return  datetime_object.time().strftime('%H.%M')
    except:
        try:
            datetime_object = parse_prefix(stringDate, '%a %d %b %Y %X')
            return datetime_object.time().strftime('%H.%M')
        except:
            try:
                datetime_object = parse_prefix(stringDate, '%a %d %b %Y %H:%M')
                return datetime_object.time().strftime('%H.%M')
            except:
                try:
                    datetime_object = parse_prefix(stringDate, '%Y-%m-%dt%X')
                    return datetime_object.time().strftime('%H.%M')
                except:
                    try:
                        datetime_object = parse_prefix(stringDate, '%a %d %b %y %H:%M')
                        return datetime_object.time().strftime('%H.%M')
                    except:
                        try:
                            datetime_object = parse_prefix(stringDate, '%Y/%m/%d %a %X')
                            return datetime_object.time().strftime('%H.%M')
                        except:
                            try:
                                datetime_object = parse_prefix(stringDate, '%Y/%m/%d %a %H:%M')
                                return datetime_object.time().strftime('%H.%M')
                            except:
                                try:
                                    datetime_object = parse_prefix(stringDate, '%a %b %d %X %Y')
                                    return datetime_object.time().strftime('%H.%M')
                                except:
                                    try:
                                        datetime_object = parse_prefix(stringDate, '%a %b %d %H:%M %Y')
                                        return datetime_object.time().strftime('%H.%M')
                                    except:
                                        try:
                                            datetime_object = parse_prefix(stringDate, '%d %b %y %X')
                                            return datetime_object.time().strftime('%H.%M')
                                        except:
                                            try:
                                                datetime_object = parse_prefix(stringDate, '%d %b %y %H:%M')
                                                return datetime_object.time().strftime('%H.%M')
                                            except:
                                                try:
                                                    datetime_object = parse_prefix(stringDate, '%a%d %b %Y %X')
                                                    return datetime_object.time().strftime('%H.%M')
                                                except:
                                                    try:
                                                        datetime_object = parse_prefix(stringDate, '%a%d %b %Y %H:%M')
                                                        return datetime_object.time().strftime('%H.%M')
                                                    except:
                                                        try:
                                                            datetime_object = parse_prefix(stringDate, '%Y-%m-%dt%H:%M')
                                                            return datetime_object.time().strftime('%H.%M')
                                                        except:
                                                            try:
                                                                datetime_object = parse_prefix(stringDate,
                                                                                               '%d/%m/%Y %X')
                                                                return datetime_object.time().strftime('%H.%M')
                                                            except:
                                                                try:
                                                                    datetime_object = parse_prefix(stringDate,
                                                                                                   '%d/%m/%Y %H:%M')
                                                                    return datetime_object.time().strftime('%H.%M')
                                                                except:
                                                                    try:
                                                                        datetime_object = parse_prefix(stringDate,
                                                                                                       '%a %b %d %Y %X')
                                                                        return datetime_object.time().strftime('%H.%M')
                                                                    except:
                                                                        return Get_Time(stringDate,trial + 1,org)

def process_foler(path,isSpam):
    global SpamCounts
    global HamCounts
    global TotalCounts
    """Get the text of every mail in a given directory."""
    texts = []
    files = os.listdir(path)
    for file in files:
        dateString = "temp"
        with open(os.path.join(path, file), encoding='utf8', errors='ignore') as f:
            content = f.read()
            soup = BeautifulSoup(content, 'html.parser')
            content = soup.get_text()
            obj = process_count(content, isSpam)
            dateString = obj.get('sentDate')
            BagOfWordsCount = obj.get('wordsCount')

        no_of_url = len(Get_URLS(content))
        dateString = Get_Time(str(dateString),1,str(dateString))

        if (dateString != "XXXXXXXXXX"):
            with open("IntermediatePreprocessDataForSpamAssassin.csv",mode='a+') as p:
                p.write(file)
                #print(BagOfWordsCount)
                idx = 0
                for c in BagOfWordsCount:
                    p.write(",")
                    p.write(str(c))
                    #increse the respective word's count
                    BagOfWordsCountForCount[idx] += 1
                    idx = idx + 1
                p.write(",")
                p.write(str(no_of_url))
                p.write(",")
                p.write(dateString)
                p.write(",")
                p.write(str(isSpam))
                p.write("\n")
                if(isSpam):
                    SpamCounts += 1
                else:
                    HamCounts += 1
                TotalCounts += 1
    return texts

def process_count(content, isSpam):
    lines = content.split("\n")
    datestring = 'XXXXXXXXXX'
    BagOfWordsCount = [0,0,0,0,0,0,0,0]
    for l in lines:
        #trim whitespaces and tabs
        l = l.replace("\t","").strip()
        if(l.lower().startswith("date:")):
            datestring = l.lower().replace("date:","").strip()
        words = l.split()
        for w in words:
            stemword = stem(w)
            if (w.lower() in BagOfWords):
                idx = BagOfWords.index(w.lower())
                BagOfWordsCount[idx] += 1
            elif(stemword in BagOfWords):
                idx = BagOfWords.index(stemword)
                BagOfWordsCount[idx] += 1

    return {'sentDate':datestring,'wordsCount':BagOfWordsCount}

def generateProbability(totalCount, categoryCount, totalMyCount, myCount):
    P_word_category = totalMyCount / categoryCount
    P_category = categoryCount / totalCount
    P_word = myCount / totalCount
    if myCount == 0:
        return 0
    else:
        return round((P_word_category * P_category) / P_word,2)

def StartPreprocessing():
    global SpamCounts
    global HamCounts
    global TotalCounts
    #Extract the spam tar.bz2 file and create a new directory containing the spam archive
    tar = tarfile.open("E:/INSE 6180/20021010_spam.tar.bz2", "r:bz2")
    tar.extractall("E:/INSE 6180/data/spam")
    tar.close()
    tar = tarfile.open("E:/INSE 6180/20030228_spam.tar.bz2", "r:bz2")
    tar.extractall("E:/INSE 6180/data/spam")
    tar.close()
    tar = tarfile.open("E:/INSE 6180/20050311_spam_2.tar.bz2", "r:bz2")
    tar.extractall("E:/INSE 6180/data/spam")
    tar.close()

    # Extract the spam tar.bz2 file and create a new directory containing the spam archive
    tar = tarfile.open("E:/INSE 6180/20021010_easy_ham.tar.bz2", "r:bz2")
    tar.extractall("E:/INSE 6180/data/ham")
    tar.close()
    tar = tarfile.open("E:/INSE 6180/20021010_hard_ham.tar.bz2", "r:bz2")
    tar.extractall("E:/INSE 6180/data/ham")
    tar.close()
    tar = tarfile.open("E:/INSE 6180/20030228_easy_ham.tar.bz2", "r:bz2")
    tar.extractall("E:/INSE 6180/data/ham")
    tar.close()
    tar = tarfile.open("E:/INSE 6180/20030228_easy_ham_2.tar.bz2", "r:bz2")
    tar.extractall("E:/INSE 6180/data/ham")
    tar.close()
    tar = tarfile.open("E:/INSE 6180/20030228_hard_ham.tar.bz2", "r:bz2")
    tar.extractall("E:/INSE 6180/data/ham")
    tar.close()

    with open("IntermediatePreprocessDataForSpamAssassin.csv",mode='w') as p:
        print("Emptied the preprocessed file")



    # Get text from every document in spam
    spam_path1 = 'E:/INSE 6180/data/spam/spam'
    spam_path2 = 'E:/INSE 6180/data/spam/spam_2'
    spam_content = process_foler(spam_path1,1)
    print("Processed ", spam_path1)
    spam_content = process_foler(spam_path2,1)
    print("Processed ", spam_path2)

    ham_path1 = 'E:/INSE 6180/data/ham/easy_ham'
    ham_path2 = 'E:/INSE 6180/data/ham/easy_ham_2'
    ham_path3 = 'E:/INSE 6180/data/ham/hard_ham'
    ham_content = process_foler(ham_path1,0)
    print("Processed ", ham_path1)
    ham_content = process_foler(ham_path2,0)
    print("Processed ", ham_path2)
    ham_content = process_foler(ham_path3,0)
    print("Processed ", ham_path3)

    print(SpamCounts)
    print(HamCounts)
    print(TotalCounts)

    p_BagOfWordsCountForCount_spam = [BagOfWordsCountForCount[0]/SpamCounts,
                                 BagOfWordsCountForCount[1] / SpamCounts,
                                 BagOfWordsCountForCount[2] / SpamCounts,
                                 BagOfWordsCountForCount[3] / SpamCounts,
                                 BagOfWordsCountForCount[4] / SpamCounts,
                                 BagOfWordsCountForCount[5] / SpamCounts,
                                 BagOfWordsCountForCount[6] / SpamCounts,
                                 BagOfWordsCountForCount[7] / SpamCounts]

    p_BagOfWordsCountForCount_ham = [BagOfWordsCountForCount[0] / HamCounts,
                                      BagOfWordsCountForCount[1] / HamCounts,
                                      BagOfWordsCountForCount[2] / HamCounts,
                                      BagOfWordsCountForCount[3] / HamCounts,
                                      BagOfWordsCountForCount[4] / HamCounts,
                                      BagOfWordsCountForCount[5] / HamCounts,
                                      BagOfWordsCountForCount[6] / HamCounts,
                                      BagOfWordsCountForCount[7] / HamCounts]

    p_spam = SpamCounts / TotalCounts
    p_ham = HamCounts / TotalCounts

    with open("FinalPreprocessDataForSpamAssassin.csv",mode='w') as p:
        p.write("offer_count,free_count,dollar_count,win_count,order_count,business_count,lottery_count, mail_count,no_of_url,time_of_email,Spam\n")
        with open(PreprocessFileName1) as f:
            for line in f:
                # print(line)
                seprated = line.split(",")
                #p.write(seprated[0])
                #p.write(",")
                #P(offer/spam or ham)
                if(seprated[11] == '1\n'):
                    p.write(str(generateProbability(TotalCounts, SpamCounts,p_BagOfWordsCountForCount_spam[0],(int(seprated[1])))))
                    p.write(",")
                    # P(free/spam)
                    p.write(str(generateProbability(TotalCounts, SpamCounts,p_BagOfWordsCountForCount_spam[1],(int(seprated[2])))))
                    p.write(",")
                    # P(dollar/spam)
                    p.write(str(generateProbability(TotalCounts, SpamCounts,p_BagOfWordsCountForCount_spam[2],(int(seprated[3])))))
                    p.write(",")
                    # P(win/spam)
                    p.write(str(generateProbability(TotalCounts, SpamCounts,p_BagOfWordsCountForCount_spam[3],(int(seprated[4])))))
                    p.write(",")
                    # P(order/spam)
                    p.write(str(generateProbability(TotalCounts, SpamCounts,p_BagOfWordsCountForCount_spam[4],(int(seprated[5])))))
                    p.write(",")
                    # P(Business/spam)
                    p.write(str(generateProbability(TotalCounts, SpamCounts,p_BagOfWordsCountForCount_spam[5],(int(seprated[6])))))
                    p.write(",")
                    # P(Lottery/spam)
                    p.write(str(generateProbability(TotalCounts, SpamCounts,p_BagOfWordsCountForCount_spam[6],(int(seprated[7])))))
                    p.write(",")
                    # P(Mail/spam)
                    p.write(str(generateProbability(TotalCounts, SpamCounts,p_BagOfWordsCountForCount_spam[7],(int(seprated[8])))))
                    p.write(",")
                else:
                    p.write(str(generateProbability(TotalCounts, HamCounts, p_BagOfWordsCountForCount_ham[0],(int(seprated[1])))))
                    p.write(",")
                    # P(free/spam)
                    p.write(str(generateProbability(TotalCounts, HamCounts, p_BagOfWordsCountForCount_ham[1],(int(seprated[2])))))
                    p.write(",")
                    # P(dollar/spam)
                    p.write(str(generateProbability(TotalCounts, HamCounts, p_BagOfWordsCountForCount_ham[2],(int(seprated[3])))))
                    p.write(",")
                    # P(win/spam)
                    p.write(str(generateProbability(TotalCounts, HamCounts, p_BagOfWordsCountForCount_ham[3],(int(seprated[4])))))
                    p.write(",")
                    # P(order/spam)
                    p.write(str(generateProbability(TotalCounts, HamCounts, p_BagOfWordsCountForCount_ham[4],(int(seprated[5])))))
                    p.write(",")
                    # P(Business/spam)
                    p.write(str(generateProbability(TotalCounts, HamCounts, p_BagOfWordsCountForCount_ham[5],(int(seprated[6])))))
                    p.write(",")
                    # P(Lottery/spam)C
                    p.write(str(generateProbability(TotalCounts, HamCounts, p_BagOfWordsCountForCount_ham[6],(int(seprated[7])))))
                    p.write(",")
                    # P(Mail/spam)
                    p.write(str(generateProbability(TotalCounts, HamCounts, p_BagOfWordsCountForCount_ham[7],(int(seprated[8])))))
                    p.write(",")
                # url count
                p.write(seprated[9])
                p.write(",")
                # time
                p.write(seprated[10])
                p.write(",")
                #is spam or not
                p.write(seprated[11])
