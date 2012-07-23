#http://asimpleweblog.wordpress.com/2010/06/20/julian-date-calculator/

import math
MJD0 = 2400000.5 # 1858 November 17, 00:00:00 hours 


def decimal_to_base60(deci,precision=1e-8):
  """Converts decimal number into sexagesimal number parts. 

 ``deci`` is the decimal number to be converted. ``precision`` is how
 close the multiple of 60 and 3600, for example minutes and seconds,
 are to 60.0 before they are rounded to the higher quantity, for
 example hours and minutes.
 """
  sign = "+" # simple putting sign back at end gives errors for small
             # deg. This is because -00 is 00 and hence ``format``,
             # that constructs the delimited string will not add '-'
             # sign. So, carry it as a character.
  if deci < 0:
    deci = abs(deci)
    sign = "-" 

  frac1, num = math.modf(deci)
  num = int(num) # hours/degrees is integer valued but type is float
  frac2, frac1 = math.modf(frac1*60.0)
  frac1 = int(frac1) # minutes is integer valued but type is float
  frac2 *= 60.0 # number of seconds between 0 and 60 

  # Keep seconds and minutes in [0 - 60.0000)
  if abs(frac2 - 60.0) < precision:
    frac2 = 0.0
    frac1 += 1
  if abs(frac1 - 60.0) < precision:
    frac1 = 0.0
    num += 1 

  return (sign,num,frac1,frac2)

def caldate(mjd):
  """Given mjd return calendar date. 

 Retrns a tuple (year,month,day,hour,minute,second). The last is a
 floating point number and others are integers. The precision in
 seconds is about 1e-4. 

 To convert jd to mjd use jd - 2400000.5. In this module 2400000.5 is
 stored in MJD0.
 """
  MJD0 = 2400000.5 # 1858 November 17, 00:00:00 hours 

  modf = math.modf
  a = long(mjd+MJD0+0.5)
  # Julian calendar on or before 1582 October 4 and Gregorian calendar
  # afterwards.
  if a < 2299161:
    b = 0
    c = a + 1524
  else:
    b = long((a-1867216.25)/36524.25)
    c = a+ b - long(modf(b/4)[1]) + 1525 

  d = long((c-122.1)/365.25)
  e = 365*d + long(modf(d/4)[1])
  f = long((c-e)/30.6001)

  day = c - e - int(30.6001*f)
  month = f - 1 - 12*int(modf(f/14)[1])
  year = d - 4715 - int(modf((7+month)/10)[1])
  fracofday = mjd - math.floor(mjd)
  hours = fracofday * 24.0 

  sign,hour,minute,second = decimal_to_base60(hours)

  return (year,month,day,int(sign+str(hour)),minute,second)
