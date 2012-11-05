import numpy
from MySQLFunction import *
import fake_s5_data as fake_s5

SID,BN,TFREQ,BFREQ,PWR=0,1,2,3,4

def get_hits(speclo, spechi):
    '''
    Input:
    speclo - specid for first spectrum
    spechi - specid for last spectrum
    '''

    cmd='select specid,binnum,topocentric_freq,barycentric_freq,eventpower from hit where specid>=%s and specid<=%s and meanpower > 150 and rfi_found=0 and reserved=0;' % (speclo,spechi)

    #Get data from database and parse into numpy arrays
    data=numpy.array(mysqlcommand(cmd)).transpose()
    
    return data

def gen_beam_col(speclo, spechi):

    cmd='select beamnum from config where specid>=%d and specid<=%d' % (speclo,spechi)

    #Get beam numbers from the database
    #Assign a beam to each of the specids in the list of hits
    beams=numpy.array(mysqlcommand(cmd))
#    beams=beams[(sid_list-speclo).astype(int)]

    #Convert to physical beam
    beams=beams.astype(float)/2.0

    #Convert to quarter beam to track cycle phase
    if beams[1]-beams[0] == 0:  beams[1::2]+=0.25
    else:  beams[0::2]+=0.25

    return beams

def allowed2beams(blist):

    b2comb=numpy.array([[0,1], [0,2], [0,3], [0,4], [0,5], [0,6],\
                  [1,2], [2,3], [3,4], [4,5], [5,6], [1,6]])

    allowed=(b2comb==blist).all(axis=1).any()

    return allowed

def allowed3beams(blist):

    b3comb=numpy.array([[0,1,2], [0,2,3], [0,3,4], [0,4,5], [0,5,6], [0,1,6]])

    allowed=(b3comb==blist).all(axis=1).any()

    return allowed

def find_unique_beams(cls,cll,beams,speclo,dopol=False):
    long_sid=numpy.array([])

    for ii in range(len(cls)):
        long_sid=numpy.append(long_sid, numpy.arange(cls[ii], cls[ii]+cll[ii]))

    beam_list=beams[(long_sid-speclo).astype(int)]

    if not dopol: beam_list=beam_list.astype(int)

    return beam_list

def find_repeated_bin(fbin):
    ubin=numpy.unique(fbin)
    ubin=numpy.append(ubin, ubin[-1]+1)

    bhist,be=numpy.histogram(fbin, bins=ubin)

    tmp=numpy.where(bhist>1)[0]
    repeated=be[tmp]

    return repeated

def cluster2d(specid, bn_freq, eventpwr,  speclim=(0,0), ngap=0, mode='max', type='freq'):
    '''A 2D clustering algorithm for S5 data.
    It defines clusters in time for each frequency channel.
    
    Input:
    specid: numpy array of specids
    bn_freq: numpy array of freq bin numbers or frequencies
    
    ngap - Allow no gaps in time (0), allow 1 gap (1); default 0
    mode - Return max or mean eventpower in a cluster
        (\'max\' or \'mean\'); default=\'max\'

    Output:
    cl_start - specid of beginning of cluster
    freq_bin - freq bin number of cluster
    pwr_tmp - event power (max or mean) of cluster
    cl_len - number of samples in cluster
    '''

    #Calculate unique freq bins 
    if type=='bins':
        fbins=numpy.unique(bn_freq)[::-1]
    else:
        freq=numpy.round(bn_freq, decimals=1)
        fbins=numpy.unique(bn_freq)[::-1]

    x=numpy.digitize(bn_freq, fbins)

    #Calculate unique specids
    tbins=numpy.arange(speclim[0], speclim[1]+1)
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

    #Reassign loc bin numbers/freq to global bin numbers/freq
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

def reject_long_clusters(hits, speclim=(0,100), ngap=0):
    rfilen=13

    #Define topocentric clusters for RFI rejection
    cls,clb,clp,cll=cluster2d(hits[SID], hits[BN], hits[PWR], \
        speclim=speclim, ngap=ngap, type='bins')

    rficl=numpy.where(cll>=rfilen)[0]

    #Delete hits that are part of the long clusters
    for r in rficl:
        dinds=numpy.where((hits[BN]==clb[r]) & (hits[SID]>=cls[r]) & (hits[SID]<(cls[r]+cll[r])))[0]
        hits=numpy.delete(hits, dinds, axis=1)

    return hits

def find_good_clusters(hits, beams, speclim=(0,100), ngap=0):

    #Cluster on barycentric frequency
    cls,clb,clp,cll=cluster2d(hits[SID], hits[TFREQ], hits[PWR], \
        speclim=speclim, ngap=ngap, type='topo')

    #Find clusters longer than one event
    gcl=numpy.where(cll>1)[0]

    #Find freq bins with more than one cluster
    rb=find_repeated_bin(clb[gcl])

    #Loop through repeated bins
    clgood=numpy.array([])
    clgood.shape=(5,0)

    for b in rb:
        inds=numpy.where(clb[gcl]==b)[0]
        beamlist=find_unique_beams(cls[gcl[inds]], cll[gcl[inds]], beams, speclim[0])
        beamlist=numpy.unique(beamlist)  #Put inside find_unique_beams

        if len(beamlist)==1:
            allowed=True
        elif len(beamlist)==2:
            allowed=allowed2beams(beamlist)
        elif len(beamlist)==3:
            allowed=allowed3beams(beamlist)
        else:
            allowed=False

        if allowed:
            btmp=beams[cls[gcl[inds]]-speclim[0]]
            clgood=numpy.concatenate((clgood, [cls[gcl[inds]], clb[gcl[inds]], \
                clp[gcl[inds]], cll[gcl[inds]], btmp]), axis=1)

    return clgood

def multiple_pointings(cllist, maxp=2):
    CI,SI,TF,EP,CW,CB=0,1,2,3,4,5
    ndec=-3
    clclean=numpy.array([])
    clclean.shape=(cllist.shape[0],0)

    uf=numpy.unique(numpy.round(cllist[TF], decimals=ndec))

    for f in uf:
        tmp=numpy.where(numpy.round(cllist[TF], decimals=ndec)==f)[0]
        pointings=numpy.unique(cllist[CI,tmp])
        if len(pointings)<=maxp: clclean=numpy.concatenate((clclean, cllist[:,tmp]), axis=1)

    return clclean

def main(speclo, spechi, ngap=1):
    SID,BN,TFREQ,BFREQ,PWR=0,1,2,3,4

    #Get data from database
    hits=get_hits(speclo, spechi)

    #Get fake hits
#    hits=fake_s5.make_fake_s5data()

    #Get a list of beams vs specid
    beams=gen_beam_col(speclo, spechi) 
#    beams=fake_s5.make_fake_beamlist((spechi-speclo+1))

    #Reject long clusters
#    hits=reject_long_clusters(hits, speclim=(speclo, spechi), ngap=ngap)

    #Find good clusters
    clgood=find_good_clusters(hits, beams, speclim=(speclo, spechi), ngap=ngap)

    return clgood

if __name__=="__main__":
    speclo=int(sys.argv[1])
    spechi=int(sys.argv[2])
    ngap=1

    main(speclo, spechi, ngap)
