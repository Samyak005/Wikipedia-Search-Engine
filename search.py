# search5 - removed document leangth normalisation done in search4 - only 10 results shown
#  
# Index is stored in multiple files to reduce file size and for faster access
# When a query is received, Search.py first has to identify the index files which must be retrieved
#  
# Field wise file numbers are stored in the "Vocabulary" file which is sorted by the "word" 
# Query words are stemmed and then searched in the "Vocabulary" file. 
# Binary search is performed using an Offset file. 
# First of all, "Offset" file is loaded which enables random access through Vocabulary file.
# 
# Once file numbers for each of the fields in which the word is present are known,
# list of documents is retrieved from the index file (specific to each field)
# Index file also returns the frequency of the word present in the document

# In phase 1, only the list of documents by the field were presented as results.
# In phase 2, the documents are ranked basis fieldwise weights and frequenct of word occurrence in the fields
# Final results are sorted by the cumulative score and 
# the Title of these documents are retrieved and presented as results in order of declining score.

# Random access through offset files is using for loading the index files and 
# also the Title file for final presentation of results
# 
# Performance optimizations -
# 1. Offset files are stored as pickle files for faster load time, large part of search query time
# corresponds to file load time, however, once a search server is set up, 2 of the offset files can be pre-loaded
# in the memory and time can be saved for query execution
# 2. Binary search through the use of offset files - This helps in faster search through Vocabulary, index files
# and Title files
# 3. Sorting of final results through Heapq substantially reduced time to retrieve top N results
# 4. Index stores the corpus frequency of each word that enables computing weights for each word
# 5.

# unique words in r 1313077
# unique words in t 2830134
# unique words in l 2171766
# unique words in b 17540808
# unique words in c 379529
# unique words in i 3721155
# Unique Vocab Count in corpus 18938858


from collections import defaultdict
from createPreindex import Page
import sys
import re
import timeit
import pickle
import math
import heapq

start = 0
end = 0
numPages = 21384756
numResults = 10
numPreResults = 10
offset = []

FIELDS = {  'b' : 0,
            't': 1 ,
            'c': 2,
            'i': 3,
            'r': 4, 
            'l': 5 }

FIELD_NAMES = {  'b' : "body",
            't': "title" ,
            'c': "categories",
            'i': "infobox",
            'r': "references", 
            'l': "links" }

FACTOR = {'b' : 0.2, 't': 0.4, 'c':0.1, 'i':0.2, 'r':0.05, 'l':0.05}
avgLength = [203.46, 3.29, 6.36, 23.37, 3.05, 4.73]

def return5charstring(term1):
    if len(term1) == 5:
        return term1
    elif len(term1) == 4:
        return '+'+term1
    elif len(term1) == 3:
        return '++'+term1
    elif len(term1) == 2:
        return '+++'+term1
    elif len(term1) == 1:
        return '++++'+term1

def findFileNo(low, high, offset, term, f, typ):
    # print("in find file no", low, high)
    while low < high:
        mid = int((low + high) / 2)
        f.seek(int(offset[mid]))
        termPtr = f.readline().strip().split()

        midstring = termPtr[0]

        if typ == '64bit':
            midstring = return5charstring(midstring)

            # print(mid, termPtr)
            # print(low, high, mid, int(offset[mid]), termPtr[0], midstring, term)

        if typ == 'int':
            if int(term) == int(termPtr[0]):
                return termPtr[1:], mid
            elif int(term) > int(termPtr[0]):
                low = mid + 1
            else:
                high = mid
        else:
            if term == midstring:
                # print(midstring, mid)
                return termPtr[1:], mid
            elif term > midstring:
                low = mid + 1
            else:
                high = mid
    return [], -1

def findPages(fileNo, field, word, fieldFile):
    fieldOffset = []
    # with open(sys.argv[1] + '/offset_' + field + fileNo + '.txt') as f:
    #     for line in f:
    #         fieldOffset.append(line)

    dbfile = open(sys.argv[1] + '/offset_' + field + fileNo + '.pkl', 'rb')
    fieldOffset= pickle.load(dbfile)                     
    dbfile.close()

    pageList, _ = findFileNo(0, len(fieldOffset), fieldOffset, word, fieldFile, 'str')
    fieldOffset = []
    # print("pageList", pageList)
    return pageList

