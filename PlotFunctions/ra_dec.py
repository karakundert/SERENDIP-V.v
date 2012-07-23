def fetchdata(where='', savedata=''):
  """Retrieves mysql data for RA and DEC.

  where is a string specifying which data from mysql to grab. 
  ONLY include columns from table 'config'. do not include 
  the word 'where' at the beginning or the semicolon at the 
  end. all other common mysql syntax rules apply.

  savedata allows the user to have the data saved by 
  inputting the file name. data is saved as an ASCII file. if 
  left empty, no file will be saved

  returns three arrays, ra, dec, and specid"""

  import MySQLFunction, command, numpy

  #Create command to send to mysql
  if not where:
    cmd = command.generate('ra,decl,specid','config')
  else: cmd = command.generate('ra,decl,specid','config',where=where)

  #Send command to mysql, return data
  data = MySQLFunction.mysqlcommand(cmd)

  #Separate data into two arrays
  length = len(data)
  ra = numpy.asarray([data[x][0] for x in range(length)])
  dec = numpy.asarray([data[x][1] for x in range(length)])
  specid = numpy.asarray([data[x][2] for x in range(length)])

  #Save data?
  if savedata!='':
    numpy.savetxt('%s' %savedata,(ra,dec,specid))

  return(ra,dec,specid)

def makeplot(where='',figtype='sky',saveplot=''):
  """ Makes a plot of RA and DEC after using fetchdata to 
  obtain the values for each.

  where is a string specifying which data from mysql to grab. 
  ONLY include columns from table 'config'. do not include 
  the word 'where' at the beginning or the semicolon at the 
  end. all other common mysql syntax rules apply.

  figtype is the figure type. default is 'cart' for cartesian 
  coordinates. 'sky' plots the ra and dec as a Mollweide
  projection

  saveplot allows you to save the figure by specifying the 
  file name as a string. if left empty, the figure is not 
  saved.

  returns a figure"""

  import pylab, numpy, jd2gd, command, MySQLFunction, math, astroconvert

  #Use fetchdata to obtain arrays
  ra, dec, specid = fetchdata(where)
  
  #Determine values to include in figure
  var1 = min(specid)
  var2 = max(specid)
  var3 = len(specid)

  #Get time info from database
  cmd = command.generate('obstime,AGC_Time','config',where=where)
  data = MySQLFunction.mysqlcommand(cmd)

  #Create list
  day = numpy.asarray([data[x][0] for x in xrange(len(data))])
  fracday = numpy.asarray([float(data[x][1])/86400000 for x in xrange(len(data))])
  time = day+fracday

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

  #Which fig type?
  if figtype=='cart':

    #Initialize figure
    fig=pylab.figure(figsize=(12,7))
    ax1 = fig.add_axes([0.1, 0.12, 0.85, 0.75])

    #Set axis limits
    v=[0,24,-1.3333,38.0333333]
    pylab.axis(v)

    #Plot data
    ax1.plot(ra,dec,'b+',label='spectra')
   
  else:
    #Convert RA to degrees
    length = len(ra)
    ra = [ra[x]*15 for x in range(length)]
    
    #Convert arrays to radians
    ra = [math.radians(ra[x]) for x in range(length)]
    dec = [math.radians(dec[x]) for x in range(length)]

    #Adjust ra scale
    ra = [ra[x]-numpy.pi for x in range(length)]
    
    #Create figure
    fig = pylab.figure(figsize=(12,7))
    ax1 = fig.add_axes([.1,.12,.70,.85],projection='mollweide')
    
    #Plot data
    ax1.scatter(ra,dec,label='spectra',marker='+')
    
    #Set xtick labels
    ax1.set_xticklabels(['2','4','6','8','10','12','14','16','18','20','22'])

  #Create l,b arrays
  b = [math.radians(5)]*360 + [math.radians(-5)]*360
  l = list(numpy.linspace(0,2*numpy.pi,360))*2
  
  #Pass l,b pairs to gal2eq
  bounds = []
  for x in range(720):
    bounds.append(astroconvert.gal2eq(l[x],b[x]))

  #Separate into component arrays
  ra_bounds = [bounds[x][0] for x in range(720)]
  dec_bounds = [bounds[x][1] for x in range(720)]

  #Convert to deg if necessary, and plot
  if figtype=='sky':
    ra_bounds = [ra_bounds[x]-numpy.pi for x in range(720)]
    ax1.scatter(ra_bounds,dec_bounds,edgecolor='none',c='r',label='galactic plane')
  else:
    ra_bounds = [math.degrees(ra_bounds[x])/15 for x in range(720)]
    dec_bounds = [math.degrees(dec_bounds[x]) for x in range(720)]
    ax1.plot(ra_bounds,dec_bounds,'r',label='galactic plane')

  #Set axis labels and title
  pylab.xlabel('RA (hours)')
  pylab.ylabel('Dec (degrees)')
  pylab.title('Right Ascension and Declination')

  #Add legend
  ax1.legend(bbox_to_anchor=(0,0,1,1),loc=0)

  #Add text to figure
  pylab.figtext(0.1,.97,'First Specid: %d' %var1)
  pylab.figtext(0.1,.945,'Last Specid: %d' %var2)
  pylab.figtext(0.1,.92,'Count: %d spectra' %var3)
  pylab.figtext(0.95,.97,'Start: %s' %date1, ha='right')
  pylab.figtext(0.95,.945,'End:   %s' %date2, ha='right')

  #Include grid
  pylab.grid(True)
 
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
  are saved with auto-incremented names."""

  import numpy

  #User ok with inputs?
  temp = raw_input('Defaults: \nFigure Type: Sky \nIs this ok? y/n  ')
  if temp=='n':
    fig_type = raw_input('Figure Type: cart/sky  ')
  else: fig_type='sky'

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
      where = 'obstime>=%f and obstime<%f and beamnum=%i' %(obstime_l,obstime_h,x)

      #Create plot name
      name = 'radec_from_%s_to_%s_beam%i.png'%(obstime_l,obstime_h,x)
      
      #Execute script
      makeplot(where,fig_type,name)
   elif beams=='False':

      #Create where modifier based on user inputs
      where = 'obstime>=%f and obstime<%f' %(obstime_l,obstime_h)

      #Create plot name
      name = '/home/jburt/Desktop/ra_dec/radec_from_%s_to_%s.png'%(obstime_l,obstime_h)
      
      #Execute script
      makeplot(where,fig_type,name)
