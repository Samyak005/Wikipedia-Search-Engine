# Indexer4 - removed reduntant code for performance optimisation
import sys
import heapq
from collections import defaultdict
import re
import os
import xml.sax
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer as Stemmer
import timeit
import string

stemmer = Stemmer('english')
NUMPAGES_IN_PREINDEX = 15000
DICTIONARYSUBDIV = 50000
debug = 0
dictID = {}

# global number_of_unique_unstemmed_words
# number_of_unique_unstemmed_words = set()

start = timeit.default_timer()

termFrequencyInCorpus = defaultdict(int)

fileCount = 0
pageCount = 0
offset = 0

def writeFile(field, data, filecount):
    offset = []
    offsetSize =0
    filename = sys.argv[2] + '/' + field + str(filecount) + '.txt'
    with open(filename, 'w') as f:
        for key in sorted(data.keys()):
            offset.append(str(offsetSize))       
            f.write(key)
            offsetSize += len(key)
            for page in data[key]:
                page = re.sub(r'\$', r' ', page)
                f.write(' '+page)
                offsetSize += len(page)+1
            f.write('\n')
            offsetSize +=1

    filename = sys.argv[2] + '/offset_' + field+ str(filecount) +'.txt'
    with open(filename, 'w') as f:
        f.write('\n'.join(offset))   
    return filecount+1


# This function reads all the partial indexes and merges them
# Use heap to read the words from each index and then call FinalIndex in a sorted order
def mergeFiles(fileCount, fieldindicator):
    distinctWords = defaultdict(list)
    wordsTopLine = {}
    files = {}
    topLine = {}
    flag = [0] * fileCount
    data = defaultdict(list)
    heap = []
    termFrequencyInCorpus = 0
    # finalFileCount refers to file count in final i.e. global index which is obtained after merging
    finalFileCount = 0

    for i in range(fileCount):
        filename = sys.argv[2] + '/index' + str(fieldindicator) + str(i) + '.txt'
        # print(filename)
        files[i] = open(filename, 'r')
        flag[i] = 1
        topLine[i] = files[i].readline().strip()
        if topLine[i] != '':
            wordsTopLine[i] = topLine[i].split()
            if wordsTopLine[i][0] not in heap:
                heapq.heappush(heap, wordsTopLine[i][0])
        else:
            flag[i] = 0
    count = 0
    while any(flag) == 1:
        temp = heapq.heappop(heap)
        count += 1
        # print(count)
        if count%DICTIONARYSUBDIV == 0:
            oldFileCount = finalFileCount
            finalFileCount = writeFile(fieldindicator, data, finalFileCount)   
            if oldFileCount != finalFileCount:
                data = defaultdict(list)

            with open(sys.argv[2] + '/vocab'+fieldindicator+'.txt', 'a') as f:
                for key in sorted(distinctWords.keys()):
                    f.write(distinctWords[key])
                    f.write('\n')
            distinctWords = defaultdict(list)

        for i in range(fileCount):
            if flag[i]:
                if wordsTopLine[i][0] == temp:
                    data[temp].extend(wordsTopLine[i][1:])
                    # print(data[temp], '\n')   
                    topLine[i] = files[i].readline().strip()
                    if topLine[i] == '':
                        flag[i] = 0
                        files[i].close()
                        # os.remove(sys.argv[2]+'/index' + str(fieldindicator)+ str(i) + '.txt')
                    else:
                        wordsTopLine[i] = topLine[i].split()
                        if wordsTopLine[i][0] not in heap:
                            heapq.heappush(heap, wordsTopLine[i][0])

        termFrequencyInCorpus = 0
        uniqueDocsInCorpus = 0
        # For printing the distinct words in the vocabulary of the Field
        for i in range(0, len(data[temp]), 1):
            np = data[temp][i].split('$')
            termFrequencyInCorpus += int(np[1])
            uniqueDocsInCorpus += 1
        vocabRecord = temp + ' ' + str(termFrequencyInCorpus) + ' '+ str(uniqueDocsInCorpus)+ ' '+ str(finalFileCount)
        distinctWords[temp] = vocabRecord


    finalFileCount = writeFile(fieldindicator, data, finalFileCount)
    print("unique words in", fieldindicator, count)

    with open(sys.argv[2] + '/vocab'+fieldindicator+'.txt', 'a') as f:
        for key in sorted(distinctWords.keys()):
            f.write(distinctWords[key])
            f.write('\n')

    return count

