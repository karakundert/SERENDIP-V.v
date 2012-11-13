#!/bin/env python

import sys
import numpy
import matplotlib.pyplot as py
import pulsarutil as plsr
import find_ET

nspec=400

def vertical_stack(npanels):

    tot_height=0.8
    tot_width=0.8
    xoff=(1.0-tot_width)/2
    yoff=(1.0-tot_height)/2
    dy=tot_height/npanels

    fig=py.figure()

    for ii in range(npanels):
        ax=fig.add_axes([xoff, dy*ii+yoff, tot_width, dy])
        if ii !=0:
            tc=ax.get_xticklabels()
            for tt in tc: tt.set_visible(False)

    return fig

def make_fake_beamlist(nspec):
    #Create beam number vector
    beamnum=numpy.repeat([0,1,2,3,4,5,6], 4)
    beamnum=numpy.tile(beamnum, nspec/28+1)
    beamnum=beamnum[0:nspec]

    return beamnum

def make_fake_s5data(nspec):
    nbins=2**27
    nhits_spec=128
    prate=8
    fstep=2.0e8/2**27
    flo=1.325e9

    #Define RFI and signal parameters
    rfibn1,rfipwr1=0.125*2**27,10
    rfibn2,rfipwr2=0.375*2**27,10
    rfibn3,rfipwr3=0.625*2**27,10
    sigbn,sigpwr=0.875*2**27,-7

    sid=numpy.array([])
    bn=numpy.array([])
    epwr=numpy.array([])

    beamnum=make_fake_beamlist(nspec)

    #Create poisson events
    tmp=numpy.zeros((nhits_spec,nspec))
    tmp=plsr.add_poissonevents3(tmp, prate)
    bloc,sloc=numpy.where(tmp!=0)

    #Expand the freq channels to a uniform distribution from 0 to nbins 
    unique_sid=numpy.unique(sloc)

    for s in unique_sid:
        inds=numpy.where(sloc==s)[0]

        sid=numpy.append(sid, s*numpy.ones(len(inds)))
        bn=numpy.append(bn, numpy.random.uniform(0,nbins,size=(len(inds),)))
        epwr=numpy.append(epwr, tmp[bloc[inds], sloc[inds]])

    #Add RFI and signal
    #Persistent RFI
    sid=numpy.append(sid, range(0,nspec))
    bn=numpy.append(bn, numpy.repeat(rfibn1, nspec))
    epwr=numpy.append(epwr, numpy.repeat(rfipwr1, nspec))

    #Sporatic RFI
    inds=numpy.where((beamnum==0) | (beamnum==1) | (beamnum==4))[0]
    sid=numpy.append(sid, inds[0:24])
    bn=numpy.append(bn, numpy.repeat(rfibn2, len(inds[0:24])))
    epwr=numpy.append(epwr, numpy.repeat(rfipwr2, len(inds[0:24])))

    #Multi pointing RFI
    inds=numpy.where((beamnum==2))[0]
    sid=numpy.append(sid, inds[0:12])
    sid=numpy.append(sid, inds[32:44])
    bn=numpy.append(bn, numpy.repeat(rfibn3, len(inds[0:12])))
    bn=numpy.append(bn, numpy.repeat(rfibn3, len(inds[32:44])))
    epwr=numpy.append(epwr, numpy.repeat(rfipwr3, len(inds[0:12])))
    epwr=numpy.append(epwr, numpy.repeat(rfipwr3, len(inds[32:44])))

    #Signal
    inds=numpy.where((beamnum==3))[0]
    sid=numpy.append(sid, inds[0:28])
    bn=numpy.append(bn, numpy.repeat(sigbn, len(inds[0:28])))
    epwr=numpy.append(epwr, numpy.repeat(sigpwr, len(inds[0:28])))

    #Calculate freq column
    tfreq=fstep*bn+flo
    hits=numpy.concatenate((sid[:,numpy.newaxis], bn[:,numpy.newaxis], \
        tfreq[:,numpy.newaxis], tfreq[:,numpy.newaxis], epwr[:,numpy.newaxis]), axis=1)

    #Delete gap
    inds=numpy.where((sid > (nspec/2-8)) & (sid < (nspec/2+8)))[0]
    hits=numpy.delete(hits, inds, axis=0)

    return hits.transpose(), beamnum

