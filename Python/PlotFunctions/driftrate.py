def getspec(rawfile=''):
  """ Returns the first specid and time for a specified rawfile.
  Returns specid,obstime,and AGC_Time. """
  
  import MySQLFunction

  #Add quotes around string
  rawfile = "'%s'" %rawfile

  #Create command to send to mysql
  cmd = 'select specid,obstime,AGC_Time from config where rawfile=%s order by specid asc limit 1;' %(rawfile)

  #Execute command and return results
  data = MySQLFunction.mysqlcommand(cmd)
  specid = data[0][0]
  obstime = data[0][1]
  AGC_Time = data[0][2]

  return specid,obstime,AGC_Time

def calc(specid=[1,2]):
  """ Calculates the drift rate based on two consecutive spectra 
  in deg/sec. Input is a list of specids at which to calculate 
  drift rate and the output is a list of floats. """

  import numpy, math, MySQLFunction

  #Create command to send to mysql
  cmd = 'select ra,decl,specid from config where specid>=%i and specid<=%i and beamnum=3;' %(specid[0],specid[-1])

  #Execute command and return results
  data = MySQLFunction.mysqlcommand(cmd)
  data = data[::2]

  #Calculate difference in ra,dec
  length = len(data)-1
  delta_ra = [15*(data[x][0]-data[x+1][0]) for x in xrange(length)]
  delta_dec = [data[x][1]-data[x+1][1] for x in xrange(length)]
  specid = [data[x][2] for x in xrange(length)]

  #Account for absolute declination
  dec_rad = [math.radians(0.5*(data[x][1]+data[x+1][1])) for x in xrange(length)]
  delta_dec = [math.cos(dec_rad[x])*math.radians(delta_dec[x]) for x in xrange(length)]
  delta_dec = [math.degrees(delta_dec[x]) for x in xrange(length)]

  #Calculate difference vector quadratically
  vec = [math.sqrt((delta_ra[x])**2 + (delta_dec[x])**2) for x in xrange(length)]

  #Calculate drift rate
  diff = specid[1]-specid[0]
  time = .67108864*diff
  driftrate = [x/time for x in vec]

  return driftrate,specid

def plot(rawfile=''):
  """ Plots the drift rates for one polarization of beam 0
  over the course of an hour, beginning with the first spectrum
  in the specified rawfile. Output is a figure instance. 
  Also prints the average drift rate for the time interval. """
 
  import pylab, numpy, jd2gd

  #Create spectra array
  spec1,obstime,AGC_Time = getspec(rawfile=rawfile)
  spectra = list(numpy.linspace(spec1,spec1+5366,2))

  #Input array into calc function
  rates,spectra = calc(spectra)

  #Initialize figure
  fig=pylab.figure(figsize=(12,7))
  ax1 = fig.add_axes([0.1, 0.14, 0.85, 0.75])

  #Convert spectra to times
  minimum = min(spectra)
  spec = [x-minimum for x in spectra]
  time = [x*.671/60 for x in spec]

  #Plot data
  ax1.scatter(time,rates,marker='+',c='g')

  #Creat time string for title
  frac = float(AGC_Time)/86400000
  juldate = obstime + frac
  gdate = jd2gd.caldate(juldate)
  date = [str(gdate[0]),str(gdate[1]),str(gdate[2]),str(gdate[3]),str(gdate[4]),str(gdate[5])]
  dates = ['January','February','March','April','May','June','July',
  'August','September','October','November','December']

  if float(date[2])<10:
    date[2] = '0' + date[2]
  if float(date[3])<10:
    date[3] = '0' + date[3]
  if float(date[4])<10:
    date[4] = '0' + date[4]
  if float(date[5])<10:
    date[5] = '0' + date[5]

  date = date[0]+' '+dates[int(date[1])-1]+' '+date[2]+' '+date[3]+':'+date[4]+':'+date[5][:2]

  #Add Labels
  ax1.set_xlabel('Time (minutes)')
  ax1.set_ylabel('Drift Rate (deg/sec)')
  ax1.set_title('Drift Rates for %s' %date)

  #Set axis limits and grid
  ax1.grid(True)
  v=[0,60,0,max(rates)*1.02]
  ax1.axis(v)

  print numpy.median(rates)

  return fig
