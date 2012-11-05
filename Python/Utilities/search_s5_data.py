#!/bin/env python

import sys
sys.path.append('/home/laura/SERENDIP-V.v/Python/Libraries')
sys.path.append('/home/laura/SERENDIP-V.v/Python/PlotFunctions')

from time import gmtime, asctime
import numpy
import findpointings
import dynspec_hits
import find_ET

def dump_data(cllist, sid_long):
    #Find clusters across pointings
    clclean=find_ET.multiple_pointings(cllist, maxp=2)

    fout=open('lists/cluster_good_%08d_%08d.txt' % \
        (sid_long[0], sid_long[-1]), 'w')
    for jj in range(cllist.shape[1]):
        fout.write('%d    %d    %f    %d    %d    %f\n' %
            (cllist[0,jj], cllist[1,jj], cllist[2,jj], cllist[3,jj], cllist[4,jj], cllist[5,jj]))
    fout.close()

    fout=open('lists/cluster_clean_%08d_%08d.txt' % \
        (sid_long[0], sid_long[-1]), 'w')
    for jj in range(clclean.shape[1]):
        fout.write('%d    %d    %f    %d    %d    %f\n' % (clclean[0,jj], clclean[1,jj],
            clclean[2,jj], clclean[3,jj], clclean[4,jj], clclean[5,jj]))
    fout.close()

                #Make plots
    figname='plots/dynspec_cluster_%08d_%08d.png' % \
        (sid_long[0], sid_long[-1])
    fig=dynspec_hits.clusterplot(clclean, cllist, sid_long, saveplot=figname)

    return

mingap=60
maxgap=30*60
sidlo_all,sidhi_all=500000,1000000
sid_interval=5000

sidlo_loc=sidlo_all
sidhi_loc=sidlo_all+sid_interval

obstime_now=0
sid_long=numpy.array([])
cllist=numpy.array([])
cllist.shape=(6,0)
pindex=0
obstimenow=5e9
while sidlo_loc < sidhi_all:
    #Find the edges of the telescope pointings
    sid_start,sid_end,rawfile,pnt_len,obstime,ra,dec=\
        findpointings.pointing(sidlo_loc, sidlo_loc+sid_interval)

    inds=numpy.where(sid_end < sidlo_loc+sid_interval)[0]

    #Loop over pointings and apply algorithm
    for ii in range(len(sid_start[inds])):
        #If the jump in time is too long, assume a new observing session
        if obstime[ii]-obstimenow > maxgap: 
            print "*****NEW OBSERVING SESSION*****"

            if len(sid_long) > 0:
                #Clean cluster list over multiple pointings
                #Write out files and make plots
                dump_data(cllist, sid_long)

                pindex=0
                cllist=numpy.array([])
                cllist.shape=(6,0)
                sid_long=numpy.array([])

        #Check that the pointing is long enough
        if pnt_len[ii]>mingap:
            #Print info for log
            print asctime(gmtime(obstime[ii]-4*3600)), rawfile[ii], ra[ii], dec[ii], \
                sid_start[ii], sid_end[ii], pnt_len[ii]

            #Make a list of valid start specids
            sid_long=numpy.append(sid_long, sid_start[ii])

            #Find valid clusters
            clgood=find_ET.main(sid_start[ii], sid_end[ii], 1)

            #Create a pointing index to keep track of pointings
            picol=numpy.repeat(pindex, clgood.shape[1])
            clgood=numpy.concatenate((picol[numpy.newaxis,:], clgood))

            #Add local cluster list to global list
            cllist=numpy.concatenate((cllist, clgood), axis=1)
            pindex+=1
        else:
            print asctime(gmtime(obstime[ii]-4*3600)), sid_start[ii], sid_end[ii], pnt_len[ii], "Too short"
        obstimenow=obstime[ii]

    if len(sid_start) == 0: sidlo_loc+=sid_interval
    else: sidlo_loc=sid_end[inds[-1]]+1

#If done with loop, dump what's left
if len(sid_long) > 0:
    dump_data(cllist, sid_long)
