def check(spec_init,spec_final,filename,algorithm):
 """Loads a text file of meanpower limits and checks hit 
 table, marking those hits where the frequency
 lies below the limit. Spec_init is the first specid
 in the range to be checked, and spec_final is the 
 final specid in the range. Filename is the name of the file
 with the meanpower limits, with one tab beamnum and 
 limit per line. algorithm denotes which check
 is being performed, and it is an integer from 0 to 7,
 inclusive. """

 import numpy, MySQLFunction

 #Load file
 limits = numpy.loadtxt(filename)

 #Determine value to add to rfi_check and rfi_found
 num = 2**algorithm 

 #Create list of intervals
 vals = list(numpy.arange(spec_init,spec_final,10000))
 vals.append(spec_final+1)

 #Loop through beams and intervals, updating db
 for x in range(14):
  beamnum = int(list(limits[x])[0])
  limit = int(list(limits[x])[1])
  print 'checking beamnum %s of %s' %(x+1,14)
  for y in range(len(vals)-1):
   print 'checking specid range %s to %s' %(vals[y],vals[y+1]-1)
   
   #Get list of specids
   cmd = 'select specid from config where specid>=%s and specid<%s and beamnum=%s;' %(vals[y],vals[y+1],beamnum)
   specs = MySQLFunction.mysqlcommand(cmd)
   specs = [str(x[0]) for x in specs]
   where = ', '.join([z for z in specs])

   #Create query
   query = 'select hitid from hit where specid in (%s) and meanpower<%s;' %(where,limit)

   #Get hitids where rfi_found
   data = MySQLFunction.mysqlcommand(query)
   data = [str(x[0]) for x in data]

   #Update rfi_found
   if len(data)>0:
    where_string = ', '.join([z for z in data])
    query = "UPDATE hit SET rfi_found = +%s WHERE hitid in (%s)" %(num,where_string)
    MySQLFunction.mysqlcommand(query)
    print 'rfi_found updated'
 
   #Update rfi_checked
   query = 'UPDATE hit SET rfi_checked = +%s WHERE specid>=%s and specid<%s;' %(num,vals[y],vals[y+1])
   MySQLFunction.mysqlcommand(query)
   print 'rfi_checked updated'

 return
