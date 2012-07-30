import sys

def main(freq_type='topo',increment_log=7,where='h.specid<100',dolog='False',saveplot=''):
  """Creates a histogram of hits versus frequency, 
  where frequency (or binnum) has been grouped by 
  increments of 10^(increment_log).

  freq_type is either 'topo', 'bary', or 'binnum'. default is
  topo

  increment_log is the log of the spacing between bins. must 
  be an integer

  where is a string to include additional information to 
  narrow the results. typically it will be used to specify a 
  range of specids. each column name MUST be prefixed with 
  the first letter of the table name and a period, like 
  c.obstime. include c.specid=h.specid if referncing both hit and 
  config tables. do not include the word 'where' at the beginning 
  or the semicolon at the end. all other common mysql syntax 
  rules apply. Ex: 'h.specid>1 and h.specid<=20 
  and c.beamnum!=8 and h.specid=c.specid'. by default it will
  grab only the first 99 specids.

  if dolog='True', the hit count is plotted on a log scale

  saveplot allows the user to have the plot saved by inputting
  the file name. if left empty, no file will be saved.

  output is a figure instance."""

  #Get data
  bins,count = fetchdata(freq_type,increment_log,where)
  
  #Plot data
  fig = makeplot(bins,count,freq_type,increment_log,where,dolog,saveplot)
  
  return fig

if __name__=="__main__":
  main()
  
def fetchdata(freq_type='topo',increment_log=7,where='h.specid<100',savedata=''):
  """Fetches data for creating a histogram of hits versus
  frequency, where frequency (or binnum) has been grouped by 
  increments of 10^(increment_log).

  freq_type is either 'topo', 'bary', or 'binnum'. default is
  topo

  increment_log is the log of the spacing between bins. must 
  be an integer

  where is a string to include additional information to 
  narrow the results. typically it will be used to specify a 
  range of specids. each column name MUST be prefixed with 
  the first letter of the table name and a period, like 
  c.obstime. include c.specid=h.specid if referncing both hit and 
  config tables. do not include the word 'where' at the beginning 
  or the semicolon at the end. all other common mysql syntax 
  rules apply. Ex: 'h.specid>1 and h.specid<=20 
  and c.beamnum!=8 and h.specid=c.specid'. by default it will
  grab only the first 99 specids.

  savedata allows the user to have the data saved by 
  inputting the file name. data is saved as an ASCII file. if 
  left empty, no file will be saved

  returns two arrays, bins and count"""

  import MySQLFunction, command, numpy, histcommand

  #Generate mysql command using histcommand
  cmd = histcommand.hist(freq_type,increment_log,where)
  
  #Pass command to mysql and return results
  data = MySQLFunction.mysqlcommand(cmd)

  #Split data into two arrays
  length = len(data)
  bins = numpy.asarray([data[x][0] for x in range(length)])
  count = numpy.asarray([data[x][1] for x in range(length)])

  #Save data?
  if savedata!='':
    numpy.savetxt('%s' %savedata,(bins,count))
  
  return (bins, count)

