def check(spec1,spec2,width,length):
 """Checks a range of specids for frequency
 clustering. 

 spec1 and spec2 are the first and last
 spectra to be checked for clustering. 
 
 width is the frequency interval width in
 which to look for clusters.
 
 length is the number of consecutive spectra
 that consistitutes a cluster.

 All spectra must share a common center 
 frequency. 

 Output is a list of frequency bands in 
 which clustering was observed."""

 import MySQLFunction, numpy, sys

 #Obtain frequency information for loops
 cmd = 'select distinct IF1_rfFreq from config where specid>=%s and specid<=%s;'%(spec1,spec2)
 centerfreq = MySQLFunction.mysqlcommand(cmd)
 centerfreq = [freq[0] for freq in centerfreq]
 
 #Only one center frequency?
 if len(centerfreq)>1:
  sys.exit('More than one center frequency in this range')
 else:
  center = centerfreq[0]

 #Create frequency band ranges
 uppbound = center + 100000000
 lowbound = center - 100000000
 freqs = numpy.arange(lowbound,uppbound+1,width)
 
 #Loop through freq bands
 results = []
 for x in range(len(freqs)-1):
  #Get spectra where a hit is found in the specified freq range
  cmd = 'select distinct specid from hit where specid>=%s and specid<=%s and topocentric_freq>%s and topocentric_freq<%s and rfi_found=0 and reserved=0;'%(spec1,spec2,freqs[x],freqs[x+1])
  spectra = MySQLFunction.mysqlcommand(cmd)
  spectra = [b[0] for b in spectra]

  #Does a cluster occur?
  if len(spectra)>(width-1):
   for y in range(len(spectra)-(width-1)):
 
    #Create list of differences
    diff = [spectra[z+1]-spectra[z] for z in numpy.arange(y,y+width,1)] 
    for val in diff:
     if val!=1:
      diff[val]=0
    #All consecutive?
    if all(diff):
     results.append(freqs[x]+(width/2))
     break
  print x
  
 return results
