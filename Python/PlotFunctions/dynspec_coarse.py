import sys

def main(where='',freqtype='binnum',vlim=(-1,-1), tslim=(-1,-1),saveplot=''):
  """Produces the three panel
  dynamic spectrum plot. The main panel
  is a pcolormesh figure of data with
  the mesh defined by xarr and yarr.
  The bottom panel shows a time series of
  the 2D data, and the right panel shows
  the average bandpass

  freqtype is the frequency type for the pcolormesh, either 
  'binnum' or 'topo'.

  where is a string to include additional information to 
  narrow the results. typically it will be used to specify a 
  range of specids. each column name MUST be prefixed with 
  the first letter of the table name and a period, like 
  c.obstime. don't forget to include 's.specid=c.specid if 
  referencing config and spec. do not include the word 'where' 
  at the beginning or the semicolon at the end. all other common 
  mysql syntax rules apply. Ex: 's.specid>1 and s.specid<=20 and 
  c.beamnum!=8 and c.specid=s.specid'. don't include hit table.

  vlim and tslim are plot limits for pcolormesh and time series.

  saveplot allows the user to have the figure saved by 
  inputting the file name. if left empty, no file will be saved

  returns a figure instance. """

  #Get data
  xarr,yarr,data = fetchdata(where,freqtype)
  
  #Plot data
  fig = makeplot(xarr,yarr,data,where,vlim,tslim,saveplot=saveplot)
  
  return fig

if __name__=="__main__":
  main()

def fetchdata(where='',freqtype='binnum'):
  """Fetches data to produce the three panel dynamic spectrum 
  plot.

  where is a string to include additional information to 
  narrow the results. typically it will be used to specify a 
  range of specids. each column name MUST be prefixed with 
  the first letter of the table name and a period, like 
  c.obstime. don't forget to include 's.specid=c.specid if 
  referencing config and spec. do not include the word 'where' 
  at the beginning or the semicolon at the end. all other common 
  mysql syntax rules apply. Ex: 's.specid>1 and s.specid<=20 and 
  c.beamnum!=8 and c.specid=s.specid'. don't include hit table.

  freqtype is the frequency type for the pcolormesh, either 
  'binnum' or 'topo'.

  output is xarr, a 1D array representing the x-axis, yarr, a 1D 
  array representing the y-axis, and data, a 2D array of the 
  data"""

  import MySQLFunction, struct, threeplot, pylab, numpy, command

  #Create command to send to database
  if ('c.specid=s.specid' or 's.specid=c.specid') not in where:
   where = where + ' and c.specid=s.specid'
  cmd = command.generate('s.coarsespec,c.obstime,c.IF1_rfFreq','spec s, config c', where=where)
  
  #Fetch data from mysql
  fromdb = MySQLFunction.mysqlcommand(cmd)

  #Create arrays from data
  length = len(fromdb)
  coarsespec = [fromdb[x][0] for x in xrange(length)]
  time = numpy.array([fromdb[x][1] for x in xrange(length)])
  
  #Freq type?
  if freqtype=='topo':
    rfFreq = fromdb[0][2]
    RFLO = rfFreq - 50000000
    yarr = numpy.linspace(RFLO, RFLO+200000000, 4096)
    yarr = yarr / 1000000
  else: 
    yarr = numpy.arange(1,4097,1)
  
  #Create seconds array
  time = time-min(time)
  xarr = time*86400

  #Unpack data from blob
  data = [numpy.array(struct.unpack('i'*4096,coarsespec[x])) for x in xrange(length)]
  data = numpy.transpose(data)

  return (xarr,yarr,data)

