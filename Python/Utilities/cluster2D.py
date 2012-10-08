import numpy
from MySQLFunction import *

def cluster2d(speclo, spechi, ngap=0, mode='max'):
    '''A 2D clustering algorithm for S5 data.
    It defines clusters in time for each frequency channel.
    
    Input:
    speclo - specid for first spectrum
    spechi - specid for last spectrum
    ngap - Allow no gaps in time (0), allow 1 gap (1); default 0
    mode - Return max or mean eventpower in a cluster
        (\'max\' or \'mean\'); default=\'max\'

    Output:
    cl_start - specid of beginning of cluster
    freq_bin - freq bin number of cluster
    pwr_tmp - event power (max or mean) of cluster
    cl_len - number of samples in cluster
    '''

    cmd='select binnum,specid,eventpower from hit where specid>=%s and specid<=%s and rfi_found=0 and reserved=0;' % (speclo,spechi)

    #Get data from database and parse into numpy arrays
    data=numpy.array(mysqlcommand(cmd))
    bn,specid,eventpwr=data.transpose()

    #Calculate unique freq bins 
    fbins=numpy.unique(bn)[::-1]
    x=numpy.digitize(bn, fbins)

    #Calculate unique specids
    tbins=numpy.arange(speclo, spechi+1)
    #Assign each specid to a bin
    #Note: y>=1 since specid>=speclo
    y=numpy.digitize(specid, tbins)

    #Make zero arrays for hits and event pwrs
    #Make array 2 longer to pad edges with zeros
    hits=numpy.zeros((len(fbins),len(tbins)+2))
    hitpwr=numpy.zeros((len(fbins),len(tbins)+2))

    #Fill zero arrays with 1's or hit event power
    hits[x,y]=1.0
    hitpwr[x,y]=eventpwr

    #Calculate specid difference array
    diff=hits[:,1:]-hits[:,:-1]

    #Account for gaps if requested
    if ngap==1:
        gap_row,gap_col=numpy.where((diff[:,0:-1]==-1) & (diff[:,1:]==1))
        hits[gap_row,gap_col+1]=1
        diff=hits[:,1:]-hits[:,:-1]

    #Define cluster edges and length
    bin,left_edge=numpy.where(diff==1)
    bin,right_edge=numpy.where(diff==-1)
    cl_len=right_edge-left_edge
    left_edge=left_edge+1
    right_edge=right_edge+1

    #Reassign loc bin numbers to global bin numbers
    freq_bin=fbins[bin]

    #Calc cluster max/mean
    pwr_tmp=numpy.zeros(len(freq_bin))
    cl_start=tbins[left_edge-1]

    #Just assign event power if cluster length is 1
    inds=numpy.where(cl_len==1)[0]
    pwr_tmp[inds]=hitpwr[bin[inds],left_edge[inds]]

    #Otherwise loop
    inds=numpy.where(cl_len>1)[0]
    for cs in inds:
        if mode=='max':
            pwr_tmp[cs]=numpy.max(hitpwr[bin[cs], \
                left_edge[cs]:right_edge[cs]]) 

        else:
            tmp=hitpwr[bin[cs], left_edge[cs]:right_edge[cs]]
            pwr_tmp[cs]=numpy.mean(tmp[numpy.nonzero(tmp)])
    
    return cl_start, freq_bin, pwr_tmp, cl_len