def makeplot(bins,count,freq_type='topo',increment_log=7,where='h.specid<100',dolog='False',saveplot=''):
  """Creates a histogram of hits at different
  frequencies, separated into bins by increments of 
  10^(increment_log).

  freq_type is either 'topo', 'bary', or 'binnum'. default is
  topo

  increment_log is the log of the spacing between bins. must 
  be an integer

  where is a string to include additional information to 
  narrow the results. typically it will be used to specify a 
  range of specids. each column name MUST be prefixed with 
  the first letter of the table name and a period, like 
  c.obstime. do not include the word 'where' at the beginning 
  or the semicolon at the end. all other common mysql syntax 
  rules apply. Ex: 'h.specid>1 and h.specid<=20 and 
  c.beamnum!=8'. by default it will grab only the first 99 
  specids.

  if dolog='True', the hit count is plotted on a log scale

  saveplot allows the user to have the plot saved by inputting
  the file name. if left empty, no file will be saved.

  returns a figure"""
  
  import pylab, numpy, math, MySQLFunction, command, jd2gd

  #Are there data to plot?
  if len(bins)!=0:

    #Initialize figure
    fig=pylab.figure(figsize=(12,7))
    ax1 = fig.add_axes([0.1, 0.14, 0.85, 0.75])

    #Configure x-ticks
    if freq_type!='binnum':
      lowbound = min(bins)/1000000
      uppbound = max(bins)/1000000
      xticks = numpy.arange(lowbound,uppbound+10**(increment_log-6),10)
      pylab.xticks(xticks)
    else: 
      lowbound = min(bins)
      uppbound = max(bins)
      xticks = numpy.arange(lowbound,uppbound+10**(increment_log),5000000)
      pylab.xticks(xticks)

    #Rotate xticks
    for i in ax1.get_xticklabels(): i.set_rotation(45)

    #Create xlabels
    if freq_type=='topo':
      xlabel = 'Topocentric Frequency (MHz)'
    elif freq_type=='bary':
      xlabel = 'Barycentric Frequency (MHz)'
    else: xlabel = 'Bin Number'

    #Determine bar width
    if freq_type != 'binnum':
      width = (10**increment_log)/1000000
    else: width = 10**increment_log

    #Make plots
    if dolog=='True' and freq_type!='binnum':
      pylab.bar(bins/1000000,count,log='True',width=width,align='center')
      ylabel = 'Count (Logarithmic)'
    elif dolog=='True':
      pylab.bar(bins,count,log='True',width=width,align='center')
      ylabel = 'Count (Logarithmic)'
    elif freq_type!='binnum':
      pylab.bar(bins/1000000,count,width=width,align='center')
      ylabel = 'Count'
    else:
      pylab.bar(bins,count,width=width,align='center')
      ylabel = 'Count'

    #Determine y-axis lower limit
    if dolog=='True':
      bottom = int(math.floor(numpy.log10(min(count)+1)))
      var = 10**bottom
    else:
      var = min(count)*0.5
     
    #Set axes limits
    if freq_type=='binnum':
      v = [0,uppbound+width/2,var,max(count)*1.1]
      pylab.axis(v)
    else:
      v=[lowbound-width/2,uppbound+width/2,var,max(count)*1.1]
      pylab.axis(v)
 
    #Add grid
    pylab.grid(True)
 
    #Add labels
    pylab.xlabel('%s'%xlabel)
    pylab.ylabel('%s'%ylabel)
    pylab.title('Event Count Per Bin')

    #Get extra info for plot
    if where=='':
      cmd = command.generate('specid,obstime,AGC_Time','config')
    elif 'c.' not in where:
      where = where + ' and h.specid=c.specid'
    cmd = command.generate('c.specid,c.obstime,c.AGC_Time','config c, hit h',where=where)
  
    #Send command to mysql, return results
    data = MySQLFunction.mysqlcommand(cmd)

    #Separate into arrays
    length = len(data)
    specid = [data[x][0] for x in range(length)]
    day = numpy.asarray([data[x][1] for x in range(length)])
    fracday = numpy.asarray([float(data[x][2])/86400000 for x in range(length)])
    time = day + fracday  

    #Get hit count and specid count
    uniq_IDs = set(specid)
    speccount = len(uniq_IDs)
    hitcount = sum(count)

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
    date1 = start[0]+' '+dates[int(start[1])-1]+' '+start[2]+' '+start[3]+':'+start[4]+':'+start[5][:2]
    date2 = end[0]+' '+dates[int(end[1])-1]+' '+end[2]+' '+end[3]+':'+end[4]+':'+end[5][:2]

    #Create dictionary of bin resolutions
    if freq_type!='binnum':
      binres = {0: '1 Hz', 1: '10 Hz', 2: '100 Hz', 3: '1 KHz', 4: '10 KHz', 5: '100 KHz',
    6: '1 MHz', 7: '10 MHz', 8: '100MHz', 9: '1 GHz'}
    else:
      binres = {0: '1 Bin', 1: '10 Bins', 2: '100 Bins', 3: '1,000 Bins', 4: '10,000 Bins', 5: '100,000 Bins',
    6: '1,000,000 Bins', 7: '10,000,000 Bins', 8: '100,000,000 Bins'}

    #Add text to figure
    pylab.figtext(0.1,.97,'Hit Count: %s' %hitcount)
    pylab.figtext(0.1,.92,'Bin Resolution: %s' %binres[increment_log])
    pylab.figtext(0.1,.945,'SpecID Count: %s' %speccount)
    pylab.figtext(0.95,.97,' Start: %s' %date1, ha='right')
    pylab.figtext(0.95,.945,'End:   %s' %date2, ha='right')

    #Save figure?
    if saveplot!='':
      pylab.savefig('%s'%saveplot)

    return fig

def loop(interval=1,start=55678,end=55688,beams='False'):
  """ Loops through data in the database
  and makes plots during specific times over specific intervals.

  interval is the length of time for data to be included in each 
  plot, measured in days.

  start is the modified julian date at which to begin the looping,
  and end is time at which to terminate the looping

  plots are also further subdivided into individual beams. plots 
  are saved with auto-incremented names.

  beams, set either to true or false, determines whether or not
  each plot is subdivided into individual beams."""

  import numpy

  #User ok with inputs?
  temp = raw_input('Defaults: \nFrequency Type: Topocentric \nBin Increment: 10,000,000 \nLog: No \nIs this ok? y/n  ')
  if temp=='n':
    freq_type = raw_input('Frequency Type: topo/bary/binnum  ')
    increment_log = input('Increment Log: must be an integer  ')
    dolog = raw_input('Log? True/False: ')
  else: freq_type,increment_log,dolog='topo',7,'False'

  #Set loop limits
  limits = numpy.arange(start,end+interval,interval)
  loops = len(limits)-1

  #Execute loop
  for x in xrange(loops):
    
   #Determine time bounds
   obstime_l = limits[x]
   obstime_h = limits[x+1]
    
   if beams=='True':
    for x in xrange(14):
      #Create where modifier based on user inputs
      where = 'c.obstime>=%f and c.obstime<%f and c.beamnum=%i and c.specid=h.specid' %(obstime_l,obstime_h,x)

      #Create plot name
      name = 'freqbin_hist_from_%s_to_%s_beam%i.png'%(obstime_l,obstime_h,x)
      
      #Execute script
      makeplot(freq_type,increment_log,where,dolog,name)
   elif beams=='False':
     #Create where modifier based on user inputs
      where = 'c.obstime>=%f and c.obstime<%f and c.specid=h.specid' %(obstime_l,obstime_h)

      #Create plot name
      name = '/home/jburt/Desktop/Frequency_Bins/freqbin_hist_from_%s_to_%s.png'%(obstime_l,obstime_h)
      
      #Execute script
      main(freq_type,increment_log,where,dolog,name)
