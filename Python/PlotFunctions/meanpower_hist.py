import sys

def main(where='',cumulative='False', dolog='False',saveplot=''):
  """ Fetches data for a histogram of hits per mean power bin
  and plot them.

  where is a string to include additional information to 
  narrow the results. typically it will be used to specify a 
  range of specids. each column name MUST be prefixed with 
  the first letter of the table name and a period, like 
  c.obstime. don't forget to include 'h.specid=c.specid if 
  referencing config and hit. do not include the word 'where' 
  at the beginning or the semicolon at the end. all other common 
  mysql syntax rules apply. Ex: 'h.specid>1 and h.specid<=20 and 
  c.beamnum!=8 and c.specid=h.specid'. 

  setting cumulative='True' makes a cumulative histogram as mean
  power increases.

  setting dolog='True' makes the y-axis (count) logarithmic

  saveplot allows the user to have the figure saved by 
  inputting the file name. if left empty, no file will be saved

  returns a figure instance. """

  #Get data
  bins,count = fetchdata(where=where,cumulative=cumulative,dolog=dolog)
  
  #Plot data
  fig = makeplot(where=where,bins=bins,count=count,dolog=dolog,cumulative=cumulative,saveplot=saveplot)
  
  return fig

if __name__=="__main__":
  main()
  
def fetchdata(where='',cumulative='False',dolog='False',savedata=''):
  """ Fetches data for a histogram of hits per mean power bin.

  where is a string to include additional information to 
  narrow the results. typically it will be used to specify a 
  range of specids. each column name MUST be prefixed with 
  the first letter of the table name and a period, like 
  c.obstime. don't forget to include 'h.specid=c.specid if 
  referencing config and hit. do not include the word 'where' 
  at the beginning or the semicolon at the end. all other common 
  mysql syntax rules apply. Ex: 'h.specid>1 and h.specid<=20 and 
  c.beamnum!=8 and c.specid=h.specid'. 

  setting cumulative='True' makes a cumulative histogram as mean
  power increases

  savedata allows the user to have the data saved by 
  inputting the file name. data is saved as an ASCII file. if 
  left empty, no file will be saved

  returns two arrays, bins and count. bins are LEFT edges"""

  import numpy, MySQLFunction, command

  #Create command to pass to mysql
  if 'c.' in where:
    cmd = command.generate('h.meanpower','config c, hit h', where=where)
  else:
    cmd = command.generate('h.meanpower','hit h',where=where)
  
  #Send command to mysql, return results
  data = MySQLFunction.mysqlcommand(cmd)

  #Data not empty?
  if len(data)>0:

    #Turn data into array
    data = numpy.array([x[0] for x in data])

    #Create linearly spaced bins
    bins = list(numpy.linspace(50,500,91))
    bins.append(max(data))

    #Histogram data
    count,bins = numpy.histogram(data,bins)
    
    #Normalize data if not log
    if dolog!='True':
     norml = float(numpy.sum(count))
     count = [x/norml for x in count]

    #Cumulative?
    if cumulative=='True':
      count = list(numpy.cumsum(count))
  
    #Save data?
    if savedata!='':
      numpy.savetxt('%s' %savedata,(bins,count))
  
  
  else: bins,count=[],[]
 
  return (bins,count)
  
def makeplot(bins,count,where='',dolog='False',cumulative='False',saveplot=''):
  """Creates histogram of hits per mean power bin.

  where is a string to include additional information to 
  narrow the results. typically it will be used to specify a 
  range of specids. each column name MUST be prefixed with 
  the first letter of the table name and a period, like 
  c.obstime. don't forget to include 'h.specid=c.specid if 
  referencing config and hit. do not include the word 'where' 
  at the beginning or the semicolon at the end. all other common 
  mysql syntax rules apply. Ex: 'h.specid>1 and h.specid<=20 and 
  c.beamnum!=8 and c.specid=h.specid'. 

  setting cumulative='True' makes a cumulative histogram as mean
  power increases

  setting dolog='True' makes the y-axis (count) logarithmic

  saveplot allows the user to have the figure saved by 
  inputting the file name. if left empty, no file will be saved

  returns a figure"""

  import pylab, MySQLFunction, command, jd2gd, math, numpy

  #Data to plot?
  if len(bins) != 0:

   #Initialize figure
   fig=pylab.figure(figsize=(12,7))
   ax1 = fig.add_axes([0.1, 0.14, 0.85, 0.75])

   #Determine bar width
   width = bins[1]-bins[0]

   #Logarithmic?
   if dolog != 'True':
     pylab.bar(bins[:-1],count,width=width)
     ylabel = 'Count'
     var = min(count)*0.5
   else:
     pylab.bar(bins[:-1],count,width=width,log='True')
     ylabel = 'Count (Logarithmic)'
     bottom = int(math.floor(numpy.log10(min(count)+1)))
     var = 10**(bottom)

   #Configure ticks
   pylab.xticks([0,50,100,150,200,250,300,350,400,450,500,500+width],['0','50','100','150','200','250','300','350','400','450','500','%d'%max(bins)])

   #Rotate xticks
   for i in ax1.get_xticklabels(): i.set_rotation(45)

   #Cumulative?
   if cumulative != 'True':  
     cumltv = ''
   else:  
     cumltv = '(Cumulative)'

   #Set axes limits
   v = [min(bins),500+width,var,max(count)*1.1]
   pylab.axis(v)

   #Add grid
   pylab.grid(True,which='both')

   #Add labels
   pylab.xlabel('Mean Power')
   pylab.ylabel('%s'%ylabel)
   pylab.title('Hit Count Per Mean Power Bin %s'%cumltv)

   #Get extra info for plot
   if where=='':
     cmd = command.generate('specid,obstime,AGC_Time','config')
   elif 'c.' not in where:
     where = where + ' and h.specid=c.specid'
   cmd = command.generate('c.specid,c.obstime,c.AGC_Time','config c, hit h',where=where)

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

   # determine start and end dates
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
   pylab.figtext(0.1,.945,'SpecID Count: %s' %speccount)
   pylab.figtext(0.95,.97,'Start: %s' %date1, ha='right')
   pylab.figtext(0.95,.945,'End:   %s' %date2, ha='right')

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

  import numpy

  #User ok with inputs?
  temp = raw_input('Defaults: \nCumulative: No \nLogarithmic: No \nIs this ok? y/n  ')
  if temp=='n':
    cumulative = raw_input('Cumulative: True/False  ')
    dolog = raw_input('Logarithmic: True/False  ')
  else: cumulative,dolog='False','False'

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
      name = 'meanpower_hist_from_%s_to_%s_beam%i.png'%(obstime_l,obstime_h,x)
      
      #Execute script
      main(where=where,cumulative=cumulative,dolog=dolog,saveplot=name)
    
