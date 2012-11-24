def plot(eventpower):
 import numpy,pylab,math

 histbins = list(numpy.linspace(min(eventpower),max(eventpower),500))
 
 count,bins=numpy.histogram(eventpower,histbins)

 countlog = [math.log(x) for x in count if x>0]
 countlog=countlog[0:10]
 binslog = [bins[x] for x in range(len(count)) if count[x]>0]
 binslog = binslog[0:10]
 coeffs = numpy.polyfit(binslog,countlog,1)

 pylab.bar(bins[:-1],count,width=(max(eventpower)-min(eventpower))/500)

 vals=list(numpy.linspace(0,max(eventpower),500))

 A = math.exp(coeffs[1])
 B = coeffs[0]
 exp = [A*math.exp(B*x) for x in vals]

 pylab.plot(vals,exp,'g-')

 pylab.show()

 return count,bins,A,B,coeffs,binslog,countlog
