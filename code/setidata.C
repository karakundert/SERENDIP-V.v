struct setidata {
    long header_size;
    long data_size;
    char name[255];
    long dsi;
    long frameseq;
    long dataseq;
    long idlecount;
    long missed;
    long ast;
    char receiver[255];
    double samplerate;
    double ver;
    // SCRAM data goes here
    long agc_systime;
    double agc_az;
    long agc_time;
    long alfashm_systime;
    long alfashm_alfafirstbias;
    long alfashm_alfasecondbias;
    double alfashm_alfamotorposition;
    long if1_systime;
    double if1_syni_freqhz_0;
    long if1_syni_ampdb_0;
    double if1_rffreq;
    double if1_if1frqmhz;
    long if1_alfafb;
    long if2_systime;
    long if2_usealfa;
    long tt_systime;
    long tt_turretencoder;
    double tt_turretdegrees;
    long min_synth_freq;
    long max_synth_freq;
    long min_rec_freq;
    long max_rec_freq;
    long filtered_min_rec_freq;
    long filtered_max_rec_freq;
    // repeat of sample rate and receiver information excluded in this
    // structure
    long num_m_in_d;
    long num_diskbufs;
    char synth_model[255];
    double turret_degrees_alfa;
    long turret_degrees_tolerance;
}