# This function reads all the field level Vocab files and merges them
def mergeVocabFiles():

    FIELDS = ['b','t','c','i','r','l']
    fieldcount = len(FIELDS)

    # for storing vocab in distinctWords and their offset
    offset = []
    distinctWords = []

    wordlength= 0
    wordsTopLine = {}
    # for k way merge variables to store flags and heap
    files = {}
    topLine = {}
    flag = [0] * fieldcount
    heap = []

    offsetSize = 0
    termFrequencyInCorpus = 0
    data = []   

    for i in range(fieldcount):
        fieldindicator = FIELDS[i]
        filename = sys.argv[2] + '/vocab' + str(fieldindicator) + '.txt'
        # print(filename)
        files[i] = open(filename, 'r')
        flag[i] = 1
        topLine[i] = files[i].readline().strip()
        if topLine[i] != '':
            wordsTopLine[i] = topLine[i].split()
            if wordsTopLine[i][0] not in heap:
                heapq.heappush(heap, wordsTopLine[i][0])
        else:
            flag[i] = 0

    count = 0
    prevCharOfVocab = '0'
    while any(flag) == 1:
        temp = heapq.heappop(heap)
        count += 1
        termFrequencyInCorpus = 0
        data = []
        uniqueDocsInCorpus =[]     
        # print(count)
        for i in range(fieldcount):
            fieldindicator = FIELDS[i]
            if flag[i]:
                if wordsTopLine[i][0] == temp:
                    data.append(wordsTopLine[i][3])
                    termFrequencyInCorpus += int(wordsTopLine[i][1])
                    uniqueDocsInCorpus.append(wordsTopLine[i][2])

                    topLine[i] = files[i].readline().strip()
                    if topLine[i] == '':
                        flag[i] = 0
                        files[i].close()
                        # os.remove(sys.argv[2]+'/vocab' + str(fieldindicator)+ '.txt')
                    else:
                        wordsTopLine[i] = topLine[i].split()
                        if wordsTopLine[i][0] not in heap:
                            heapq.heappush(heap, wordsTopLine[i][0])
                else:
                    data.append("$")
                    uniqueDocsInCorpus.append("$")
            else:
                data.append("$")
                uniqueDocsInCorpus.append("$")

        currentCharOfVocab = temp[0]
        # keep writing to file to keep RAM requirement in check
        if currentCharOfVocab != prevCharOfVocab:
            with open(sys.argv[2] + '/mergedvocab'+ prevCharOfVocab +'.txt', 'a') as f:
                f.write('\n'.join(distinctWords))
                f.write('\n')
                f.close()
            filename = sys.argv[2] + '/vocaboffset'+ prevCharOfVocab + '.txt'
            with open(filename, 'a') as f:
                f.write('\n'.join(offset))  
                f.write('\n')                 
                f.close()
            distinctWords = []
            offset = []
            prevCharOfVocab = currentCharOfVocab
            offsetSize = 0

        vocabRecord = temp + ' ' + str(termFrequencyInCorpus)+' '+ ' '.join(uniqueDocsInCorpus)+ ' ' + ' '.join(data)
        wordlength += len(temp)
        distinctWords.append(vocabRecord)   
        offset.append(str(offsetSize))
        offsetSize += len(vocabRecord)+1
    # print("unique vocab count", count, wordlength, offsetSize)

    with open(sys.argv[2] + '/mergedvocab'+ prevCharOfVocab +'.txt', 'a') as f:
        f.write('\n'.join(distinctWords))
        f.write('\n')

    filename = sys.argv[2] + '/vocaboffset'+ prevCharOfVocab + '.txt'
    with open(filename, 'a') as f:
        f.write('\n'.join(offset))   

    return count



class Parser():

    if __name__ == '__main__':

        fileCount = 1426
        pageCount = 21384756
        # fileCount = 4
        # pageCount = 52612        
        # fileCount = 1
        # pageCount = 93          
        currenttime = timeit.default_timer()
        print ("pagecount", pageCount, "filecount", fileCount, "before merge", currenttime - start)

        finalVocabCount = mergeFiles(fileCount, 'r')
        finalVocabCount  = mergeFiles(fileCount, 't' )
        finalVocabCount  = mergeFiles(fileCount, 'l' )
        finalVocabCount  = mergeFiles(fileCount, 'b' )
        finalVocabCount  = mergeFiles(fileCount, 'c' )
        finalVocabCount  = mergeFiles(fileCount, 'i' )
        finalVocabCount = mergeVocabFiles()

        print("Vocab Count", finalVocabCount)
        # with open(sys.argv[3], 'w') as f:
        #     f.write(str(len(number_of_unique_unstemmed_words)) + '\n')
        #     f.write(str(finalVocabCount))

        currenttime = timeit.default_timer()
        print ("final", currenttime - start)