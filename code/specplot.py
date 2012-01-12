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
        z = []
        for each in filesreader:
            x.append(int(each['coarsebin']))
            y.append(float(each['coarsepower']))
            z.append(float(each['hitpower']))

        print x
            
        X = numpy.array(x)
        Y = numpy.array(y)
        Z = numpy.array(z)
        plt.semilogy(X, Y)
        plt.scatter(X, Z)

plt.xlabel('coarse bin')
plt.ylabel('power')
plt.show() 

