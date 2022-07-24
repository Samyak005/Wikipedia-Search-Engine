# Indexer4 - removed reduntant code for performance optimisation
import sys
from collections import defaultdict
import os
import timeit
import string

start = timeit.default_timer()

#64 base mapping of integers - encode and decode requires following strings
ALPHABET ='+' + string.digits+  string.ascii_uppercase + '_' + string.ascii_lowercase
ALPHABET_REVERSE = dict((c, i) for (i, c) in enumerate(ALPHABET))
BASE = len(ALPHABET)

# Encodes a positive integer to base 64 coding
def num_encode(n):
    s = []
    while True:
        n, r = divmod(n, BASE)
        s.append(ALPHABET[r])
        if n == 0: break
    return ''.join(reversed(s))

# Decodes a base 64 coding to a positive integer
def num_decode(s):
    n = 0
    for c in s:
        n = n * BASE + ALPHABET_REVERSE[c]
    return n

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

class splitPageStats():

    if __name__ == '__main__':
        data = []
        dataOffset = []
        NUMPAGES = 262144
        pageCount = 0
        fileCount = 0
        prevTitleOffset = 0

        pageStatsfilename = sys.argv[1]
        with open(pageStatsfilename, 'r') as fp:
            for line in fp:
                
                if pageCount!= 0 and pageCount%NUMPAGES == 0:   
                    # change filename
                    ID = num_encode(pageCount-1)
                    ID1 = return5charstring(ID)[0:2]
                    ID2 = ID1.lower()
                    if (ID1 != ID2):
                        ID2 = ID2 + ID2[1:2]      
                    fileindicator = ID2
                    print(pageCount, fileindicator)       

                    filename = sys.argv[2] + '/pageStats'+fileindicator+'.txt'
                    with open(filename, 'w') as f:
                        f.write(''.join(data))
                    f.close()
                    filename = sys.argv[2] + '/pageStatsOffset'+fileindicator+'.txt'
                    with open(filename, 'w') as f:
                        f.write('\n'.join(dataOffset))
                        f.write('\n')
                    f.close()

                    #reset counter, free up memory
                    prevTitleOffset = 0
                    data = []
                    dataOffset = []
                    fileCount +=1

                data.append(line)
                dataOffset.append(str(prevTitleOffset))
                prevTitleOffset += len(line)

                pageCount += 1
        fp.close()
    
        # change filename
        ID = num_encode(pageCount-1)
        ID1 = return5charstring(ID)[0:2]
        ID2 = ID1.lower()
        if (ID1 != ID2):
            ID2 = ID2 + ID2[1:2]     
        fileindicator = ID2
        print(pageCount, fileindicator)       

        filename = sys.argv[2] + '/pageStats'+fileindicator+'.txt'
        with open(filename, 'w') as f:
            f.write(''.join(data))
        f.close()
        filename = sys.argv[2] + '/pageStatsOffset'+fileindicator+'.txt'
        with open(filename, 'w') as f:
            f.write('\n'.join(dataOffset))
            f.write('\n')
        f.close()

        #reset counter, free up memory
        prevTitleOffset = 0
        data = []
        dataOffset = []
        fileCount += 1

        currenttime = timeit.default_timer()
        print ("pagecount", pageCount, "number of files", fileCount, "before merge", currenttime - start)
