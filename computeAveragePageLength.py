import sys
import timeit

start = timeit.default_timer()

if __name__ == '__main__':

    FIELDS = ['b','t','c','i','r','l']
    bodyLength, titleLength, categoryLength, infoLength, refLength, linkslength = 0, 0,0 ,0,0,0
    bodyavg, titleavg, categoryavg, infoavg, refavg, linksavg = 0,0,0,0,0,0
    data = []
    dataOffset = []
    NUMPAGES = 262144 #64*64*64
    pageCount = 0
    fileCount = 0
    prevTitleOffset = 0
    numPages = 21384756
    pageStatsfilename = sys.argv[1]

    with open(pageStatsfilename, 'r') as fp:
        for line in fp:
            lt = line.split()
            bodyLength += int(lt[1])
            titleLength += int(lt[2])
            categoryLength += int(lt[3])
            infoLength += int(lt[4])
            refLength += int(lt[5])
            linkslength += int(lt[6])
            pageCount += 1
    fp.close()

    bodyavg, titleavg, categoryavg, infoavg, refavg, linksavg = bodyLength/numPages, titleLength/numPages, categoryLength/numPages, infoLength/numPages, refLength/numPages, linkslength/numPages
    print(bodyavg, titleavg, categoryavg, infoavg, refavg, linksavg )