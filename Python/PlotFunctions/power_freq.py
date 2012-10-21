import sys

def main(freqtype='topo',specid=1,dolog='False',dotext=True,where='',saveplot=''):
  """ Fetches the coarse spectrum and event power data for 
  the input parameters and plots them. 
  
  freq_type is either 'topo' or 'bary'. The default is 'topo'

  specid is the specid to be plotted. If no value is 
  assigned, data from the first specid will be plotted.

  where is an optional string to further modify which hits 
  are plotted.only include columns from table "hit". do not 
  include the word 'where' or the semicolon at the end. all 
  other syntax rules apply.

  if dolog='True', the power on the y-axis will be logarithmic

  saveplot='' allows you to save the plot by inputting its name as a 
  string. if left blank, no plot is saved

  returns a figure instance. """
  
  #Get data
  hitfreq, eventpower, rfi_found, coarsespec_freq, coarsepowers = fetchdata(freq_type=freqtype,specid=specid,where=where)
  
  #Plot data
  fig = makeplot(hitfreq=hitfreq,eventpower=eventpower,rfi_found=rfi_found, coarsespec_freq=coarsespec_freq,coarsepowers=coarsepowers,specid=specid,dolog=dolog,dotext=dotext,saveplot=saveplot)
  
  return fig

if __name__=="__main__":
  main()

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
  col_name1 = '%s, eventpower, rfi_found' % freq_type
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
  hitfreq = numpy.asarray([data[x][0] for x in range(length)])
  eventpower = numpy.asarray([data[x][1] for x in range(length)])
  rfi_found = numpy.asarray([data[x][2] for x in range(length)])
  
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

  return (hitfreq, eventpower, rfi_found, coarsespec_freq, coarsepowers)

def makeplot(hitfreq,eventpower,rfi_found,coarsespec_freq,coarsepowers,specid=1,dolog='False', dotext=True, saveplot=''):
  """Plots both coarse power (for coarse spectrum) as a blue line 
  and event power (for hits) as red X's on the same figure. 

  hitfreq is a list of frequencies for hits in a spectrum, eventpower
  is a list of the eventpowers, coarsespec_freq is a list of
  frequencies for the coarse spectra bins, and coarsepowers
  is a list of the powers in each bin.   

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

#  pylab.rc('text', usetex=True)
#  pylab.rc('font', family='serif') 

  #Get additional info for text header
  cmd = 'select beamnum, ra, decl, obstime, IF1_rfFreq, thrscale from config where specid=%d' %specid
  data = MySQLFunction.mysqlcommand(cmd)
  
  #Combine systime with obstime to get complete time
  obstime = data[0][3]

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
  rfFreq=int(data[0][4])
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

  #thrscale
  thrscale=float(data[0][5])/4.0

  #PLOTTING
  #Initialize figure
  fig=pylab.figure(figsize=(12,7))
  ax1 = fig.add_axes([0.1, 0.12, 0.85, 0.75])

  #Divide into RFI flagged or not
  ginds=numpy.where(rfi_found==0)[0]
  rinds=numpy.where(rfi_found>0)[0]  
  coarsepowers/=thrscale

  #Log or not?
  if dolog=='True':
    pylab.semilogy(coarsespec_freq/1000000,coarsepowers,'k')
    pylab.semilogy(hitfreq[rinds]/1000000,eventpower[rinds],'rx')
    pylab.semilogy(hitfreq[ginds]/1000000,eventpower[ginds],'bx')
  elif dolog=='False':
    pylab.plot(coarsespec_freq/1000000,coarsepowers,'k')
    pylab.plot(hitfreq[rinds]/1000000,eventpower[rinds],'rx')
    pylab.plot(hitfreq[ginds]/1000000,eventpower[ginds],'bx')
 
  #Add text to figure
  if dotext:
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
  pylab.xlabel('Frequency (MHz)', size=14)
  pylab.ylabel('Power (arb units)', size=14)
#  pylab.title(' Coarse Spectrum and Hits for Specid=%d' %specid)
  
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
