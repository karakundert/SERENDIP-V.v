import sys

def main(maximum=24,histtype='fracmax',where='',saveplot=''):
  """Fetches data for event count per coarse frequency bin
  and plots it.

  maximum is the maximum number of allowed hits per coarse bin

  histtype specifies the type of histogram you intend to 
  plot: 
  
  'fracmax' is the fraction of spectra that reach the 
  maximum for each coarse bin, and the default option, 
  
  '%full' is the percent full each coarse bin is after adding   
  events for all desired spectra, and
 
  'maxcount' is the number of times each bin reaches the maximum

  where is a string to include additional information to 
  narrow the results. typically it will be used to specify a 
  range of specids. each column name MUST be prefixed with 
  the first letter of the table name and a period, like 
  c.obstime. don't forget to include 'h.specid=c.specid if 
  referencing table config. do not include the word 'where' 
  at the beginning or the semicolon at the end. all other common 
  mysql syntax rules apply. Ex: 'h.specid>1 and h.specid<=20 and 
  c.beamnum!=8 and c.specid=h.specid'. 

  saveplot allows the user to have the figure saved by 
  inputting the file name. if left empty, no file will be saved

  returns a figure instance. """

  #Get data
  bins,count = fetchdata(maximum,histtype,where)
  
  #Plot data
  fig = makeplot(bins,count,maximum,histtype,where,saveplot)
  
  return fig

if __name__=="__main__":
  main()

def fetchdata(maximum=24,histtype='fracmax',where='',savedata=''):
  """Fetches data for event count per coarse frequency bin.

  maximum is the maximum number of allowed hits per coarse bin

  histtype specifies the type of histogram you intend to 
  plot: 
  
  'fracmax' is the fraction of spectra that reach the 
  maximum for each coarse bin, and the default option, 
  
  '%full' is the percent full each coarse bin is after adding   
  events for all desired spectra, and
 
  'maxcount' is the number of times each bin reaches the maximum

  where is a string to include additional information to 
  narrow the results. typically it will be used to specify a 
  range of specids. each column name MUST be prefixed with 
  the first letter of the table name and a period, like 
  c.obstime. don't forget to include 'h.specid=c.specid if 
  referencing table config. do not include the word 'where' 
  at the beginning or the semicolon at the end. all other common 
  mysql syntax rules apply. Ex: 'h.specid>1 and h.specid<=20 and 
  c.beamnum!=8 and c.specid=h.specid'. 

  savedata allows the user to have the data saved by 
  inputting the file name. data is saved as an ASCII file. if 
  left empty, no file will be saved

  returns two arrays, bin and count"""

  import MySQLFunction, command, math, numpy, collections, itertools

  #Create command to pass to mysql
  if 'c.' in where:
    cmd = command.generate('h.binnum,h.specid','config c, hit h', where=where)
  else:
    cmd = command.generate('h.binnum,h.specid','hit h',where=where)

  #Send command and return results
  data = MySQLFunction.mysqlcommand(cmd)

  #Round bin numbers down to nearest coarsebin
  data = [(math.floor(data[x][0]/32768),data[x][1]) for x in xrange(len(data))]

  #Initialize bin array
  bins = numpy.arange(0,4097,1)

  #Depending on histtype, compile data:
  if histtype!='%full':

    #Group data by specid
    res = collections.defaultdict(list)
    for v,k in data: res[k].append(v)
    data = [{'specid':k, 'coarsebin':v} for k,v in res.items()]

    #Histogram each spectrum
    length = len(data)
    hist_temp = [(numpy.histogram(data[x]['coarsebin'],bins)) for x in xrange(length)]

    #Make a list of lists of full bins
    fullbins = [[y for y in numpy.where(hist_temp[x][0]==maximum)[0]] for x in xrange(length)]
    
    #Unpack fullbins into a single list
    fullbins = list(itertools.chain(*fullbins))
    
    #Histogram the full bins
    count = numpy.histogram(fullbins,bins)[0]

    if histtype=='fracmax':
      
      #Divide by number of spectra to get fraction
      count = numpy.array(count/float(length))
  elif histtype=='%full':
    length = len(data)
    
    #Pull out coarse bins, specids from data
    coarsebins = [data[x][0] for x in xrange(length)]
    specids = [data[x][1] for x in xrange(length)]

    #Histogram data
    count = numpy.histogram(coarsebins,bins)[0]

    #Determine total number of spectra
    uniq_IDs = list(set(specids))
    numspec = len(uniq_IDs)

    #Divide by total number possible to get percent
    count = numpy.array(count/float(numspec*24))
  
  #Cut off right-most bin
  bins = bins[:-1]
   
  #Save data?
  if savedata!='':
    numpy.savetxt('%s' %savedata,(bins,count))
  return (bins,count)

