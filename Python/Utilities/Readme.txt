Method for interpolating obstime:

First, continuous intervals within the data were found. Continuous
intervals were defined to be intervals over which the systime for
consecutive spectra always incremented by either 0 or 1. Any more than
this constituted a break in continuous observing.

Second, a particular pattern was looked for within each interval. This
pattern occured when systime incremented by 1 in three consecutive spectra.
For this to happen, with a between-spectra interval of 671.08864ms 
(2^27 / 200e6), the spectrum prior to the 3 jumps would have HAD to be
in the final 13.26592ms of the second in which it occured.

To see this, imagine a spectrum being recorded with a particular 
1-second-resolution timestamp, but which occured 986.734ms after the time
on the timestamp. The 2nd spectrum would have a timestamp of 1 second greater,
and an additional component of 657.822ms (since each set of spectra are 
separated by 671.08ms. By the same logic, the 3rd spectrum would have a 
timestamp of 2 seconds greater than the first, and an additional component
of 328.91ms. Again, by the same logic, the 4th spectrum would have a timestamp
of 3 seconds greater than the first, and an additional component of 0ms had I
kept all the decimals. Therefore this is the lower bound, with the upperbound
being 13.26592ms greater (imagine shitfting all these values up by that amount). 

So, for each pattern found, the final spectrum after 3 consecutive SysTime 
jumps was given an additional 6.63296ms, halfway between the upper and lower
bounds. 

Third, each interval (between either the boundaries of the continous observing 
interval or the calibrated time values at the patterns) was linearly 
interpolated between spectra. These values are what you now see in the database.
The median value for the spacing came out to be ~671.034ms (extremely close to 
the expected spacing of 671.08864ms). Note that at the time of writing this 
there are only 3158976 spectra in the database.
