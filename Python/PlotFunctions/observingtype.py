def update(spec_init,spec_final):

 import MySQLFunction, numpy, math, sys

 for beam in range(14):

  #Create command to send to mysql
  cmd = 'select ra,decl,specid from config where specid>=%i and specid<=%i and beamnum=%i;' %(spec_init,spec_final,beam)
   
  #Execute command and return results
  alldata = MySQLFunction.mysqlcommand(cmd)

  #Run script on each set of consecutive spectra
  for v in range(2):

   if v==0:
    data = alldata[::2]
   elif v==1:
    data = alldata[1::2]

   #Calculate difference in ra,dec
   length = len(data)-1
   delta_ra = [15*(data[x][0]-data[x+1][0]) for x in xrange(length)]
   delta_dec = [data[x][1]-data[x+1][1] for x in xrange(length)]
   specid = [data[x][2] for x in xrange(length+1)]

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

   #Decide which observing type it is
   targeted = []
   slowdrift = []
   skydrift = []
   fastdrift = []
   
   #Separate by type
   for y in range(len(driftrate)-1):
    if driftrate[y]<=.0001:
      targeted.append(specid[y])
    elif driftrate[y]>.0001 and driftrate[y]<.0039:
      slowdrift.append(specid[y])
    elif driftrate[y]>=.0039 and driftrate[y]<=.0043:
      skydrift.append(specid[y])
    else: fastdrift.append(specid[y])

   #Last spectrum gets previous spectrum's designation
   if driftrate[-1]<=.0001:
     targeted.append(specid[-2])
     targeted.append(specid[-1])
   elif driftrate[-1]>.0001 and driftrate[-1]<.0039:
     slowdrift.append(specid[-2])
     slowdrift.append(specid[-1])
   elif driftrate[-1]>=.0039 and driftrate[-1]<=.0043:
     skydrift.append(specid[-2])
     skydrift.append(specid[-1])
   else: 
     fastdrift.append(specid[-2])
     fastdrift.append(specid[-1])

   #Compose strings, create query, and pass to db
   if len(targeted)>0:
    targeted_string = ', '.join([str(z) for z in targeted])
    query0 = 'update hit set reserved=0 where specid in (%s);'%targeted_string
    MySQLFunction.mysqlcommand(query0)
   
   if len(slowdrift)>0:
    slowdrift_string = ', '.join([str(z) for z in slowdrift])
    query1 = 'update hit set reserved=1 where specid in (%s);'%slowdrift_string
    MySQLFunction.mysqlcommand(query1)
   
   if len(skydrift)>0:
    skydrift_string = ', '.join([str(z) for z in skydrift])
    query2 = 'update hit set reserved=2 where specid in (%s);'%skydrift_string
    MySQLFunction.mysqlcommand(query2)
   
   if len(fastdrift)>0:
    fastdrift_string = ', '.join([str(z) for z in fastdrift])
    query3 = 'update hit set reserved=3 where specid in (%s);'%fastdrift_string
    MySQLFunction.mysqlcommand(query3)
   
   print 'beam %s updated %s/2'%(beam,v+1)
 
 return
