def update(spec_init,spec_final):

 import MySQLFunction, numpy, math, sys

 for beam in range(14):

  #Create command to send to mysql
  cmd = 'select ra,decl,specid from config where specid>=%i and specid<=%i and beamnum=%i;' %(spec_init,spec_final,beam)
   
  #Execute command and return results
  alldata = numpy.array(MySQLFunction.mysqlcommand(cmd))

  #Run script on each set of consecutive spectra
  for v in range(2):

   if v==0:
    ra,dec,specid=numpy.transpose(alldata[::2])
   elif v==1:
    ra,dec,specid=numpy.transpose(alldata[1::2])
    
   #Calculate difference in ra,dec
   delta_ra = 15*(ra[1:]-ra[:-1])
   delta_dec = dec[1:]-dec[:-1]

   #Correct for absolute declination
   dec_rad = 0.5*(numpy.radians(dec[1:]+dec[:-1]))
   delta_dec = numpy.degrees(numpy.cos(dec_rad)*numpy.radians(delta_dec))
   
   #Compute vector quadratically
   vec=numpy.sqrt(numpy.power(delta_ra,2)+numpy.power(delta_dec,2))

   #Calculate drift rate
   diff = specid[1]-specid[0]
   time = .67108864*diff
   driftrate = vec/time
   
   #Separate by observing type
   specid=specid.astype(int)
   targeted=specid[numpy.where(driftrate<=.0001)[0]]
   slowdrift=specid[numpy.where((driftrate>.0001) & (driftrate<.0039))[0]]
   skydrift=specid[numpy.where((driftrate>=.0039) & (driftrate<=.0043))[0]]
   fastdrift=specid[numpy.where(driftrate>.0043)[0]]

   #Last spectrum gets previous spectrum's designation
   if driftrate[-1]<=.0001:
     targeted=numpy.append(targeted,specid[-1])
   elif driftrate[-1]>.0001 and driftrate[-1]<.0039:
     slowdrift=numpy.append(slowdrift,specid[-1])
   elif driftrate[-1]>=.0039 and driftrate[-1]<=.0043:
     skydrift=numpy.append(skydrift,specid[-1])
   else: 
     fastdrift=numpy.append(fastdrift,specid[-1])

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
