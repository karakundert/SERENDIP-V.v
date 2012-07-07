#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <math.h>
#include <grace_np.h>
#define NUM 100000000
#define U32 unsigned int 
#define BINS 134217728.0

#define FILENAME "largefile0"
#define BUFFER_SIZE 1024
#define HEADER_STRING "HEADER\n"
#define HEADER_SIZE_STRING "HEADER_SIZE "
#define DATA_SIZE_STRING "DATA_SIZE "
#define DR_HEAER_SIZE 1024*4
#define MAX_DATA_SIZE 10240*1024
#define HEADER_SIZE 8
#define ERROR_BUF_SIZE 1024
#define SETI_HEADER_SIZE_IN_BYTES 512+8+8
#define ALFA_FREQ_LO 1225000000 
#define ALFA_FREQ_HI 1525000000
#define NBF_FREQ_LO 1390000000
#define NBF_FREQ_HI 1490000000

#ifndef EXIT_SUCCESS
#  define EXIT_SUCCESS 0
#endif

#ifndef EXIT_FAILURE
#  define EXIT_FAILURE -1
#endif

#define         AO_LONG 66.7531
#define         AO_LAT 18.3435
#define         AO_ELEV 497.0

/* structure for spectral data */
struct spectral_data{
        int coarse_spectra[4096];
        int hits[409600][2];
        int numhits;
};

struct data_vals{
    unsigned int raw_data;
    unsigned int overflow_cntr;
};


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
    long agc_systime;
    double agc_az;
    double agc_za;
    double ra;
    double dec;
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
    long pfb_shift;
    long fft_shift;
    long thrlimit;
    long thrscale;
};



void my_error_function(const char *msg);
unsigned int slice(unsigned int value,unsigned int width,unsigned int offset);

int grace_init();

/* this function plots the data in spectra on the graph specified by beam_number */
int plot_beam(spectral_data * spectra, int beam_number);

int find_first_header(int fd);
int read_header(char * header);
long read_data(char * data, int datasize);
int read_beam(char * data, int datasize);
int read_header_data(char * header, struct setidata * frame);
int read_data_header(char * data, struct setidata * frame);
double time2mjd(time_t tobs, long tuobs);
void get_filename(char * instr, char * rawfile);

void grace_open_deux(int bufsize);
void grace_init_deux(int maxbin,float maxvalue,int xmax);

