import sys, numpy, MySQLFunction, math

def main(start,end):
  """An algorithm to interpolate and update
  obstime values in the database. Interval is 
  looped over in increments of 500000 spectra.

  Inputs:
  start - first specid in range to update
  end - last specid in range to update 
  """

  #Determine limits for each loop
  limits=numpy.arange(start,end,500000)
  limits=numpy.append(limits,end)

  #Perform loop
  for x in range(len(limits)-1):

   #Grab data in current range
   data = grabdata(limits[x],limits[x+1])
  
   #Interpolate and update data in current range
   interpolate(data)

   #Display progress
   print 'completed interval %s of %s' %(x+1,len(limits)-1) 
  
  return

if __name__=="__main__":
  main()

def grabdata(start,end):
 """ Grabs mjd value, specid, AGC_SysTime and AGC_Time from
 config table in given range. Output is the correct format
 for the interpolate function.

 Inputs:
 start - first specid in range to update
 end - last specid in range to update 

 Output:
 data - array of obstime,specid,AGC_Systime,and AGC_Time, in tuples
 """
 
 #Grab values from database
 cmd = 'select obstime,specid,AGC_SysTime,AGC_Time from config where specid>=%s and specid<=%s;' %(start,end)
 data = numpy.array(MySQLFunction.mysqlcommand(cmd))

 return data

def interpolate(data):
 """Does the interpolation and loads the data into the database. 
 Input: data - the output from the grabdata function """

 #Convert data to four arrays
 obstime,specid,systime,time=numpy.transpose(data)
 
 #Calculate difference in systime
 diff = systime[1:]-systime[:-1]

 #Find discontinuities in observing
 disc = numpy.where(diff>=2)[0]
 disc=disc+1
 disc=numpy.insert(disc,0,0)
 disc=numpy.append(disc,len(systime))
 
 #Initialize obstime array
 obstime_new = []

 #For each continuous interval
 for x in range(len(disc)-1): 
  
  lowlim=disc[x] #Index limits
  highlim=disc[x+1]
  
  #Range of values to loop over
  arange = list(numpy.arange(lowlim,highlim-3,1))

  #Find patterns within the limits
  index=[]
  finaltime = time[highlim-1]

  for x in arange:
   #If the next three values increase by 1
   if (diff[x]==1 and diff[x+1]==1 and diff[x+2]==1 and time[x+3]!=finaltime):
     
     #Grab index of element where pattern occurs
     index.append(x+3)

  #Append boundary limits
  index.insert(0,lowlim)
  index.append(highlim)

  #Initialize obstemp array of obstime limits
  obstemp = list(numpy.empty(len(index)))
   
  #Convert indices to appropriate obstimes
  if time[lowlim]<72000000: #Lower bound
   obstemp[0] = obstime[lowlim] + ((time[lowlim] + 14400000.)/86400000.)
  else: obstemp[0] = (obstime[lowlim]-1) + ((time[lowlim] + 14400000.)/86400000.)
   
  if time[highlim-1]<72000000:#Upper bound
   obstemp[-1] = obstime[highlim-1] + ((time[highlim-1] + 14400000.)/86400000.)
  else: obstemp[-1] = (obstime[highlim-1]-1) + ((time[highlim-1] + 14400000.)/86400000.)
  
  vals = list(numpy.arange(1,len(index)-1,1))
  for x in vals: #Everything else
   
   if time[index[x]]<72000000:
     obstemp[x]=(obstime[index[x]]+((time[index[x]]+6.63296+14400000.)/86400000.))
   else: obstemp[x]=((obstime[index[x]]-1)+((time[index[x]]+6.63296+14400000.)/86400000.))    

  #Linear spacing between consecutive patterns/boundaries
  for x in xrange(len(obstemp)-1):
   #Generate linear spacing
   lin = list(numpy.linspace(obstemp[x],obstemp[x+1],(index[x+1]-index[x])+1)[:-1])
   #Append obstime_new
   for y in lin:
    obstime_new.append(y)

 #Create tuples of specid and obstime to be returned   
 output = [[str(specid[x]),repr(obstime_new[x])] for x in xrange(len(data))]

 #Create mysql query
 conditions_string = '\n'.join(["WHEN %s THEN %5.14s" %(x,y) for x,y in output])
 where_string = ', '.join([z[0] for z in output])
 query = "UPDATE config \nSET obstime = CASE specid \n%s \nEND \nWHERE specid in (%s)" %(conditions_string,where_string)
  
 #Send query to database
 MySQLFunction.mysqlcommand(query)

 return
