#include "setilib.h"

// * == not yet implemented
const long zone_rfi_mask         = 0x00000001;
const long staff_rfi_mask        = 0x00010000;
const long volunteer_rfi_mask    = 0x00020000;  // *
const long birdie_rfi_mask       = 0x02000000;  // *
const long badval_rfi_mask       = 0x04000000;  // *
const long redundantsig_rfi_mask = 0x08000000;  // *
const long ignorewu_rfi_mask     = 0x10000000;  // *
const long ignorewug_rfi_mask    = 0x20000000;  // *
const long ignoretape_rfi_mask   = 0x40000000;  // *
const long null_rfi_mask         = 0x80000000;  // for testing

const int num_algos = 3;
//                                                    run    mask               need spikes   function    name
const algorithm_t algorithm_table[num_algos] =  {    {true,  zone_rfi_mask,     false,        rfi_zone,   "zone"},
                                                     {false, staff_rfi_mask,    false,        rfi_staff,  "staff"},
                                                     {false, null_rfi_mask,     false,        rfi_null,   "null"}
                                                };

//___________________________________________________________________________________
int load_algorithm_vector(std::vector< algorithm_t> &algorithms) {
//___________________________________________________________________________________

    int i;
    for(i=0; i < num_algos; i++) {
        algorithms.push_back(algorithm_table[i]);
    }
}

//___________________________________________________________________________________
int update_spike_field(std::vector<spike> &spike_field, double time) {
//___________________________________________________________________________________
// The idea here is to have a vector of spikes in memory for use in rfi excision.
// We would order the signals being checked for rfi by time.  As the "next" signal
// calls for spikes to added to the field, older spikes could be freed.  Thus, a 
// forward moving waterfall is always in memory.  We won't need to redundantly read
// spikes.  
//
// This function is not needed is we are doing only zone RFI removal.

}

//___________________________________________________________________________________
bool is_rfi(common_signal_t &signal) {
//___________________________________________________________________________________

    bool rfi=false;
    static bool algorithms_loaded = false;
    static std::vector<algorithm_t> algorithms;
    int algo;
    std::vector<spike> spike_field;

    if(!algorithms_loaded) {
        load_algorithm_vector(algorithms);
        algorithms_loaded = true;
    }

     for(algo=0; algo<algorithms.size(); algo++) {
        // if alorithm is runnable and not already run on this signal
        if(algorithms[algo].run && !(signal.rfi_checked & algorithms[algo].mask)) {            
            fprintf(stderr, "running %s RFI algorithm on signal type %d ID %lld\n", 
                    algorithms[algo].name, signal.sigtype, signal.sigid);
            if(algorithms[algo].need_spike_field) {
                update_spike_field(spike_field, signal.time);
            }
            rfi = algorithms[algo].function(signal, spike_field); // determine if signal is rfi
            signal.rfi_checked |= algorithms[algo].mask;
            if(rfi) {
                //fprintf(stderr, "RFI FOUND\n");
                signal.rfi_found |= algorithms[algo].mask;
            }
        }
    }

    return(rfi);
}

