import numpy
from MySQLFunction import *

def pointing(speclo,spechi):

 """
 An algorithm to find continuous
 pointings in S5 data. 

 Input: 
 speclo - specid for first spectrum
 spechi - specid for last spectrum

 Output:
 pt_start - specid of beginning of pointing
 pt_raw - the rawfile of pt_start
 pt_length - length of pointing, in seconds
 pt_time - local time at Arecibo (datetime object)
 pt_ra - right ascension of pt_start
 pt_dec - declination of pt_start
 """

 cmd='select specid,reserved from hit where specid>=%s and specid<=%s and rfi_found=0 group by specid;' %(speclo,spechi)

 #Get specids from hit table
 data = numpy.array(mysqlcommand(cmd))
 specid,reserved = numpy.transpose(data)

 #Find edges of pointings
 pt_start = specid[numpy.where((reserved[:-1]!=0) & (reserved[1:]==0))[0]]
 pt_end = specid[numpy.where((reserved[1:]!=0) & (reserved[:-1]==0))[0]]
 
 #Account for non-congruent vector lengths
 error = len(pt_end)-len(pt_start)
 if error==1:
  pt_start=numpy.insert(pt_start,0,specid[0])
 elif error==-1:
  pt_end=numpy.append(pt_end,specid[-1])

 #Compute length
 pt_length = numpy.trunc(0.671*(pt_end-pt_start))
 pt_length = pt_length.astype(int)

 #Get ra,dec,rawfile,time from config table
 spec_str = ', '.join([str(pt) for pt in pt_start])
 cmd2 = 'select ra,decl,rawfile,from_unixtime(AGC_SysTime) from config where specid in (%s);' %spec_str
 data2 = numpy.array(mysqlcommand(cmd2))
 pt_ra,pt_dec,pt_raw,pt_time=numpy.transpose(data2)
 pt_ra = pt_ra.astype(float)
 pt_dec = pt_dec.astype(float)

 return pt_start, pt_raw, pt_length, pt_time, pt_ra, pt_dec
