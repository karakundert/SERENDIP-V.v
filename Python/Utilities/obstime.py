def reset():
 """ Determines mjd integer value for each spectrum based on AGC_SysTime.
 Returns list of tuples, each with specid and mjd integer."""

 import MySQLFunction, gd2jd, time
 
 #Grab SysTimes
 data = MySQLFunction.mysqlcommand('select AGC_SysTime,specid from config;')
 
 #Create lists
 datarray = [x[0] for x in data]
 specid = [x[1] for x in data]
 
 #Create tuples of year, month, day in Gregorian format
 tuples = [(time.gmtime(x)[0],time.gmtime(x)[1],time.gmtime(x)[2]) for x in datarray]

 #Convert to mjd integer values
 mjd = [(str(specid[x]),int(gd2jd.julian_date(tuples[x][0],tuples[x][1],tuples[x][2],0,0,0))) for x in xrange(len(tuples))]

 return mjd

def interpolate(mjd,data):
 """Does the interpolation and loads the data into the database. Inputs are
 mjd, the output from reset(), and data, which is a list of tuples of
 AGC_SysTime and AGC_Time for each spectrum in the database."""

 import numpy, math, MySQLFunction

 #Remove data from tuples
 length = len(data)
 systime = [data[x][0] for x in xrange(length)]
 time = [data[x][1] for x in xrange(length)]
 obstime = [x[1] for x in mjd]
 specid = [x[0] for x in mjd]
 
 #Calculate difference
 diff = [int(systime[x+1]-systime[x]) for x in xrange(length-1)]

 #Find discontinuities in observing
 disc = []
 for x in range(length-1):
  if diff[x]>=2:
   disc.append(x+1) 

 disc.insert(0,0)
 disc.append(length)
 
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
 output = [[str(specid[x]),repr(obstime_new[x])] for x in xrange(length)]

 #Loop through output in increments of 50000

 lim = list(numpy.arange(0,len(output),50000))
 lim.append(len(output)+1)

 for x in range(len(lim)-1):
  print '%s of %s' %(x,len(lim)-1)
  output_temp = output[lim[x]:lim[x+1]]
 
  #Create mysql query
  conditions_string = '\n'.join(["WHEN %s THEN %5.14s" %(x,y) for x,y in output_temp])
  where_string = ', '.join([z[0] for z in output_temp])
  query = "UPDATE config \nSET obstime = CASE specid \n%s \nEND \nWHERE specid in (%s)" %(conditions_string,where_string)
  
  #Send query to database
  MySQLFunction.mysqlcommand(query)

 return
