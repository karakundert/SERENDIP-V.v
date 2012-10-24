def update(algorithm,spec1,spec2):
 """
 Checks database for consecutive occurrences
 of the same beam and flags them in rfi_found.

 Inputs: 
 algorithm: an integer between 0 and 7, inclusive
 spec1: the first spectrum to be checked
 spec2: the last spectrum to be checked
 """

 import MySQLFunction, numpy, sys

 #Compute RFI value
 num = 2**algorithm

 #Create query and grab beamnums
 cmd = 'select beamnum from config where specid>=%s and specid<=%s;'%(spec1,spec2)
 data = MySQLFunction.mysqlcommand(cmd)
 data = [y[0] for y in data]
 length = len(data)
 
 #Create list of values to loop through
 vals = list(numpy.arange(1,length,10000))
 vals.append(length+1)
 
 #Loop through data, checking and updating 
 for x in range(len(vals)-1):
  #Create shorter list of data to work with
  tempdata = data[vals[x]-1:vals[x+1]-1]
  
  #Grab indices where next two beamnums are equivalent
  indices = [a for a in range(len(tempdata)-2) if (tempdata[a+2]==tempdata[a] and tempdata[a+1]==tempdata[a])]
  
  #Manually flag two spectra after final flagged spectrum
  if len(indices)>0:
   final = max(indices)
   indices.append(final+1)
   indices.append(final+2)
  
  #Compute offset for this particular interval
  indices = [b+(vals[x]-1)+spec1 for b in indices]

  #Create where string
  where_string = ', '.join([str(c) for c in indices])
  
  #Create queries and update db
  if len(indices)>0:
   query1= 'update hit set rfi_found=rfi_found+%s where specid in (%s);'%(num,where_string)
   MySQLFunction.mysqlcommand(query1)
  query2= 'update hit set rfi_checked=rfi_checked+%s where specid>=%s and specid<%s;'%(num,vals[x]+spec1-1,vals[x+1]+spec1-1)
  MySQLFunction.mysqlcommand(query2)
  print 'done with interval %s to %s'%(vals[x]+spec1-1,vals[x+1]+spec1-2)
  
 return
