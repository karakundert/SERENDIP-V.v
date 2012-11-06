import sys

def main(where='',freqtype='topo',vlim=(-1,-1),frac=0.9,saveplot=''):
  """ Produces the dynamic spectrum plot for hits.

  where is a string to include additional information to 
  narrow the results. typically it will be used to specify a 
  range of specids. each column name MUST be prefixed with 
  the first letter of the table name and a period, like 
  c.obstime. don't forget to include 'h.specid=c.specid if 
  referencing config and hit. do not include the word 'where' 
  at the beginning or the semicolon at the end. all other common 
  mysql syntax rules apply. Ex: 'h.specid>1 and h.specid<=20 and 
  c.beamnum!=8 and c.specid=h.specid'.

  freqtype is the frequency type for the y-axis, either 
  'binnum', 'topo', or 'bary'.

  vlim is a tuple of (vmin,vmax). Values are used in conjuction
  with norm to normalize luminance data.

  frac is the fraction of hits, sorted by eventpower, before which
  the size is 0.1 and after which the size is 1

  saveplot allows the user to have the figure saved by 
  inputting the file name. if left empty, no file will be saved

  returns a figure instance. """

  #Get data
  eventpower,freq,time = fetchdata(where,freqtype)
  
  #Plot data
  fig = makeplot(eventpower,freq,time,where,freqtype,vlim,frac,saveplot)
  
  return fig

if __name__=="__main__":
  main()
  
def fetchdata(where='',freqtype='topo',savedata=''):
  """Fetches data to produce the dynamic spectrum plot for hits.

  where is a string to include additional information to 
  narrow the results. typically it will be used to specify a 
  range of specids. each column name MUST be prefixed with 
  the first letter of the table name and a period, like 
  c.obstime. don't forget to include 'h.specid=c.specid if 
  referencing config and hit. do not include the word 'where' 
  at the beginning or the semicolon at the end. all other common 
  mysql syntax rules apply. Ex: 'h.specid>1 and h.specid<=20 and 
  c.beamnum!=8 and c.specid=h.specid'.

  freqtype is the frequency type for the y-axis, either 
  'binnum', 'topo', or 'bary'.

  returns three arrays: eventpower,frequency (in MHz),time (in 
  seconds since first spectra in data set)"""

  import MySQLFunction, numpy, command

  # create full column name from freq_type
  if freqtype=='topo':
    freqtype = 'h.topocentric_freq'
  elif freqtype=='bary':
    freqtype = 'h.barycentric_freq'
  elif freqtype=='binnum':
    freqtype = 'h.binnum'

  # generate mysql command
  if ('c.specid=h.specid' or 'h.specid=c.specid') not in where:
    where = where + ' and c.specid=h.specid'
  cmd = command.generate('h.eventpower,%s,c.obstime'%freqtype,'hit h, config c',where=where)

  # send command to database and return results
  data = MySQLFunction.mysqlcommand(cmd)

  # separate data into individual arrays
  length = len(data)
  eventpower = numpy.asarray([data[x][0] for x in xrange(length)])
  if freqtype != 'h.binnum':
    freq = numpy.asarray([data[x][1]/1000000 for x in xrange(length)])
  elif freqtype=='h.binnum': 
    freq=numpy.asarray([data[x][1] for x in xrange(length)])
  time = numpy.array([data[x][2] for x in xrange(length)])

  # create seconds array
  time = time-min(time)
  time = time*86400

  # save data?
  if savedata!='':
    numpy.savetxt('%s' %savedata,(eventpower,freq,time))

  return (eventpower,freq,time)

