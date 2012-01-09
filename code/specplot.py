import numpy
import matplotlib.pyplot as plt
import csv as CSV
import sys as sys


if len(sys.argv) != 3:
    print 'usage: python specplots.py <inputfilename> <outputfilename>'
    exit()

inputfilename = sys.argv[1]
outputfilename = sys.argv[2]
x = []
y = []

file = open(inputfilename)
filesreader = CSV.DictReader(file)
for each in filesreader:
    print each
file.close()


