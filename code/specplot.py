import numpy
import matplotlib.pyplot as plt
import csv as CSV
import sys as sys


#if len(sys.argv) != 3:
#    print 'usage: python specplots.py <inputfilename> <outputfilename>'
#    exit()

#inputfilename = sys.argv[1]
#outputfilename = sys.argv[2]

for inputfilename in sys.argv[1:]:
    with open(inputfilename) as file:
        filesreader = CSV.DictReader(file, skipinitialspace=True)
        x = []
        y = []
        for each in filesreader:
            x.append(int(each['coarsebin']))
            y.append(float(each['power']))
            
        X = numpy.array(x)
        Y = numpy.array(y)
        plt.semilogy(X, Y)

plt.xlabel('coarse bin')
plt.ylabel('power')
plt.show() 

