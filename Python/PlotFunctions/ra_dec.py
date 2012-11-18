#!/bin/env python
import sys, matplotlib
import MySQLFunction, command, numpy
import math, pylab, astroconvert

def main(where='',figtype='cart',ellipses='no',saveplot=''):
  """ Makes a plot of RA and DEC.

  where is a string specifying which data from mysql to grab. 
  ONLY include columns from table 'config'. do not include 
  the word 'where' at the beginning or the semicolon at the 
  end. all other common mysql syntax rules apply.

  figtype is the figure type. default is 'cart' for cartesian 
  coordinates. 'sky' plots the ra and dec as a Mollweide
  projection

  saveplot allows the user to have the figure saved by 
  inputting the file name. if left empty, no file will be saved

  returns a figure instance. """

  #Get data
  ra,dec,specid = fetchdata(where)
  
  #Plot data
  fig = makeplot(ra,dec,specid,where,figtype,ellipses,saveplot)
  
  return fig

if __name__=="__main__":
  main()

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

def makeplot(ra,dec,specid,where='',figtype='cart',ellipses='no',saveplot=''):
  """ Makes a plot of RA and DEC.

  where is a string specifying which data from mysql to grab. 
  ONLY include columns from table 'config'. do not include 
  the word 'where' at the beginning or the semicolon at the 
  end. all other common mysql syntax rules apply.

  figtype is the figure type. default is 'cart' for cartesian 
  coordinates. 'sky' plots the ra and dec as a Mollweide
  projection

  if ellipses='yes', the spectra are plotted as individual ellipses
  of fixed size corresponding to ALFA beam width (only for Cartesian
  coordinate axis)

  saveplot allows you to save the figure by specifying the 
  file name as a string. if left empty, the figure is not 
  saved.

  returns a figure"""

  import jd2gd, command

  #Determine values to include in figure
  var1 = min(specid)
  var2 = max(specid)
  var3 = len(specid)

  #Get time info from database
  cmd = command.generate('obstime','config',where=where)
  data = MySQLFunction.mysqlcommand(cmd)

  #Create list
  day = numpy.asarray([data[x][0] for x in xrange(len(data))])

  #Determine start and end dates
  start = min(day)
  end = max(day)
 
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

  #Which fig type?
  patches=[]
  if figtype=='cart':

    #Initialize figure
    fig=pylab.figure(figsize=(12,7))
    ax1 = fig.add_axes([0.1, 0.12, 0.85, 0.75])

    #Plot data
    if ellipses=='yes':
      for x,y in zip(ra,dec):
       circle=matplotlib.patches.Ellipse((x,y),width=.0038888,height=.058333,facecolor='b',edgecolor='b')
       patches.append(circle)
      p=matplotlib.collections.PatchCollection(patches)
      ax1.add_collection(p)
    else: ax1.scatter(ra,dec,s=.1,label='spectra')
   
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
    ax1.scatter(ra,dec,label='spectra',marker='+',c='b')
    
    #Set xtick labels
    ax1.set_xticklabels(['2','4','6','8','10','12','14','16','18','20','22'])

  #Create galactic plane lines
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

    #Set axis limits
    ax1.set_xlim(0, 24)
    ax1.set_ylim(0, 40)

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
  pylab.figtext(0.95,.97,' Start: %s' %date1, ha='right')
  pylab.figtext(0.95,.945,'End: %s' %date2, ha='right')

  #Include grid
  pylab.grid(True)
 
  #Save figure?
  if saveplot!='':
    pylab.savefig('%s'%saveplot)

  return fig

def histogram2d(xcoords,ycoords,dtype='Equatorial'):
 """Prepares data using numpy.histogram2D for a pcolormesh
 figure.

 Inputs: 
 xcoords: x coordinates of pointings in db
 ycoords: y coordinates of pointings in db
 dtype: either Galactic or Equatorial
 
 Outputs:
 """

 #Get axes ranges
 yrnge=max(ycoords)-min(ycoords)
 xrnge=max(xcoords)-min(xcoords)
 if dtype=='Equatorial':
  xrnge=xrnge*15
 width=3.5/60

 #Perform histogramming
 xbinnum=round(xrnge/width)
 ybinnum=round(yrnge/width)
 vals=numpy.histogram2d(xcoords,ycoords,[numpy.linspace(min(xcoords),max(xcoords),xbinnum),numpy.linspace(min(ycoords),max(ycoords),ybinnum)])[0]
 
 #Generate 2D mesh
 x,y=numpy.meshgrid(numpy.linspace(min(xcoords),max(xcoords),xbinnum),numpy.linspace(min(ycoords),max(ycoords),ybinnum))
 data = numpy.transpose(vals)

 return x,y,data

