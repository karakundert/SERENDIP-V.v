def extract(rawfile='',spec=[]):
 """Returns a list of tuples of start/stop 
 specids for continuous observing intervals where 
 drift rate is zero.

 Input is EITHER the rawfile in which the intervals
 are to be computed, or a list of the FIRST and LAST 
 spectra between which all intervals are computed. 
 Use one or the other but not both."""

 import MySQLFunction, numpy, sys

 #Create query depending on input type
 if rawfile!='' and spec==[]:
  cmd = 'select straight_join distinct c.specid from config c,hit h where h.reserved=0 and c.rawfile="%s" and c.specid=h.specid;' %rawfile
 elif spec!=[] and rawfile=='' and len(spec)==2:
  cmd = 'select straight_join distinct specid from hit  where reserved=0 and specid>=%s and specid<=%s;' %(spec[0],spec[1])
 elif len(spec)!=2:
  sys.exit('Spec is a list of TWO specids only')
 elif spec!=[] and rawfile!='':
  sys.exit('Please only use ONE input type')

 #Send query to db, fetch results
 data = MySQLFunction.mysqlcommand(cmd)
 data = [int(x[0]) for x in data]

 #Compute differences between each spectra in results
 diff = [data[x+1]-data[x] for x in range(len(data)-1)]

 #Determine indices where diff>10
 indices=[x for x in range(len(diff)) if diff[x]>20]

 #Create tuples of start/stop specids for pointings
 tuples = [(data[indices[x]+1],data[indices[x+1]]) for x in range(len(indices)-1) if (data[indices[x+1]]-data[indices[x]+1])>25]

 return tuples
