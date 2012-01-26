void convertToRADec(struct setidata frame, int beamnum) {
//------------------------------------------------------------

    double coord_unixtime = seti_ao_timeMS2unixtime(frame->agc_time, frame->agc_systime);

    if(frame->agc_systime) {
        
        seti_time temp_time((time_t)0,coord_unixtime); 
        coord_time = temp_time; 

        double Za        = frame->agc_za;    // don't change the header since we want to keep it as read.
        double Az        = frame->agc_az;    // don't change the header since we want to keep it as read.
        double Rotation  = frame->alfashm_alfamotorposition;
        // include beam number without channel
        // how do I get around using a telescope_id variable? I've got an int
        // version of the beam number...
        telescope_id Tel = channel_to_receiverid[channel];

        co_ZenAzCorrection(Tel, &Za, &Az, Rotation);       
        //fprintf(stderr, "TIME %ld %ld %lf\n", scram_agc.Time, scram_agc.SysTime, seti_ao_timeMS2unixtime(scram_agc.Time, scram_agc.SysTime));
        seti_AzZaToRaDec(Az, Za, coord_unixtime, ra, dec);
    } 
    else {
        fprintf(stderr, "In populate_derived_values() : no scram_agc.SysTime!\n");
        exit(1);
    }
}
    

