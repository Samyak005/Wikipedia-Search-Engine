import timeit
import pickle
import sys
import string

vocabletter = string.digits +  '@' + '^' + string.ascii_lowercase

def pickleField(fileNo, field):
    fieldOffset = []
    with open(sys.argv[1] + '/offset_' + field + str(fileNo) + '.txt', 'r') as f:
        for line in f:
            fieldOffset.append(line)

    dbfile = open(sys.argv[1] + '/offset_' + field + str(fileNo) + '.pkl', 'wb')
    pickle.dump(fieldOffset, dbfile)                     
    dbfile.close()
    return 

def pickleVocabOffset(vocabl):
    fieldOffset = []
    with open(sys.argv[1] + '/vocaboffset' + vocabl + '.txt', 'r') as f:
        for line in f:
            fieldOffset.append(line)

    dbfile = open(sys.argv[1] + '/vocaboffset' + vocabl + '.pkl', 'wb')
    pickle.dump(fieldOffset, dbfile)                     
    dbfile.close()
    return 

def picklePageStatOffset(id):
    fieldOffset = []
    with open(sys.argv[1] + '/dataAll_PageStats' + '/pageStatsOffset' + id + '.txt', 'r') as f:
        for line in f:
            fieldOffset.append(line)

    dbfile = open(sys.argv[1] + '/dataAll_PageStats' + '/pageStatsOffset' + id +  '.pkl', 'wb')
    pickle.dump(fieldOffset, dbfile)                     
    dbfile.close()
    return 

if __name__ == '__main__':

    start = timeit.default_timer()   
    offset = []
    # with open(sys.argv[1] + '/titleOffset.txt', 'r') as f:
    #     for line in f:
    #         offset.append(line)

    # dbfile = open(sys.argv[1] + '/titleOffset.pkl', 'wb')
    # pickle.dump(offset, dbfile)                     
    # dbfile.close()
    # offset = []

    # with open(sys.argv[1] + '/offset.txt', 'r') as f:
    #     for line in f:
    #         offset.append(line)

    # dbfile = open(sys.argv[1] + '/offset.pkl', 'wb')
    # pickle.dump(offset, dbfile)                     
    # dbfile.close()
    # offset = []

    numBodyFiles, numTitleFiles, numInfoFiles, numRefFiles, numLinkFiles, numCategoryFiles = 351, 57 , 75, 27 , 44 , 8
    # numBodyFiles, numTitleFiles, numInfoFiles, numRefFiles, numLinkFiles, numCategoryFiles = 7, 1 , 2, 1 , 1 , 1

    # for i in range(numBodyFiles):
    #     pickleField(i, 'b')

    # for i in range(numTitleFiles):
    #     pickleField(i, 't')

    # for i in range(numInfoFiles):
    #     pickleField(i, 'i')

    # for i in range(numRefFiles):
    #     pickleField(i, 'r')

    # for i in range(numLinkFiles):
    #     pickleField(i, 'l')

    # for i in range(numCategoryFiles):
    #     pickleField(i, 'c')

    # for i in range(len(vocabletter)):
    #     pickleVocabOffset(vocabletter[i])

    pageStatLetter = [
"+w",
"+7",
"+cc",
"+h",
"+ll",
"+vv",
"+pp",
"+b",
"+qq",
"03",
"+aa",
"+0",
"02",
"+9",
"+i",
"+bb",
"+nn",
"+uu",
"+hh",
"0dd",
"+kk",
"+v",
"+y",
"0+",
"04",
"+jj",
"+2",
"+o",
"+xx",
"+e",
"+k",
"+a",
"05",
"+d",
"+mm",
"+8",
"+l",
"++",
"09",
"07",
"+n",
"+x",
"+r",
"+3",
"+_",
"+j",
"+q",
"+5",
"+z",
"08",
"+zz",
"+dd",
"+s",
"+oo",
"+ss",
"+f",
"0ff",
"+t",
"+4",
"0gg",
"+rr",
"+u",
"+p",
"+g",
"+ee",
"+tt",
"+c",
"+m",
"01",
"+ii",
"0ee",
"+6",
"00",
"0bb",
"+gg",
"+1",
"+ff",
"0g",
"+yy",
"06",
"0aa",
"+ww",
"0cc"
]
    for i in range(len(pageStatLetter)):
        picklePageStatOffset(pageStatLetter[i])

    end = timeit.default_timer()
    print('Time taken =', end-start)

    # dbfile = open('examplePickle', 'rb')
      
    # # source, destination
    # offset1= pickle.load(dbfile)                     
    # dbfile.close()
    # end = timeit.default_timer()
    # print('Time taken =', end-start)  