def makeplot(eventpower,freq,time,errbar=[0], where='',freqtype='topo',vlim=(-1,-1),frac=0.9,saveplot=''):
  """Produces a 'confetti plot' of spectra dynamically. 

  freqtype is the frequency type, either 'binnum', 'bary', or 
  'topo'.

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

  vlim is a tuple of (vmin,vmax). Values are used in conjuction
  with norm to normalize luminance data.

  frac is the fraction of hits, sorted by eventpower, before which
  the size is 0.1 and after which the size is 1

  saveplot='' allows you to save the plot by inputting its name 
  as a string. if left blank, no plot is saved

  Output:
  Figure instance
  """
  import pylab, numpy, MySQLFunction, command, jd2gd, math

  # initialize figure
  fig=pylab.figure(figsize=(12,7))
  ax1 = fig.add_axes([0.1, 0.14, 0.85, 0.75])

  #If no plot limits specified,
  if vlim==(-1,-1):
    vlim=(numpy.min(eventpower), numpy.max(eventpower))

  # create array of point sizes
  sorted = numpy.sort(eventpower)
  index = math.floor(frac*len(eventpower))
  cutoff = eventpower[index]
  size = [.1 if eventpower[x]<cutoff else 1 for x in xrange(len(eventpower))]

  # plot data
  if len(errbar)>1:
    size=20
    pylab.errorbar(time,freq,xerr=errbar,fmt=None,ecolor='k', capsize=0.0)
  pylab.scatter(time,freq,s=size,c=eventpower,edgecolors='none',vmin=vlim[0],vmax=vlim[1])


  # add grid
  pylab.grid(True,which='both')

  # add labels
  ax1.set_xlabel('Time (seconds)')
  ax1.set_title('Dynamic Spectra - Hits')

  if freqtype=='binnum':
    ax1.set_ylabel('Frequency channel')
  elif freqtype=='topo':
    ax1.set_ylabel('Topocentric Frequency (MHz)')
  elif freqtype=='bary':
    ax1.set_ylabel('Barycentric Frequency (MHz)')

  # gather additional info
  if where=='':
    cmd = command.generate('specid,obstime,AGC_Time,IF1_rfFreq','config')
  elif 'c.' not in where:
    where = where + ' and h.specid=c.specid'
    cmd = command.generate('h.specid,c.obstime,c.AGC_Time,c.IF1_rfFreq','hit h, config c',where=where)
  else:
    where = where + ' and h.specid=c.specid'
    cmd = command.generate('h.specid,c.obstime,c.AGC_Time,c.IF1_rfFreq','hit h, config c',where=where)

  data = MySQLFunction.mysqlcommand(cmd)
  
  # separate into arrays
  length = len(data)
  specid = [data[x][0] for x in xrange(length)]
  day = numpy.asarray([data[x][1] for x in xrange(length)])

  # get specid and hit count
  uniq_IDs = set(specid)
  speccount = len(uniq_IDs)
  hitcount = len(eventpower)

  # determine start and end dates
  start = min(day)
  end = max(day)

  # calculate the min and max RF from the center freq
  # scale y axis accordinly 
  rfctr=float(data[0][3])
  rflo=rfctr-50e6
  rfhi=rflo+200e6
  rflo-=5e6    #Add offsets to get hits away from plot edges
  rfhi+=5e6
  
  # guess whether data is given in Hz or MHz
  if numpy.log10(freq[0])<4:
    rflo/=1e6
    rfhi/=1e6

  # set axes limits
  v = [0,max(time),rflo,rfhi]
  pylab.axis(v)
  if min(freq)<rflo or max(freq)>rfhi: print "WARNING: There are hits outside freq limits"

  # create Gregorian date from obstime
  start = jd2gd.caldate(start)
  end = jd2gd.caldate(end)
  dates = ['January','February','March','April','May','June','July',
  'August','September','October','November','December']
  start = [str(start[x]) for x in range(len(start))]
  end = [str(end[x]) for x in range(len(end))]

  # insert zeros to make formatting nice
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

  # compile date strings
  date1 = start[0]+' '+dates[int(start[1])-1]+' '+start[2]+' '+start[3]+':'+start[4]+':'+start[5][:2]
  date2 = end[0]+' '+dates[int(end[1])-1]+' '+end[2]+' '+end[3]+':'+end[4]+':'+end[5][:2]

  # add text to figure
  pylab.figtext(0.4,.96,'Spectra Count: %s' %speccount)
  pylab.figtext(0.4,.935,'Hit Count: %s' %hitcount)
  pylab.figtext(0.61,.96,'Vmin,Vmax: %s %s' % (vlim[0], vlim[1]))
  pylab.figtext(0.61,.935,'ALFA RFctr: %4.1f' % (rfctr/1e6))
  pylab.figtext(0.8,.96,'Max Power: %s' %max(eventpower))
  pylab.figtext(0.8,.935,'Min Power: %s' %min(eventpower))
  pylab.figtext(0.1,.96,'Start: %s' %date1)
  pylab.figtext(0.1,.935,'End:   %s' %date2)

  # save plot?
  if saveplot != '':
    pylab.savefig('%s' %saveplot)

  return fig

def clusterplot(clclean, cllist, sidlist, saveplot=''):
    import matplotlib.pyplot as py
    import numpy
    from MySQLFunction import mysqlcommand
    from time import gmtime, asctime

    CI,SI,TF,EP,CW,CB=0,1,2,3,4,5

    fig=py.figure(figsize=(12,7))
    ax = fig.add_axes([0.1, 0.14, 0.85, 0.75])

    #Add the full list of clusters
    ax.plot(cllist[SI]+cllist[CW]/2, cllist[TF]/1e6, marker=',', color='#E8E8E8', linestyle='None')

    #Add "cleaned" clusters
    ax.errorbar(clclean[SI]+clclean[CW]/2, clclean[TF]/1e6, xerr=clclean[CW]/2, fmt=None, capsize=0)
    ax.scatter(clclean[SI]+clclean[CW]/2, clclean[TF]/1e6, s=10, c=clclean[CB], \
        vmin=0, vmax=6, edgecolors='None')

    for sid in sidlist:
        ax.axvline(sid, linestyle=':', color='Black')

    #Get info
    cmd='select AGC_SysTime, IF1_rfFreq from config where specid=%d' % sidlist[0]
    systime,rfctr=numpy.array(mysqlcommand(cmd)).transpose()
    systime=int(systime)
    rfctr=float(rfctr)/1e6+50

    sidlo,sidhi=min(cllist[SI]),max(cllist[SI])
    date1=asctime(gmtime(systime - 4*3600))
    date2=asctime(gmtime(systime - 4*3600 + 0.671*(sidhi-sidlo)))
    py.figtext(0.1,.96,'Start: %s' %date1)
    py.figtext(0.1,.935,'End:   %s' %date2)
    py.figtext(0.61,.96,'RFctr: %4.1f' % rfctr)

    #Set plot properties
    ax.set_xlim((sidlo, sidhi))
    ax.set_ylim((rfctr-105, rfctr+105))

    ax.set_xlabel('Specid')
    ax.set_ylabel('Frequency (MHz)')

    if saveplot != '': py.savefig(saveplot)

    return fig
