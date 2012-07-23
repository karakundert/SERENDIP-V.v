def fetchdata(freq_type='topo', specid=1, where='',writedata='False'):
  """ Fetches the coarse spectrum and event power data for 
  the input parameters. 
  
  freq_type is either 'topo' or 'bary'. The default is 'topo'

  specid is the specid to be plotted. If no value is 
  assigned, data from the first specid will be plotted.

  where is an optional string to further modify which hits 
  are plotted.only include columns from table "hit". do not 
  include the word 'where' or the semicolon at the end. all 
  other syntax rules apply.

  writedata='True' allows the user to have the data saved. 
  data are stored as ASCII files, one for each the coarse 
  spectrum and the hits, each containing two arrays of the 
  same length. writedata is set to 'False' by default. Files, 
  if saved, are named CoarseSpec_specid.txt and 
  Hits_specid.txt, where specid is the corresponding 
  numerical value.

  returns four arrays: hit_frequency, hit_eventpower, 
  coarsespec_frequency, coarsespec_power"""

  import MySQLFunction, command, numpy, struct

  #Create full column name from freq_type
  if freq_type=='topo':
    freq_type = 'topocentric_freq'
  elif freq_type=='bary':
    freq_type = 'barycentric_freq'

  #Create strings to put in command function
  col_name1 = '%s, eventpower' % freq_type
  table_name1 = 'hit'
  where1 = 'specid=%d' % specid
  
  #Change where1 if where string isn't empty
  if where != '' :
    where1 = where1 + ' and %s' %where

  col_name2 = 's.coarsespec, c.IF1_rfFreq'
  table_name2 = 'spec s, config c'
  where2 = 's.specid=%d and s.specid=c.specid' % specid

  #Create command to send to MySQL
  command1 = command.generate(col_name1,table_name1,where=where1)
  command2 = command.generate(col_name2, table_name2,where=where2)
  
  #Execute commands in MySQL
  data = MySQLFunction.mysqlcommand(command1)
  allelse = MySQLFunction.mysqlcommand(command2)
  
  #Separate data into component arrays
  length = len(data)
  freq = numpy.asarray([data[x][0] for x in range(length)])
  eventpower = numpy.asarray([data[x][1] for x in range(length)])
  
  blob = allelse[0][0]
  rfFreq = allelse[0][1]

  #Unpack blob
  coarsepowers = numpy.asarray(struct.unpack('i'*4096,blob))

  #Compute coarse spectrum frequencies, centered on each bin
  RFLO = rfFreq - 50000000
  coarsespec_freq = numpy.linspace(RFLO, RFLO+200000000, 4096)

  #Save data?
  if writedata == 'True':
    numpy.savetxt('CoarseSpec_%d.txt' %specid,(coarsespec_freq,coarsepowers))
    numpy.savetxt('Hits_%d.txt' %specid,(freq,eventpower))

  return (freq, eventpower, coarsespec_freq, coarsepowers)

def makeplot(freq_type='topo',specid=1,where='',dolog ='False',saveplot=''):
  """Uses the command.fetchdata function to gather frequency data for 
  a single specid, then plots both coarse power as a blue line and 
  event power as red X's on the same figure. x-axis is converted to MHz
  
  freq_type is either 'topo' or 'bary' (default is topo)

  specid is the value of the specid desired

  if dolog='True', the power on the y-axis will be logarithmic

  where is an optional string to further modify which hits are plotted.
  prefix all columns with an 'h' and a period, such as h.eventpower. do
  not include the phrase 'where' or the semicolon at the end. all other
  syntax rules apply.

  saveplot='' allows you to save the plot by inputting its name as a 
  string. if left blank, no plot is saved

  output is a figure."""
  
  import pylab, numpy, MySQLFunction, jd2gd, math

  #Fetch data using fetchdata
  freq, eventpower, coarsespec_freq, coarsepowers = fetchdata(freq_type,specid,where)

  #Plot coarse spectrum and hits

  #Initialize figure
  fig=pylab.figure(figsize=(12,7))
  ax1 = fig.add_axes([0.1, 0.12, 0.85, 0.75])
  
  #Log or not?
  if dolog=='True':
    pylab.semilogy(coarsespec_freq/1000000,coarsepowers,'b')
    pylab.semilogy(freq/1000000,eventpower,'rx')
    power = '(Logarithmic)' # affects y-axis label
  elif dolog=='False':
    pylab.plot(coarsespec_freq/1000000,coarsepowers,'b')
    pylab.plot(freq/1000000,eventpower,'rx')
    power = ''
  
  #Get additional info for text header
  cmd = 'select beamnum, ra, decl, obstime, AGC_Time,IF1_rfFreq from config where specid=%d' %specid
  data = MySQLFunction.mysqlcommand(cmd)
  
  #Combine systime with obstime to get complete time
  frac = float(float(data[0][4])/86400000)
  obstime = data[0][3] + frac

  #Create Gregorian date from obstime
  gd = jd2gd.caldate(obstime)
  dates = ['January','February','March','April','May','June','July',
  'August','September','October','November','December']
  gd = [str(gd[x]) for x in range(len(gd))]

  #Insert zeros to make formatting nice
  if float(gd[2])<10:
    gd[2] = '0' + gd[2]
  if float(gd[3])<10:
    gd[3] = '0' + gd[3]
  if float(gd[4])<10:
    gd[4] = '0' + gd[4]
  if float(gd[5])<10:
    gd[5] = '0' + gd[5]

  #Compile one date string
  date = gd[0] + ' ' + dates[int(gd[1])-1] + ' ' + gd[2] + ' ' + gd[3] + ':' + gd[4] + ':' + gd[5][:2]

  #Calculate center frequency
  rfFreq=int(data[0][5])
  rfFreq = rfFreq/1000000
  rfFreq = rfFreq-50
  cfreq = rfFreq + 100

  #Determine beam and polarization
  beam = int(data[0][0])
  beamnum = str(math.floor(float(beam)/2))[0]
  frac = float(beam)/2
  if math.modf(frac)[0]==0.0:
    newbeam = beamnum + 'a'
  else: newbeam = beamnum + 'b'

  #Add text to figure
  pylab.figtext(0.1,.97,'Beam: %s' % newbeam)
  pylab.figtext(0.3,.97,'RA: %s' %data[0][1])
  pylab.figtext(0.5,.97,'Dec: %s' %data[0][2])
  pylab.figtext(0.95,.97,'Date: %s' %date, ha='right')
  pylab.figtext(0.1,.92,'Hit Count: %s' %len(eventpower))
  pylab.figtext(0.95,.92,'Center Freq: %s MHz' %cfreq, ha='right')
  
  #Set x-scale
  lowbound = cfreq - 100
  uppbound = cfreq + 100
  xticks = numpy.linspace(lowbound,uppbound,21)
  pylab.xticks(xticks)

  #Rotate x-labels
  for i in ax1.get_xticklabels(): i.set_rotation(45)

  #Set labels and title
  pylab.xlabel('Frequency (MHz)')
  pylab.ylabel('Power %s' %power)
  pylab.title(' Coarse Spectrum and Hits for Specid=%d' %specid)
  
  #Set axis limits
  if len(eventpower) != 0:
    v = [lowbound,uppbound,min(coarsepowers),max(eventpower)+1000]
  else: v=[lowbound,uppbound,min(coarsepowers),max(coarsepowers)]
  pylab.axis(v)

  #Add grid
  pylab.grid(True)
  
  #Save plot?
  if saveplot != '':
    pylab.savefig('%s' %saveplot)

  return fig