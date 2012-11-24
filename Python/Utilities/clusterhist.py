def plot(length,eventpower,ones='True',bins=1000):
 
 """Plots a histogram of power vs. cluster length.
 An exponential fit is overlayed on the figure.

 Inputs:
 Length and eventpower arrays returned by the 
 cluster2D algorithm.

 Ones is either 'True' or 'False' depending on 
 whether you want just length-1 clusters or just
 clusters with length greater than 1.

 Bins is the number of bins to divide the spread
 of eventpowers into.

 Output is a figure instance. """

 import numpy, pylab, sys, math

 #Grab eventpowers corresponding to desired length
 if ones=='True':
  a=numpy.where(length==1)[0]
  epm=eventpower[a]
 elif ones=='False':
  a=numpy.where(length>1)[0]
  epm=eventpower[a]
 else: sys.exit('Incorrect string given to ones variable')

 #Perform histogramming
 y,x=numpy.histogram(epm,bins)
 
 #Find parameters for best fit exp line
 nonzero = numpy.where(y>max(y)/100)[0] #can't do log(0)
 counttemp=y[nonzero]
 bintemp=x[nonzero]
 counttemp = numpy.log(counttemp)
 coeffs = numpy.polyfit(bintemp,counttemp,1) #best fit polynomial
 A = math.exp(coeffs[1])
 B = abs(coeffs[0])
 exp = A*numpy.exp(-B*x[:-1])

 #Create plot
 fig=pylab.figure(figsize=(9,6))
 ax1 = fig.add_axes([0.1, 0.1, 0.8, 0.8])
 ax1.bar(x[:-1],y,align='center',width=(max(eventpower)-min(eventpower))/bins)
 ax1.plot(x[:-1],exp,'r--')
 if ones=='True':
  ax1.set_title('Length 1 Clusters: Histogram w/ Best Fit Exponential')
 elif ones=='False':
  ax1.set_title('Length>1 Clusters: Histogram w/ Best Fit Exponential')
 ax1.set_ylabel('Count')
 ax1.set_xlabel('Mean Cluster Power')
 
 return fig,counttemp,bintemp,nonzero
