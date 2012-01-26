#include "setilib.h"

extern const int signal_type_cnt = 4;
const char * signal_name[signal_type_cnt] =  {"spike", "gaussian", "pulse", "triplet"};
extern const int mp_type_cnt = 2;
const char * mp_name[mp_type_cnt] =  {"bary", "nonbary"};

int signal_index_by_type(int sigtype) {
    switch (sigtype) {
        case 1 :
            return(0);
        case 2 :
            return(1);
        case 4 :
            return(2);
        case 8 :
            return(3);
        default :
            return(-1);
    }
}

int signal_type_by_index(int sigindex) {
// sigindex is an enum defined in the companion header file.
    switch (sigindex) {
        case 0 :
            return(spike_t);
        case 1 :
            return(gaussian_t);
        case 2 :
            return(pulse_t);
        case 3 :
            return(triplet_t);
        default :
            return(-1);
    }
}

const char * signal_name_by_type(int sigtype) {
    return(signal_name[signal_index_by_type(sigtype)]);
}

const char * signal_name_by_index(int sigindex) {
    return(signal_name[sigindex]);
}

int signal_to_type(spike s)     {return(spike_t);}
int signal_to_type(gaussian s)  {return(gaussian_t);}
int signal_to_type(pulse s)     {return(pulse_t);}
int signal_to_type(triplet s)   {return(triplet_t);}
int signal_to_type(star s)      {return(star_t);}

void common_signal_t::populate(spike signal) { 

    populate_common(signal);
    sigtype     = spike_t;
}

void common_signal_t::populate(gaussian signal) { 

    populate_common(signal);
    sigtype = gaussian_t;
}

void common_signal_t::populate(pulse signal) { 

    populate_common(signal);
    sigtype = pulse_t;
    period  = signal.period;
}

void common_signal_t::populate(triplet signal) { 

    populate_common(signal);
    sigtype = triplet_t;
    period  = signal.period;
}

template<typename T> void common_signal_t::populate_common(T signal) { 

    int retval;
    subband_description_t subband_description;
    double lo_freq;

    retval = signal.result_id->cached_fetch();
    if(!retval) {
        fprintf(stderr, "Cannot fetch result %ld for %s %ld : retval is %d\n", 
                signal.result_id.id, signal_name_by_type(sigtype), sigid, retval);
        exit(1);
    }
    retval = signal.result_id->wuid->cached_fetch();
    if(!retval) {
        fprintf(stderr, "Cannot fetch WU %ld for result %ld for %s %ld : retval is %d\n", 
                signal.result_id->wuid.id, signal.result_id.id, signal_name_by_type(sigtype), sigid, retval);
        exit(1);
    }
    subband_description = signal.result_id->wuid->subband_desc;
    lo_freq = subband_description.base                        -
              (((subband_description.number+128)%256)-128)    *
              subband_description.sample_rate;

    sigid               = signal.id;
    ra                  = signal.ra;
    decl                = signal.decl;
    time                = signal.time;
    freq                = signal.freq;
    peak_power          = signal.peak_power;
    mean_power          = signal.mean_power;
    detection_freq      = signal.detection_freq;
    barycentric_freq    = signal.barycentric_freq;
    fft_len             = signal.fft_len;
    chirp_rate          = signal.chirp_rate;
    rfi_checked         = signal.rfi_checked;
    rfi_found           = signal.rfi_found;
    baseband_freq       = detection_freq-lo_freq;
    subband_sample_rate = subband_description.sample_rate;
    //fprintf(stderr, "sbsr = %lf\n", subband_sample_rate);

}

//___________________________________________________________________________________
bool common_signal_t::update_db() {
//___________________________________________________________________________________

    bool retval;
    std::string sig_str;
    std::stringstream update_sstr;

    sig_str = signal_name_by_type(sigtype);
    update_sstr << "update " << sig_str
                << "  set rfi_checked = " << rfi_checked 
                << ", rfi_found = " << rfi_found 
                << " where id = " <<  sigid;
    //fprintf(stderr, "running : %s\n", update_sstr.str().c_str());
    retval = sql_run(update_sstr.str().c_str());
    return(retval);
}
