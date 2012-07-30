def check(spec_init,spec_final,filename,algorithm):
 """Loads a text file of limits for RFI bands and checks
 hit table, marking those hits where the frequency
 lies inside an RFI band. Spec_init is the first specid
 in the range to be checked, and spec_final is the 
 final specid in the range. Filename is the name of the file
 with the RFI band bounds, with one tab separated upper 
 and lower bound per line. algorithm denotes which rfi check
 is being performed, and it is an integer from 0 to 7,
 inclusive. """

 import numpy, MySQLFunction

 #Load file
 rfi = numpy.loadtxt(filename)

 #Determine value to add to rfi_check and rfi_found
 num = 2**algorithm 

 #Create list of intervals
 vals = list(numpy.arange(spec_init,spec_final,10000))
 vals.append(spec_final+1)

 #Loop through rfi bands and intervals, updating db
 for x in range(len(rfi)):
  bounds = list(rfi[x])
  print 'checking rfi band %s of %s' %(x+1,len(rfi))
  for y in range(len(vals)-1):
   print 'checking specid range %s to %s' %(vals[y],vals[y+1])
   
   #Create query
   query = 'select hitid from hit where specid>=%s and specid<%s and topocentric_freq>%s and topocentric_freq<%s;' %(vals[y],vals[y+1],bounds[0],bounds[1])

   #Get hitids where rfi_found
   data = MySQLFunction.mysqlcommand(query)
   data = [str(x[0]) for x in data]

   #Update rfi_found
   where_string = ', '.join([z for z in data])
   query = "UPDATE hit SET rfi_found = +%s WHERE hitid in (%s)" %(num,where_string)
   MySQLFunction.mysqlcommand(query)
   print 'rfi_found updated'
 
   #Update rfi_checked
   query = 'UPDATE hit SET rfi_checked = +%s WHERE specid>=%s and specid<%s;' %(num,vals[y],vals[y+1])
   MySQLFunction.mysqlcommand(query)
   print 'rfi_checked updated'

 return
