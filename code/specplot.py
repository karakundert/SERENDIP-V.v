# this is the python file used to plot the data saved in a spectraldata
# file. currently, it plots the sum of coarse power as a line vs. LSR
# velocity. should be modified to plot hits as well, so we can check that
# they line up with the frequencies they should.
#
# the file used to check is called spectraldatabirdie. I believe the 
# injected tone is at 1419.0. we've already verified that the coarse 
# spectra are in the right bins, we just need to check that the hits are
# as well.
#
# to run: python specplot.py <datafilename>
#
# good luck!


from __future__ import division
import numpy
import matplotlib.pyplot as plt
import csv as CSV
import sys as sys

for inputfilename in sys.argv[1:]:
    with open(inputfilename) as file:
        filesreader = CSV.DictReader(file, skipinitialspace=True)
        theSum = numpy.zeros(4096, dtype=float)
        for each in filesreader:
            #x.append(float(each['coarsebin']))
            #y.append(float(each['coarsepower']))
            #z.append(float(each['hitpower']))

            if each['coarsebin']=='coarse bin':
                continue
            x = int(each['coarsebin'])
            y = float(each['coarsepower'])
            theSum[x] += y; 
        
        X = numpy.zeros(4096)
        freq = numpy.array(x)
        count = 0;
        while (count < 4096):
            #X[count] = 1525 - 200*count/4096
            #nu = (1525 - 200*count/4096) -(1420.41 -
            #        (21106.1*1420.41/(3*(10**8))))
            #X[count] = -(nu/1420.41)*(3*(10**8))/1000
            X[count] = (1570 - 200*count/4096)
            count += 1

        print X
        #Z = numpy.array(z)

        #plt.semilogy(X[1400:1450], theSum[1400:1450])
        plt.plot(X, theSum)
        #plt.scatter(X, Z)

plt.xlabel('LSR velocity')
plt.ylabel('power')
plt.show()