def rank(pageList, docFreq, numPages, qtype):

    docs = defaultdict(float)
    termFreqinDoc = defaultdict(list)
    # print(pageList,docFreq, numPages, qtype)

    queryIdf = defaultdict(list)
    idf = []
    for key in docFreq:
        for field in range(len(docFreq[key]))[1:]:
            # docFreq[key][field] = round(math.log(float(numPages) / float(docFreq[key][field])),2)
            if docFreq[key][field] != '$':
                docFreq[key][field] = math.log((float(numPages) - float(docFreq[key][field]) + 0.5) / ( float(docFreq[key][field]) + 0.5))
            else:
                docFreq[key][field] = 0
        # print("weight for", key,"= ",  docFreq[key])

    for word in pageList:
        fieldWisePostingList = pageList[word]
        for field in fieldWisePostingList:
            if len(field) > 0:
                # field = field
                postingList = fieldWisePostingList[field]
                factor = FACTOR[field]
                # print(word, field, len(postingList)/2)
                for i in range(0, len(postingList), 2):
                    # docs[postingList[i]] += round(float( factor * (1+math.log(1+float(postingList[i+1]))) * docFreq[word][FIELDS[field]+1]), 2)
                    docs[postingList[i]] += round(float( factor * (float(postingList[i+1])/ (1+float(postingList[i+1]))) * docFreq[word][FIELDS[field]+1]), 2)
                    # print(postingList[i], postingList[i+1], field, docs[postingList[i]])

    return docs

def fieldQuery(words, fields):
    pageList = defaultdict(dict)
    pageFreq = defaultdict(list)
    for i in range(len(words)):
        word = words[i]
        field = fields[i]
        if word == '':
            continue
        else:
            offset = []
            currentCharOfVocab = word[0]
            dbfile= open(sys.argv[1] + '/vocaboffset'+ currentCharOfVocab +'.pkl', 'rb')
            offset = pickle.load(dbfile)
            dbfile.close()
            vocab_file = open(sys.argv[1] + '/mergedvocab'+ currentCharOfVocab + '.txt', 'r')

            # print()
            pages, _ = findFileNo(0, len(offset), offset, word, vocab_file, 'str')

            # print(word,'pages', field, pages)
            if len(pages) > 0:
                pageFreq[word] = pages[0:7]
                fileNoList = pages[7], pages[8], pages[9], pages[10], pages[11], pages[12]
                fileNo = fileNoList[FIELDS[field]]
                # print(word, fileNoList, fileNo)
                if fileNo != '$':
                    filename = sys.argv[1] + '/' + field + str(fileNo) + '.txt'
                    fieldFile = open(filename, 'r')
                    returnedList = findPages(fileNo, field, word, fieldFile)
                    pageList[word][field] = returnedList
                else:
                    print(word, "not present in ", field)
    return pageList, pageFreq

def normalQuery(words):
    pageList = defaultdict(dict)
    pageFreq = defaultdict(list)
    fields = ['t', 'b', 'i', 'c', 'r', 'l']
    for word in words:
        if word == '':
            continue
        else:
            offset = []
            currentCharOfVocab = word[0]
            dbfile= open(sys.argv[1] + '/vocaboffset'+ currentCharOfVocab +'.pkl', 'rb')
            offset = pickle.load(dbfile)
            dbfile.close()
            vocab_file = open(sys.argv[1] + '/mergedvocab'+ currentCharOfVocab + '.txt', 'r')

            pages, _ = findFileNo(0, len(offset), offset, word, vocab_file, 'str')
            if len(pages) > 0:
                pageFreq[word] = pages[0:7]
                fileNoList = pages[7], pages[8], pages[9], pages[10], pages[11], pages[12]

                for field in fields:
                    #print(word, field)
                    fileNo = fileNoList[FIELDS[field]]
                    if fileNo != '$':
                        filename = sys.argv[1] + '/' + field + str(fileNo) + '.txt'
                        fieldFile = open(filename, 'r')
                        returnedList = findPages(fileNo, field, word, fieldFile)
                        pageList[word][field] = returnedList
                    else:
                        print(word, "not present in ", field)
                    # print(word, field,'pages', pageList[word][field])
    return pageList, pageFreq