def confetti_plot(hits, beam):

    fig=py.figure()

    py.scatter(hits[0]*0.671, hits[2]/1e6, s=5, c=hits[4], edgecolors='None')

    py.xlim((0,0.671*nspec))
    py.ylim((1325, 1525))

    py.xlabel('Time (sec)')
    py.ylabel('Frequency (MHz)')

    return fig

def cluster_plot(clall, clgood, clclean):
    SI,BN,PWR,LEN=0,1,2,3
    CI,CSI,TF,EP,CW,CB=0,1,2,3,4,5

    fstep=200000000.0/2**27
    flo=1325e6

    #Make figure instance with three horizontal panels
    fig=vertical_stack(3)
    ax=fig.get_axes()

    #Add plot of all clusters with LEN>1
    gcl=numpy.where(clall[LEN] > 1)[0]
    ct=0.671*clall[SI,gcl]
    ctl=0.671*clall[LEN,gcl]/2
    ct+=ctl
    cf=clall[BN,gcl]*fstep + flo
    cf/=1e6

    ax[2].errorbar(ct, cf, xerr=ctl, fmt='|', color='k', ecolor='k', ls='None', \
        capsize=0.0, elinewidth=2)

    ax[2].set_xlim((0,0.671*nspec))
    ax[2].set_ylim((1325, 1525))

    #Add plots of clusters with allowable beam combinations
    gcl=numpy.where(clgood[CW] > 1)[0]
    ct=0.671*clgood[CSI,gcl]
    ctl=0.671*clgood[CW,gcl]/2
    ct+=ctl
    cf=clgood[TF,gcl]
    cf/=1e6

    ax[1].errorbar(ct, cf, xerr=ctl, fmt='|', color='k', ecolor='k', ls='None', \
        capsize=0.0, elinewidth=2)

    ax[1].set_xlim((0,0.671*nspec))
    ax[1].set_ylim((1325, 1525))
    ax[1].set_ylabel('Frequency (MHz)')

    #Add plots of cleaned clusters
    gcl=numpy.where(clclean[CW] > 1)[0]
    ct=0.671*clclean[CSI,gcl]
    ctl=0.671*clclean[CW,gcl]/2
    ct+=ctl
    cf=clclean[TF,gcl]
    cf/=1e6

    ax[0].errorbar(ct, cf, xerr=ctl, fmt='|', color='k',  ecolor='k', ls='None', \
        capsize=0.0, elinewidth=2)

    ax[0].set_xlim((0,0.671*nspec))
    ax[0].set_ylim((1325, 1525))
    ax[0].set_xlabel('Time (sec)')

    return fig

def main():
    SID,BN,PWR,LEN=0,1,2,3

    ngap=1
    hits,beams=make_fake_s5data(nspec)

    #Get all clusters for plotting
    cls,clf,clp,cll=find_ET.cluster2d(hits[SID], hits[BN], hits[PWR], \
        speclim=(0,nspec), ngap=ngap, type='bins')
    clall=numpy.concatenate((cls[numpy.newaxis,:], clf[numpy.newaxis,:], \
        clp[numpy.newaxis,:], cll[numpy.newaxis,:]), axis=0)

    #Get good clusters (i.e valid beams)
    clgood=find_ET.find_good_clusters(hits, beams, speclim=(0, nspec), ngap=ngap)

    #Define the cluster index
    ci=numpy.zeros((1,clgood.shape[1]))
    inds=numpy.where(clgood[SID] > nspec/2)[0]
    ci[:,inds]=1.0

    clgood=numpy.concatenate((ci, clgood), axis=0)

    #Define cleaned clusters
    clclean=find_ET.multiple_pointings(clgood, maxp=1)

    return clall, clgood, clclean
