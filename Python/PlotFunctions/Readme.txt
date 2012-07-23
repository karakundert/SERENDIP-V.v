A brief description of what each function does. Note: For some or all of
the functions, you will need files from the Libraries directory in the
appropriate directory on your computer (or the correct Python path). 

coarsebin_hist: Generates plots of event count per coarse frequency bin. 
Can plot any one of the following: 1) the number of spectra in the
given interval that reach the maximum allowed hit count in each 
coarse bin, 2) the fraction of spectra in the given interval that
reach the maximum allowed hit count in each coarse bin, and 3) the
percent of maximum possible hits in each coarse bin over all spectra
in the interval.

dynspec_coarse: Produces a three panel dynamic spectrum plot. The main
panel is a pcolomesh figure of data, the bottom panel shows a time series
of the 2D data, and the right panel shows the average bandpass. 

dynspec_hits: Produces a 'confetti' scatter plot of hits over time.

freqbin_hist: Produces a histogram of hits as a function of frequency
bin.

meanpower_hist: Creates a histogram of hits as a function of meanpower
bin. Has the ability to plot hit count cumulatively as meanpower bin
increases.

power_freq: Plots the coarse spectrum and hits for a single specid on the
same set of axes.

ra_dec: Plots observing locations on either cartesian coordinates or a sky
map as a function of ra and dec.

driftrate: Can calculate and plot drift rates for a range of specids. 