def allsky_plot(ra,dec,color='False',header='False',saveplot=''):
 """Plots a 2D histogram of pointing data,
 with a color scale giving the relative counts. One ra value
 and one dec value are supplied for each continuous pointing.

 Inputs:
 ra: array of RA values for pointings in db
 dec: array of DEC values for pointings in db
 color: whether or not to generate a color plot, default='False'
 header: whether or not to include header information, default='False'
 saveplot: string to specify name of plot
 
 Output is a figure"""

 #Perform histogramming
 x,y,data=histogram2d(ra,dec,dtype='Equatorial')

 #Create figure/axes
 fig = pylab.figure(figsize=(12,7))
 if header=='False':
  ax1 = fig.add_axes([.1,.12,.90,.85])
 else: ax1=fig.add_axes([.1,.12,.90,.75])

 #Add plot
 
 if color=='False':
  mesh=ax1.pcolormesh(x,y,data,cmap=pylab.get_cmap('gray_r'))
 elif color=='True':
  mesh=ax1.pcolormesh(x,y,data,cmap=pylab.get_cmap('spectral_r'))
 fig.colorbar(mesh)
 ax1.set_ylabel('Declination')
 ax1.set_xlabel('Right Ascension')
 pylab.grid(True)

 #Add galactic plane
  
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
 ra_bounds = [math.degrees(ra_bounds[x])/15 for x in range(720)]
 dec_bounds = [math.degrees(dec_bounds[x]) for x in range(720)]
 ax1.plot(ra_bounds,dec_bounds,'k--',label='galactic plane')
 ax1.legend(bbox_to_anchor=(0,0,1,1),loc=0) 

 #Fix axes
 ax1.set_xlim(min(ra),max(ra))
 ax1.set_ylim(min(dec),max(dec))

 #Add more info
 if header!='False':
  pylab.figtext(0.1,.95,'# Spectra: %d' %len(specid))
  pylab.figtext(0.1,.93,'Max Count: %d' %numpy.max(data))
 
 return fig

def palfa_plot(xcoords,ycoords,dtype='Galactic',color='False',xlim=[],ylim=[]):
 """Makes a plot of palfa pointings in either galactic
 or equatorial coords.

 Inputs: 
 xcoords- the x coordinates of the palfa pointings
 ycoords- the y coordinates of the palfa pointings
 dtype- either Galactic or Equatorial
 color- whether or not to plot in color, default='False'
 xlim- first and second elements of the array are the lower and upper
       bounds of the x-axis. If left empty, min/max values are generated
       from data.
 ylim- same as xlim
 note: specify BOTH xlim and ylim or NEITHER

 Output: 2 figures, for the inner and outer galaxy"""

 #Separate arrays
 ycoords=numpy.array(ycoords)
 xcoords=numpy.array(xcoords)

 if dtype=='Galactic':
  ind1=numpy.where(xcoords<120)[0]
  xcoord1=xcoords[ind1]
  ycoord1=ycoords[ind1]

  ind2=numpy.where(xcoords>120)[0]
  xcoord2=xcoords[ind2]
  ycoord2=ycoords[ind2]

 if dtype=='Equatorial':
  ind1=numpy.where(xcoords>12)[0]
  xcoord1=xcoords[ind1]
  ycoord1=ycoords[ind1]

  ind2=numpy.where(xcoords<12)[0]
  xcoord2=xcoords[ind2]
  ycoord2=ycoords[ind2]

 if len(xcoord1)>0:
  #Perform histogramming
  x1,y1,data1=histogram2d(xcoord1,ycoord1,dtype)

  #Initialize figure/axes
  fig1 = pylab.figure(figsize=(12,7))
  ax1=fig1.add_axes([.1,.12,.90,.85])

  #Create pcolormesh
  if color=='False':
   mesh1=ax1.pcolormesh(x1,y1,data1,cmap=pylab.get_cmap('gray_r'))
  else: mesh1=ax1.pcolormesh(x1,y1,data1,cmap=pylab.get_cmap('hot_r'))
  fig1.colorbar(mesh1)

  #Add axes labels, grid
  if dtype=='Galactic':
   ax1.set_ylabel('Galactic Latitude')
   ax1.set_xlabel('Galactic Longitude')
  elif dtype=='Equatorial':
   ax1.set_ylabel('Declination')
   ax1.set_xlabel('Right Ascension')
  pylab.grid(True)

  #Set axes limits
  if xlim==[] and ylim==[]:
   ax1.set_xlim(min(xcoord1),max(xcoord1))
   ax1.set_ylim(min(ycoord1),max(ycoord1))
  elif len(xlim)==2 and len(ylim)==2:
   ax1.set_xlim(xlim[0],xlim[1])
   ax1.set_ylim(ylim[0],ylim[1])

 if len(xcoord2)>0:
  #Perform histogramming
  x2,y2,data2=histogram2d(xcoord2,ycoord2,dtype)

  #Initialize figure/axes
  fig2 = pylab.figure(figsize=(12,7))
  ax2=fig2.add_axes([.1,.12,.90,.85])

  #Create pcolormesh
  if color=='False':
   mesh2=ax2.pcolormesh(x2,y2,data2,cmap=pylab.get_cmap('gray_r')) 
  else: mesh2=ax2.pcolormesh(x2,y2,data2,cmap=pylab.get_cmap('hot_r'))
  fig2.colorbar(mesh2)

  #Add axes labels, grid
  if dtype=='Galactic':
   ax2.set_ylabel('Galactic Latitude')
   ax2.set_xlabel('Galactic Longitude')
  elif dtype=='Equatorial':
   ax2.set_ylabel('Declination')
   ax2.set_xlabel('Right Ascension')
  pylab.grid(True)

  #Set axes limits
  if xlim==[] and ylim==[]:
   ax2.set_xlim(min(xcoord2),max(xcoord2))
   ax2.set_ylim(min(ycoord2),max(ycoord2))
  elif len(xlim)==2 and len(ylim)==2:
   ax2.set_xlim(xlim[0],xlim[1])
   ax2.set_ylim(ylim[0],ylim[1])
 
 pylab.show()
 return