def makeplot(xarr,yarr,data,where='',freqtype='binnum',vlim=(-1,-1), tslim=(-1,-1),saveplot=''):
   """Method to produce the three panel
   dynamic spectrum plot. The main panel
   is a pcolormesh figure of data with
   the mesh defined by xarr and yarr.
   The bottom panel shows a time series of
   the 2D data, and the right panel shows
   the average bandpass

   freqtype is the frequency type for the pcolormesh, either 
   'binnum' or 'topo'.

   Input:
   where is a string to include additional information to 
   narrow the results. typically it will be used to specify a 
   range of specids. each column name MUST be prefixed with 
   the first letter of the table name and a period, like 
   c.obstime. don't forget to include 's.specid=c.specid if 
   referencing config and spec. do not include the word 'where' 
   at the beginning or the semicolon at the end. all other common 
   mysql syntax rules apply. Ex: 's.specid>1 and s.specid<=20 and 
   c.beamnum!=8 and c.specid=s.specid'. don't include hit table.

   saveplot='' allows you to save the plot by inputting its name 
   as a string. if left blank, no plot is saved

   Output:
   Figure instance
   """
   import numpy, pylab, jd2gd, MySQLFunction, command

   #Calculate the time series and average bandpass
   #  for the subpanel plots
   tseries=numpy.mean(data, axis=0)
   bandpass=numpy.mean(data, axis=1)

   #If no plot limits specified,
   if vlim==(-1,-1):
       vlim=(numpy.min(data), numpy.max(data))
   if tslim==(-1,-1):
       tslim=(numpy.min(tseries), numpy.max(tseries))

   #Create figure instance, add axes and turn off labels
   fig=pylab.figure(figsize=(12,7))
   ax1 = fig.add_axes([0.1, 0.3, 0.6, 0.6])
   ax2 = fig.add_axes([0.1, 0.1, 0.6, 0.2], sharex=ax1)
   ax3 = fig.add_axes([0.7, 0.3, 0.2, 0.6], sharey=ax1)

   for i in ax3.get_yticklabels(): i.set_visible(False)
   for i in ax3.get_xticklabels(): i.set_rotation(270)
   for i in ax1.get_xticklabels(): i.set_visible(False)

   #Generate 2D mesh
   T,F=numpy.meshgrid(xarr,yarr)

   #Add plots
   ax1.pcolormesh(T,F,data, vmin=vlim[0], vmax=vlim[1])
   ax2.plot(xarr, tseries, 'r.')
   ax3.step(bandpass, yarr, 'g-')

   #Set axes labels
   ax2.set_xlabel('Time (Seconds)')

   if freqtype=='binnum':
     ax1.set_ylabel('Frequency channel')
   elif freqtype=='topo':
     ax1.set_ylabel('Frequency (MHz)')

   ax1.set_title('Dynamic Spectra - Coarse Bins')
   ax2.set_ylabel('Mean Intensity')
   ax1.set_xlim((min(xarr), max(xarr)))
   ax1.set_ylim((min(yarr), max(yarr)))
   ax2.set_ylim((tslim[0], tslim[1]))

   #Gather additional info
   if where=='':
     cmd = command.generate('specid,obstime,AGC_Time','config')
   elif 'c.' not in where:
     where = where + ' and s.specid=c.specid'
     cmd = command.generate('s.specid,c.obstime,c.AGC_Time','config c, spec s',where=where)

   data = MySQLFunction.mysqlcommand(cmd)
  
   #Separate into arrays
   length = len(data)
   specid = [data[x][0] for x in range(length)]
   day = numpy.asarray([data[x][1] for x in range(length)])
   fracday = numpy.asarray([float(data[x][2])/86400000 for x in range(length)])
   time = day + fracday  

   #Get specid count
   uniq_IDs = set(specid)
   speccount = len(uniq_IDs)

   #Determine start and end dates
   start = min(time)
   end = max(time)
 
   #Create Gregorian date from obstime
   start = jd2gd.caldate(start)
   end = jd2gd.caldate(end)
   dates = ['January','February','March','April','May','June','July',
  'August','September','October','November','December']
   start = [str(start[x]) for x in range(len(start))]
   end = [str(end[x]) for x in range(len(end))]

   #Insert zeros to make formatting nice
   if float(start[2])<10:
     start[2] = '0' + start[2]
   if float(start[3])<10:
     start[3] = '0' + start[3]
   if float(start[4])<10:
     start[4] = '0' + start[4]
   if float(start[5])<10:
     start[5] = '0' + start[5]
   if float(end[2])<10:
     end[2] = '0' + end[2]
   if float(end[3])<10:
     end[3] = '0' + end[3]
   if float(end[4])<10:
     end[4] = '0' + end[4]
   if float(end[5])<10:
     end[5] = '0' + end[5]

   #Compile date strings
   date1 = start[0]+' '+dates[int(start[1])-1]+' '+start[2]+' '+start[3]+':'+start[4]+':'+start[5][:4]
   date2 = end[0]+' '+dates[int(end[1])-1]+' '+end[2]+' '+end[3]+':'+end[4]+':'+end[5][:4]

   #Add text to figure
   pylab.figtext(0.73,.175,'SpecID Count: %s' %speccount)
   pylab.figtext(0.73,.15,'Start: %s' %date1)
   pylab.figtext(0.73,.125,'End: %s' %date2)

   #Save plot?
   if saveplot != '':
     pylab.savefig('%s' %saveplot)

   return fig

def loop(interval=1,start=55678,end=55688):
  """ Loops through data in the database
  and makes plots during specific times over specific intervals.

  interval is the length of time for data to be included in each 
  plot, measured in days.

  start is the modified julian date at which to begin the looping,
  and end is time at which to terminate the looping

  plots are also further subdivided into individual beams. plots 
  are saved with auto-incremented names."""

  import numpy

  #User ok with inputs?
  temp = raw_input('Defaults: \nFrequency Type: Bin number \nvlim: min/max of data \ntslim: min/max of data \nIs this ok? y/n  ')
  if temp=='n':
    freq_type = raw_input('Frequency Type: topo/bary/binnum  ')
    vlim = input('vlim: (tuple of values)  ')
    tslim = input('tslim: (tuple of values) ')
  else: freq_type,vlim,tslim='binnum',(-1,-1),(-1,-1)

  #Set loop limits
  limits = numpy.arange(start,end+interval,interval)
  loops = len(limits)-1

  #Execute loop
  for x in xrange(loops):
    
    #Determine time bounds
    obstime_l = limits[x]
    obstime_h = limits[x+1]
    
    for x in xrange(14):
      #Create where modifier based on user inputs
      where = 'c.obstime>=%f and c.obstime<%f and c.beamnum=%i and c.specid=s.specid' %(obstime_l,obstime_h,x)

      #Create plot name
      name = 'dynspec_coarse_from_%s_to_%s_beam%i.png'%(obstime_l,obstime_h,x)
      
      #Execute script
      makeplot(where,freq_type,vlim,tslim,name)
    