def outputRankedPages(results):
    count = 0

    # currenttime = timeit.default_timer()
    # print('Time taken =', currenttime-start)

    # get top 200 keys by value from results, heapq gives better performance than sorted and collections.counter
    sorted_results = heapq.nlargest(numPreResults, results.items(), key=lambda x: x[1])
    # sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)[:numResults]
    # sorted_results = dict(collections.Counter(results).most_common()[:10])

    # currenttime2 = timeit.default_timer()
    # print('Sorting time of final results=', currenttime2-currenttime)

    outfile =  open('queries_op.txt', 'a')

    if len(results)>0:
        for i in range(len(sorted_results)):
            key = sorted_results[i][0]

            key = return5charstring(key)
            ID1 = key[0:2]
            ID2 = ID1.lower()
            if (ID1 != ID2):
                ID2 = ID2 + ID2[1:2]      
            # print(key, ID2)
            titlecount = 0
            titleOffset = []
            dbfile = open(sys.argv[1] + '/dataAll_PageStats' + '/pageStatsOffset'+ ID2+ '.pkl', 'rb')
            titleOffset = pickle.load(dbfile) 
            dbfile.close()
            titlecount = len(titleOffset)

            title_file = open(sys.argv[1] + '/dataAll_PageStats' + '/pageStats'+ ID2+ '.txt', 'r')

            count += 1
            # lookup for key in title
            title, _ = findFileNo(0, titlecount, titleOffset, key, title_file,'64bit')

            outfile.write(key +"  " + ' '.join(title[6:]) + "  "+str(round(sorted_results[i][1],2)) + '\n')
        end = timeit.default_timer()
        outfile.write('Time taken =' + str(end-start) + "\n \n")
                    
    else:
        outfile.write("Search query does not match any of the pages, No results found")
    outfile.close()
    return

if __name__ == '__main__':

    d = Page()
    # query = ' '.join(sys.argv[2:])
    queryfile = sys.argv[2]
    # query = "t:World Cup i:2018 c:Football"
    with open(sys.argv[2], 'r') as dbfile:
        for line in dbfile:
            query = line.lower()
            # print(query)
            start = timeit.default_timer()   

            if re.match(r'[t|b|i|c|r|l]:', query):
                words = re.findall(r'[t|b|c|i|l|r]:([^:]*)(?!\S)', query)
                tempFields = re.findall(r'([t|b|c|i|l|r]):', query)
                tokens = []
                fields = []
                # print(words)
                for i in range(len(words)):
                    for word in words[i].split():
                        fields.append(tempFields[i])
                        tokens.append(word)
                # print(fields)
                stemmed_tokens = d.stem(tokens)
                # print(stemmed_tokens)
                pageList, pageFreq = fieldQuery(stemmed_tokens, fields)

                # currenttime = timeit.default_timer()
                # print('Time taken after retrieving all pages with words =', currenttime-start)
                offset = []  
                results = rank(pageList, pageFreq, numPages, 'f')
                pageList = []
                pageFreq = []        
    
                outputRankedPages(results)
            else:
                tokens = []
                for word in query.split():
                    tokens.append(word)
                stemmed_tokens = d.stem(tokens)

                pageList, pageFreq  = normalQuery(stemmed_tokens)

                # currenttime = timeit.default_timer()
                # print('Time taken after retrieving all pages with words =', currenttime-start)
                offset = []

                results = rank(pageList, pageFreq, numPages, 'n') 
                pageList = []
                pageFreq = []
 
                outputRankedPages(results)