def makeplot(bins,count,maximum=24,histtype='fracmax',where='',saveplot=''):
  """Plots data for event count per coarse frequency bin.

  maximum is the maximum number of allowed hits per coarse bin
  
  histtype specifies the type of histogram you intend to 
  plot: 
  
  'fracmax' is the fraction of spectra that reach the 
  max (24) for each coarse bin, and the default option, 
  
  '%full' is the percent full each coarse bin is after adding   
  events for all desired spectra, and
 
  'maxcount' is the number of times each bin reaches the max 
  (24)

  where is a string to include additional information to 
  narrow the results. typically it will be used to specify a 
  range of specids. each column name MUST be prefixed with 
  the first letter of the table name and a period, like 
  c.obstime. do not include the word 'where' at the beginning 
  or the semicolon at the end. all other common mysql syntax 
  rules apply. Ex: 'h.specid>1 and h.specid<=20 and 
  c.beamnum!=8'. 

  saveplot allows the user to have the figure saved by 
  inputting the file name. if left empty, no file will be saved

  returns a figure"""

  import pylab, MySQLFunction, jd2gd, numpy, command

  #Data to plot?
  if len(bins) != 0:

   #Initialize figure
   fig=pylab.figure(figsize=(12,7))
   ax1 = fig.add_axes([0.1, 0.14, 0.85, 0.75])

   #Set axes limits
   v = [0,4096,0,max(count)]
   ax1.axis(v)

   #Configure xticks
   xticks = numpy.arange(0,4097,256)
   ax1.set_xticks(xticks)

   #Rotate xticks
   for i in ax1.get_xticklabels(): i.set_rotation(45)

   #Add grid
   pylab.grid(True)
  
   #Plot data
   pylab.bar(bins,count,width=1,align='center')

   #Get extra info for plot
   if 'c.' not in where:
     where = where + ' and h.specid=c.specid'
   cmd = command.generate('c.specid,c.obstime','config c, hit h',where=where)
   data = MySQLFunction.mysqlcommand(cmd)
  
   #Separate into arrays
   length = len(data)
   specid = numpy.asarray([data[x][0] for x in range(length)])
   time = numpy.asarray([data[x][1] for x in range(length)])

   #Get specid count
   uniq_IDs = set(specid)
   speccount = len(uniq_IDs)
   num = sum(count)
 
   #Get hit count and labels
   if histtype=='fracmax':
     title = 'Fraction of Spectra That Reach Maximum Allowed Hit Count Per Coarse Bin'
     hitcount = int(num*speccount)
     countlabel = 'Max Count'
   if histtype=='%full':
     title = 'Percent of Maximum Allowed Hits Per Coarse Bin'
     hitcount = int(num*speccount*24)
     countlabel = 'Hit Count'
   if histtype=='maxcount':
     title = 'Number of Times Each Coarse Bin Reached The Maximum Allowed Hit Count'
     hitcount = sum(count)
     countlabel = 'Max Count'
   pylab.xlabel('Coarse Bin Number')
   pylab.ylabel('Count')
   pylab.title('%s' %title)  

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

   #Add text to figure
   pylab.figtext(0.1,.97,'%s: %d' % (countlabel,hitcount))
   pylab.figtext(0.1,.945,'SpecID Count: %s' %speccount)
   pylab.figtext(0.95,.97,'Start: %s' %date1, ha='right')
   pylab.figtext(0.95,.945,'End:   %s' %date2, ha='right')
   pylab.figtext(0.1,.92,'Limit: %d' %maximum)

   #Save figure?
   if saveplot!='':
     pylab.savefig('%s'%saveplot)

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

  import numpy,sys

  #User ok with inputs?
  temp = raw_input('Defaults: \nMaximum: 24 \nHistogram Type: fraction of bins that reach maximum \nIs this ok? y/n  ')
  if temp=='n':
    maximum = input('Maximum: ')
    histtype = raw_input('Histogram Type: fracmax/%full/maxcount  ')
  else: maximum,histtype=24,'fracmax'

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
      where = 'c.obstime>=%f and c.obstime<%f and c.beamnum=%i and c.specid=h.specid' %(obstime_l,obstime_h,x)
      
      #Create plot name
      name = 'coarsebin_hist_from_%s_to_%s_beam%i.png'%(obstime_l,obstime_h,x)
      
      #Execute script
      main(maximum,histtype,where,name)
    
