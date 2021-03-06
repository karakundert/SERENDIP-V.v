#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <string.h>
#include <unistd.h>
#include "setiread.h"

#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <assert.h>

extern "C" {
#include "aocoord/azzaToRaDec.h"
}

long read_data(char * data, int datasize)
{
    long record_count = ((long *) data)[0];
    long beam_no = ((long *) data)[1];

    fprintf(stderr, "record ct %ld beam no %ld\n", record_count, beam_no);
    //fprintf(stderr, &data[16]);

    return record_count;
}

int read_beam(char * data, int datasize)
{
    long beam_no = ((long *) data)[1];
   
    switch((int)beam_no) 
    {
	case 238:
	    beam_no = 0;
	    break;
	case 237:
	    beam_no = 0;
	    break;
	case 235:
	    beam_no = 1;
	    break;
	case 231:
	    beam_no = 2;
	    break;
	case 222:
	    beam_no = 3;
	    break;
	case 221:
	    beam_no = 4;
	    break;
	case 219:
	    beam_no = 5;
	    break;
	case 215:
	    beam_no = 6;
	    break;
	case 190:
	    beam_no = 7;
	    break;
	case 189:
	    beam_no = 8;
	    break;
	case 187:
	    beam_no = 9;
	    break;
	case 183:
	    beam_no = 10;
	    break;
	case 126:
	    beam_no = 11; 
	    break;
	case 125:
	    beam_no = 12;
	    break;
	case 123:
	    beam_no = 13; 
	    break;
	case 119:
	    beam_no = 14;
	    break;
    } 

    return beam_no;
}

//moves the fd to the beginning of the first header in the file
int find_first_header(int fd)
{
    int i;
    int header_not_found=1;
    int header_location=0;

    //we should be able to find the first header within DR_HEAER_SIZE+MAX_DATA_SIZE+strlen(HEADER_STRING)
    char *buffer = (char *) malloc(MAX_DATA_SIZE+DR_HEAER_SIZE+strlen(HEADER_STRING));
    
    read(fd, (void *) buffer, MAX_DATA_SIZE+DR_HEAER_SIZE+strlen(HEADER_STRING));
          
    for(i=0; header_not_found && i<DR_HEAER_SIZE+MAX_DATA_SIZE; i++)
    {
        header_not_found=strncmp(buffer+i, HEADER_STRING, strlen(HEADER_STRING));
        if(!header_not_found)
        {
            // need to match HEADER_SIZE also then are other instances where HEADER will occur in the header
            header_not_found = strncmp(buffer+i+strlen(HEADER_STRING)+1, HEADER_SIZE_STRING, strlen(HEADER_SIZE_STRING));
       //     fprintf(stderr, buffer+i);
        //    fprintf(stderr, buffer+i+strlen(HEADER_STRING)+1);
        }

        header_location=i;
    }

    if(header_not_found)
    {
        fprintf(stderr, "Error finding header in %s\n", FILENAME);
        return -1;
    }
    else
    {
        fprintf(stderr, "header found at %d\n", header_location);
        lseek(fd, header_location, SEEK_SET);
        return 0;
    }

}
/*
void read_data(char * data, int datasize)
{
    long record_count = ((long *) data)[0];
    long beam_no = ((long *) data)[1];
    
    //fprintf(stderr, "record ct %ld beam no %ld\n", record_count, beam_no);
    //fprintf(stderr, &data[16]);
}
*/
int read_header(char * header)
{
    //fprintf(stderr, header);
    int i;
    int datasize;
    for(i=0; i<DR_HEAER_SIZE; )
    {
        //fprintf(stderr, header+i);
        if(strncmp(header+i, DATA_SIZE_STRING, strlen(DATA_SIZE_STRING))==0)
        {
            sscanf(header+i, "DATA_SIZE %d\n", &datasize);
           // fprintf(stderr, "found data size %d at %d\n", datasize, i);
        }
        i+=strlen(header+i)+1;
    }
    return datasize;
}


int read_header_data(char * header, struct setidata * frame)
{
    // grab all data available in the header and place in an array to be
    // cleaned up later. 
    char buf[4096];
    char c;
    int i,j,k,l;
    char fields[100][4096];
    i=0;
    j=0;
    k=0;
    l=0;
    do {
        c = header[k];
        if (c!='\0') {
            buf[i++] = c;
        }
        else {
            if (i!=0) {
                buf[i] = c;
                strcpy(fields[j++], buf);
                i=0;
            }
        }
        k++;
    } while (strncmp(buf, "END_OF_HEADER", 13));

    assert(sscanf(fields[1], "HEADER_SIZE %ld", & frame->header_size));
    assert(sscanf(fields[2], "DATA_SIZE %ld", & frame->data_size));
    assert(sscanf(fields[3], "NAME %s", & frame->name));
    assert(sscanf(fields[4], "DSI %ld", & frame->dsi));
    assert(sscanf(fields[5], "FRAMESEQ %ld", & frame->frameseq));
    assert(sscanf(fields[6], "DATASEQ %ld", & frame->dataseq));
    assert(sscanf(fields[7], "IDLECOUNT %ld", & frame->idlecount));
    assert(sscanf(fields[8], "MISSED %ld", & frame->missed));
    assert(sscanf(fields[9], "AST %ld", & frame->ast));
    assert(sscanf(fields[12], "RECEIVER %s", & frame->receiver));
    assert(sscanf(fields[13], "SAMPLERATE %lf", & frame->samplerate));
    assert(sscanf(fields[14], "VER %lf", & frame->ver));
    assert(sscanf(fields[15], "SCRAM AGC AGC_SysTime %ld AGC_Az %lf AGC_Za %lf AGC_Time %ld", & frame->agc_systime, & frame->agc_az, & frame->agc_za, & frame->agc_time));
    assert(sscanf(fields[16], "SCRAM ALFASHM ALFASHM_SysTime %ld ALFASHM_AlfaFirstBias %ld ALFASHM_AlfaSecondBias %ld ALFASHM_AlfaMotorPosition %lf", & frame->alfashm_systime, & frame->alfashm_alfafirstbias, & frame->alfashm_alfasecondbias, & frame->alfashm_alfamotorposition));
    assert(sscanf(fields[17], "SCRAM IF1 IF1_SysTime %ld IF1_synI_freqHz_0 %lf IF1_synI_ampDB_0 %ld IF1_rfFreq %lf IF1_if1FrqMhz %lf IF1_alfaFb %ld", & frame->if1_systime, & frame->if1_syni_freqhz_0, & frame->if1_syni_ampdb_0, & frame->if1_rffreq, & frame->if1_if1frqmhz, & frame->if1_alfafb));
    assert(sscanf(fields[18], "SCRAM IF2 IF2_SysTime %ld IF2_useAlfa %ld", & frame->if2_systime, & frame->if2_usealfa));
    assert(sscanf(fields[19], "SCRAM TT TT_SysTime %ld TT_TurretEncoder %ld TT_TurretDegrees %lf", & frame->tt_systime, & frame->tt_turretencoder, & frame->tt_turretdegrees));
    assert(sscanf(fields[40], "min_synth_freq %ld", & frame->min_synth_freq));
    assert(sscanf(fields[41], "max_synth_freq %ld", & frame->max_synth_freq));
    assert(sscanf(fields[42], "min_rec_freq %ld", & frame->min_rec_freq));
    assert(sscanf(fields[43], "max_rec_freq %ld", & frame->max_rec_freq));
    assert(sscanf(fields[44], "filtered_min_rec_freq %ld", & frame->filtered_min_rec_freq));
    assert(sscanf(fields[45], "filtered_max_rec_freq %ld", & frame->filtered_max_rec_freq));
    assert(sscanf(fields[48], "num_m_in_d %ld", & frame->num_m_in_d));
    assert(sscanf(fields[50], "num_diskbufs %ld", & frame->num_diskbufs));
    assert(sscanf(fields[52], "synth_model %s", & frame->synth_model));
    assert(sscanf(fields[55], "turret_degrees_alfa %lf", & frame->turret_degrees_alfa));
    assert(sscanf(fields[56], "turret_degrees_tolerance %ld", & frame->turret_degrees_tolerance));
    // assert(sscanf(fields[57], "PFB SHIFT: %ld", & frame->pfb_shift));
    // assert(sscanf(fields[58], "FFT SHIFT: %ld", & frame->fft_shift));
    // assert(sscanf(fields[59], "THRESH LIMIT: %ld", & frame->thrlimit));
    // assert(sscanf(fields[60], "THRESH SCALE: %ld", & frame->thrscale));

    // TEMP: check that data retrieval is working by comparing equivalent variables
/*    printf("frame.agc_systime %ld\n", frame->agc_systime);
    printf("frame.agc_az %lf\n", frame->agc_az);
    printf("frame.agc_za %lf\n", frame->agc_za);
    printf("frame.receiver %s\n", frame->receiver);
    printf("frame.min_synth_freq %ld\n", frame->min_synth_freq);
    printf("frame.samplerate %lf\n", frame->samplerate);
*/
    return frame->header_size;
}


int read_data_header(char *data, struct setidata *frame)
{
    // read the parameters that are given at the start of the data
    char buf[2048];
    char c;
    int i,j,k,l;
    char fields[100][2048];
    int offset=0;
    //printf("### data header = {%s}\n", data);
    i=0;
    j=0;
    k=0;
    l=0;
    for (l=0; l<2048; l++) {
        c = data[k++];
        if (c != '\0') {
	    buf[i++] = c;
	    if (c == '\n') {
		buf[i] = '\0';
		strcpy(fields[j++], buf);
		i=0;
	    }
	}
    }
/*
    int iii=0;
    for(iii=0; iii<5; iii++)
	fprintf(stderr, "%s", fields[iii]);
*/
    //If the first field is a newline character, skip it
//    if(strcmp(fields[0], "\n") != 0)
    if(strstr(fields[0], "BEE2"))
	offset=0;
    else
	offset=1;


    /* looks like occasionally we didn't get any status details from the BEE */
    /* in this case, the dr2 pushed garbage into these bytes, so we'll ammend */
    /* the code below to throw a warning but load defaults if necessary      */
    //assert(strncmp(fields[0+offset], "BEE2_STATUS:", strlen("BEE2_STATUS:")));
    //assert(sscanf(fields[1+offset], "PFB SHIFT: %ld", & frame->pfb_shift));
    //assert(sscanf(fields[2+offset], "FFT SHIFT: %ld", & frame->fft_shift));
    //assert(sscanf(fields[3+offset], "THRESH LIMIT: %ld", & frame->thrlimit));
    //assert(sscanf(fields[4+offset], "THRESH SCALE: %ld", & frame->thrscale));
    /*
	BEE2 STATUS: Tue Aug 25 18:46:40 AST 2009
	PFB SHIFT: 268435455
	FFT SHIFT: 28398
	THRESH LIMIT: 25
	THRESH SCALE: 96
	TENGE PORT: 33001
	TENGE IP: 167772161
     */

    if(strncmp(fields[0+offset], "BEE2_STATUS:", strlen("BEE2_STATUS:"))) fprintf(stderr, "Couldn't read BEE2 header - loading defaults\n");
    if(sscanf(fields[1+offset], "PFB SHIFT: %ld", & frame->pfb_shift) == 0) frame->pfb_shift = 268435455; 
    if(sscanf(sscanf(fields[2+offset], "FFT SHIFT: %ld", & frame->fft_shift) == 0) frame->fftshift = 28398;
    if(sscanf(fields[3+offset], "THRESH LIMIT: %ld", & frame->thrlimit)) == 0) frame->thrlimit = 25;
    if(sscanf(fields[4+offset], "THRESH SCALE: %ld", & frame->thrscale) == 0) frame->thrscale = 96;



    // TEMP: check that data retrieval is working by comparing equivalent variables
/*    printf("frame.pfb_shift %ld\n", frame->pfb_shift);
    printf("frame.fft_shift %ld\n", frame->fft_shift);
    printf("frame.thrlimit %ld\n", frame->thrlimit);
    printf("frame.thrscale %d\n", frame->thrscale);
*/
    return frame->header_size;
}

double time2mjd(time_t tobs, long tuobs)
{
	/*tobs = "AGC_SysTime" Unix time (i.e. sec from 1.1.1970)
          tuobs = "AGC_Time" msec from local midnight */

	int year,month,day;
        double tmjd,day_frac;
	struct tm *ao_tm;

	ao_tm=gmtime(&tobs);
	year=ao_tm->tm_year+1900;
	month=ao_tm->tm_mon+1;
	day=ao_tm->tm_mday;
	day_frac=((double) ao_tm->tm_hour)/24.0 + ((double) ao_tm->tm_min)/(24*60.0) + ((double) ao_tm->tm_sec)/(24*3600.0);
        tmjd=(double) gregToMjd(day,month,year);

        tmjd+=day_frac;

        return tmjd;
}

/*Extracts the name of the file from a full path string*/
void get_filename(char * instr, char * rawfile)
{
	char *loc;

	loc=strstr(instr, "largefile");

	rawfile=strncpy(rawfile, loc, 24);
}

/* Initialize GRACE plotting window */
int grace_init()
{

	float viewx[9]; //GRACE graph x coordinates
	float viewy[9]; //GRACE graph y coordinates

	int i=0,j=0,k=0,x=0; //Counters


	/* Assign Viewgraph locations (3 x 3, with 2 shrunk down for the legend) */

    viewx[8] = 0.06;
    viewy[8] = 0.04;

    viewx[7] = 0.39;
    viewy[7] = 0.04;

    viewx[6] = 0.72;
    viewy[6] = 0.04;

    viewx[5] = 0.39;
    viewy[5] = 0.04;

    viewx[4] = 0.06;
    viewy[4] = 0.04;

    viewx[3] = 0.72;
    viewy[3] = 0.36;

    viewx[2] = 0.39;
    viewy[2] = 0.36;

    viewx[1] = 0.06;
    viewy[1] = 0.36;

    viewx[0] = 0.06;
    viewy[0] = 0.68;


	/* Register GRACE Error Function */
    GraceRegisterErrorFunction(my_error_function);

    /* Start Grace with a buffer size of 16k and open the pipe */
    if (GraceOpen(16768) == -1) {
        fprintf(stderr, "Can't run Grace. \n");
        exit(EXIT_FAILURE);
    }
    
    GracePrintf("DEVICE \"X11\" PAGE SIZE 1000, 1000");

    GracePrintf("arrange(3, 3, 0.1, 0.15, 0.5)");

    GracePrintf("with g8"); 
    GracePrintf("BACKGROUND COLOR 1");	

    GracePrintf("Legend ON");
    GracePrintf("Legend loctype view");
    GracePrintf("Legend 0.39, .88");
    GracePrintf("LEGEND COLOR 0"); 	
    GracePrintf("LEGEND BOX COLOR 0"); 
    GracePrintf("LEGEND BOX FILL COLOR 1"); 

    GracePrintf("with g8");
    GracePrintf("view ymax 0.002");
    GracePrintf("view ymin 0.001");
    GracePrintf("view xmax 0.002");
    GracePrintf("view xmin 0.001");
    GracePrintf("xaxis tick off");
    GracePrintf("yaxis tick off");    

    GracePrintf("with g7"); 
    GracePrintf("view ymax 0.002");
    GracePrintf("view ymin 0.001");
    GracePrintf("view xmax 0.002");
    GracePrintf("view xmin 0.001");
    GracePrintf("xaxis tick off");
    GracePrintf("yaxis tick off");    
	
	
	for(j=0;j<7;j++){
	   GracePrintf("with g%d", j);
	   		   	 	
	    GracePrintf("BACKGROUND COLOR 1");	

 	   GracePrintf("xaxis tick minor grid on");
 	   GracePrintf("yaxis tick minor grid on");
 	   GracePrintf("xaxis tick major grid on");
 	   GracePrintf("yaxis tick major grid on");

 	   GracePrintf("yaxis tick major color 0");
 	   GracePrintf("xaxis tick major color 0");
 	   GracePrintf("yaxis tick minor color 0");
 	   GracePrintf("xaxis tick minor color 0");

 	   GracePrintf("yaxis tick major linewidth 0");
 	   GracePrintf("xaxis tick major linewidth 1");
 	   GracePrintf("yaxis tick minor linewidth 0");
 	   GracePrintf("xaxis tick minor linewidth 0");

 	   GracePrintf("yaxis tick major linestyle 2");
 	   GracePrintf("xaxis tick major linestyle 2");
 	   GracePrintf("yaxis tick minor linestyle 2");
 	   GracePrintf("xaxis tick minor linestyle 2");

 	   GracePrintf("yaxis tick color 0");
 	   GracePrintf("xaxis tick color 0");

 	   GracePrintf("yaxis tick default 5");
 	   GracePrintf("xaxis tick default 5");


 	   GracePrintf("yaxis bar on");
 	   GracePrintf("xaxis bar on");

 	   GracePrintf("yaxis bar color 0");
 	   GracePrintf("xaxis bar color 0");

 	   GracePrintf("yaxis label color 0");
 	   GracePrintf("xaxis label color 0");

 	   GracePrintf("yaxis bar linewidth 2");
 	   GracePrintf("xaxis bar linewidth 2");

 	   GracePrintf("yaxis ticklabel color 0");
 	   GracePrintf("xaxis ticklabel color 0");

 	   GracePrintf("yaxis ticklabel format power");
 	   GracePrintf("xaxis ticklabel format decimal");



		GracePrintf("view ymin %f", viewy[j]);
    	GracePrintf("view xmin %f", viewx[j]);
		GracePrintf("view xmax %f", viewx[j] + .25);
	   	GracePrintf("view ymax %f", viewy[j] + .23);

	    GracePrintf("xaxis tick major 50");
	    GracePrintf("yaxis tick major 100");

	   GracePrintf("yaxis tick minor off");
 	   GracePrintf("xaxis tick minor off");

 	   GracePrintf("xaxis tick minor size .20");
 	   GracePrintf("yaxis tick minor size .20");
 	   GracePrintf("xaxis tick major size .40");
 	   GracePrintf("yaxis tick major size .40");
 	   
 	   GracePrintf("xaxis ticklabel char size 0.55");
 	   GracePrintf("yaxis ticklabel char size 0.55");

 	   GracePrintf("xaxis ticklabel skip 2");
 	   GracePrintf("yaxis ticklabel skip 2");
 
 	   GracePrintf("xaxis ticklabel append \" MHz\"");

 	   GracePrintf("yaxis ticklabel prec 2");
 
	   GracePrintf("SUBTITLE FONT 10");
	   GracePrintf("SUBTITLE SIZE .70");
   	   GracePrintf("SUBTITLE \"ALFA BEAM %d\"", j);    
   	   GracePrintf("SUBTITLE COLOR 0");    


	   GracePrintf("world xmax 300");
	   GracePrintf("world xmin 100");
	   GracePrintf("world ymax 600");
	   GracePrintf("world ymin 1");	
	   GracePrintf("yaxes scale Logarithmic");

	  GracePrintf("s0 color 3");
	  GracePrintf("s1 color 14");
	  GracePrintf("s2 color 3");
	  GracePrintf("s2 symbol 4");
	  GracePrintf("s2 symbol size 0.28");
	  GracePrintf("s2 symbol fill pattern 1");
	  GracePrintf("s2 linestyle 0");
	  GracePrintf("s2 symbol color 3");
	  GracePrintf("s2 symbol linewidth 0");

	  GracePrintf("s3 color 14");
	  GracePrintf("s3 symbol 4");
	  GracePrintf("s3 symbol size 0.28");
	  GracePrintf("s3 symbol fill pattern 1");
	  GracePrintf("s3 linestyle 0");
	  GracePrintf("s3 symbol color 14");
	  GracePrintf("s3 symbol linewidth 0");


	}
	
	    /* set up legend */
         GracePrintf("g8.s0 color 3");
         GracePrintf("g8.s0 legend \"X Linear\"");

         GracePrintf("g8.s1 color 14");
         GracePrintf("g8.s1 legend \"Y Linear\"");
       
      
         for (i = 0; i < 1024 && GraceIsOpen(); i++) {
             GracePrintf("g8.s0 point %d, %d", i, i);
         
         }

         for (i = 0; i < 1024 && GraceIsOpen(); i++) {
             GracePrintf("g8.s1 point %d, %d", i, i);
         
         }


         GracePrintf("redraw");

		//GracePrintf("FRAME BACKGROUND COLOR 5");	
		
}


void my_error_function(const char *msg)
{
    fprintf(stderr, "library message: \"%s\"\n", msg);
}

unsigned int slice(unsigned int value,unsigned int width,unsigned int offset)
{
    value = value << (32 - (width + offset));
    value = value >> (32 - width);
    return value;
}

//int plot_beam(spectral_data * spectra, int beam_number);
int plot_beam(spectral_data * spectra, int beam_number)
{
    double bin_freq = (200.0 / 134217728.0); // bin to freq conversion factor
    double start_freq = 100.00 - (200.00 / 8192);  //100 MHz - half a bin;
    int i=0;

    GracePrintf("kill g%d.s%d",(int) ( (double) beam_number / 2), beam_number % 2);
    GracePrintf("kill g%d.s%d", (int) ( (double) beam_number / 2), ((beam_number % 2) + 2));

    GracePrintf("with g%d",(int) ( (double) beam_number / 2));
    GracePrintf("s0 color 3");
    GracePrintf("s1 color 14");
    GracePrintf("s2 color 3");
    GracePrintf("s2 symbol 4");
    GracePrintf("s2 symbol size 0.28");
    GracePrintf("s2 symbol fill pattern 1");
    GracePrintf("s2 linestyle 0");
    GracePrintf("s2 symbol color 3");
    GracePrintf("s2 symbol linewidth 0");
    GracePrintf("s3 color 14");
    GracePrintf("s3 symbol 4");
    GracePrintf("s3 symbol size 0.28");
    GracePrintf("s3 symbol fill pattern 1");
    GracePrintf("s3 linestyle 0");
    GracePrintf("s3 symbol color 14");
    GracePrintf("s3 symbol linewidth 0");

    /* plot coarse bins */
    for(i=0;i<4096;i++)
    {   
	//GracePrintf("AUTOSCALE");

	GracePrintf("g%d.s%d point %f, %d", (int) ( (double) beam_number / 2), beam_number % 2, start_freq + ((i*32768) * bin_freq), (*spectra).coarse_spectra[i]);
	GracePrintf("g%d.s%d point %f, %d", (int) ( (double) beam_number / 2), beam_number % 2, start_freq + (((i*32768) + 32767) * bin_freq), (*spectra).coarse_spectra[i]);		
    }

    /* plot hits */
    for(i=0;i<(*spectra).numhits;i++)
    {   
    	//GracePrintf("AUTOSCALE");
	   	GracePrintf("g%d.s%d point %f, %f", (int) ( (double) beam_number / 2), ((beam_number % 2) + 2), start_freq + ((double) (*spectra).hits[i][1] * bin_freq), (double)((*spectra).hits[i][0]));
	   	//if(i==0) printf("g%d.s%d point %f, %f", (int) ( (double) beam_number / 2), ((beam_number % 2) + 2), start_freq + ((double) (*spectra).hits[i][1] * bin_freq), (double)((*spectra).hits[i][0]));
    }
	
}

void grace_open_deux(int bufsize)
{
    GraceRegisterErrorFunction(my_error_function);

    if(GraceOpenVA("xmgrace", bufsize, "-free","-nosafe", "-noask", NULL))
    {
        fprintf(stderr, "Can't run Grace. \n");
        exit(EXIT_FAILURE);
    }

}

void grace_init_deux(int maxbin,float maxvalue,int xmax)
{

//fonts
    GracePrintf("map font 0 to \"Times-Roman\", \"Times-Roman\"");
    GracePrintf("map font 1 to \"Times-Italic\", \"Times-Italic\"");
    GracePrintf("map font 2 to \"Times-Bold\", \"Times-Bold\"");
    GracePrintf("map font 3 to \"Times-BoldItalic\", \"Times-BoldItalic\"");
    GracePrintf("map font 4 to \"Helvetica\", \"Helvetica\"");
    GracePrintf("map font 5 to \"Helvetica-Oblique\", \"Helvetica-Oblique\"");
    GracePrintf("map font 6 to \"Helvetica-Bold\", \"Helvetica-Bold\"");
    GracePrintf("map font 7 to \"Helvetica-BoldOblique\", \"Helvetica-BoldOblique\"");
    GracePrintf("map font 8 to \"Courier\", \"Courier\"");
    GracePrintf("map font 9 to \"Courier-Oblique\", \"Courier-Oblique\"");
    GracePrintf("map font 10 to \"Courier-Bold\", \"Courier-Bold\"");
    GracePrintf("map font 11 to \"Courier-BoldOblique\", \"Courier-BoldOblique\"");
    GracePrintf("map font 12 to \"Symbol\", \"Symbol\"");
    GracePrintf("map font 13 to \"ZapfDingbats\", \"ZapfDingbats\"");

//colors

    GracePrintf("map color 0 to (255,255,255),\"white\" ");
    GracePrintf("map color 1 to (0,0,0),\"black\" ");
    GracePrintf("map color 2 to (255,0,0),\"red\" ");
    GracePrintf("map color 3 to (0, 255, 0), \"green\"");
    GracePrintf("map color 4 to (0, 0, 255), \"blue\"");
    GracePrintf("map color 5 to (255, 255, 0), \"yellow\"");
    GracePrintf("map color 6 to (188, 143, 143), \"brown\"");
    GracePrintf("map color 7 to (220, 220, 220), \"grey\"");
    GracePrintf("map color 8 to (148, 0, 211), \"violet\"");
    GracePrintf("map color 9 to (0, 255, 255), \"cyan\"");
    GracePrintf("map color 10 to (255, 0, 255), \"magenta\"");
    GracePrintf("map color 11 to (255, 165, 0), \"orange\"");
    GracePrintf("map color 12 to (114, 33, 188), \"indigo\"");
    GracePrintf("map color 13 to (103, 7, 72), \"maroon\"");
    GracePrintf("map color 14 to (64, 224, 208), \"turquoise\"");
    GracePrintf("map color 15 to (0, 139, 0), \"green4\"");

//defaults

    GracePrintf("default linewidth 1.0");
    GracePrintf("default linestyle 1");
    GracePrintf("default color 1");
    GracePrintf("default pattern 1");
    GracePrintf("default font 8");
    GracePrintf("default char size 1.000000");
    GracePrintf("default symbol size 1.000000");
    GracePrintf("default sformat \"%16.8g\"");

//background color

    GracePrintf("background color %d",7);

//g0

    GracePrintf("g0 on");
    GracePrintf("g0 hidden false");
    GracePrintf("g0 type XY");
    GracePrintf("g0 stacked false");
    GracePrintf("g0 bar hgap 0.000000");
    GracePrintf("g0 fixedpoint off");
    GracePrintf("g0 fixedpoint type 0");
    GracePrintf("g0 fixedpoint xy 0.000000, 0.000000");
    GracePrintf("g0 fixedpoint format general general");
    GracePrintf("g0 fixedpoint prec 6, 6");
    GracePrintf("with g0");

//g0 xaxis

    GracePrintf("world xmax %d",xmax);
    GracePrintf("world xmin %d",0);
    GracePrintf("world ymax %d",1000000000);
    GracePrintf("world ymin %d",1);
    GracePrintf("stack world 0, 0, 0, 0 tick 0, 0, 0, 0");
    GracePrintf("yaxes scale Logarithmic");
    GracePrintf("xaxis tick major 32000");
    GracePrintf("xaxis tick minor 100");

//g0 xaxis label 

    GracePrintf("xaxis label \"bins\"");
    GracePrintf("xaxis label font \"Courier\"");
    GracePrintf("xaxis label char size .7");
    GracePrintf("xaxis ticklabel font \"Courier\"");
    GracePrintf("xaxis ticklabel char size .7");
    GracePrintf("xaxis label color %d",1);

//g0 yaxis label

    GracePrintf("yaxis label \"amplitude\"");
    GracePrintf("yaxis label font \"Courier\""); 
    GracePrintf("yaxis label char size .7");
    GracePrintf("yaxis ticklabel font \"Courier\"");
    GracePrintf("yaxis ticklabel char size .7");
    GracePrintf("yaxis ticklabel format power");
    GracePrintf("yaxis tick minor ticks 5");
    GracePrintf("yaxis ticklabel prec 0");
    GracePrintf("yaxis label color %d",1);

//g0 title properties
    
    GracePrintf("title \"Seti Spectrometer\"");
    GracePrintf("title color %d",1);
    GracePrintf("title font \"Courier\"");
    GracePrintf("title size .9");
    GracePrintf("subtitle \"max value %f in bin %d \"",maxvalue,maxbin);
    GracePrintf("subtitle color %d",1);
    GracePrintf("subtitle font 8");
    GracePrintf("subtitle size .8");

//create set s0 and properties for graph g0

    GracePrintf("s0 on");
    GracePrintf("s0 hidden false");
    GracePrintf("s0 type xy");
    GracePrintf("s0 symbol 2");
    GracePrintf("s0 symbol color 1");
    GracePrintf("s0 symbol size .3");
    GracePrintf("s0 symbol char 65");
    GracePrintf("s0 symbol fill pattern 0");
    GracePrintf("s0 symbol fill color 0");
    GracePrintf("s0 line linestyle 0");
    GracePrintf("s0 line color 1");
    GracePrintf("s0 fill type 0");
    GracePrintf("s0 fill rule 5");
    GracePrintf("s0 fill color 0");
    GracePrintf("s0 fill pattern 1");
  
//create set s1 and properties for graph g0

    GracePrintf("s1 on");
    GracePrintf("s1 hidden false");
    GracePrintf("s1 type xy");
    GracePrintf("s1 symbol 2");
    GracePrintf("s1 symbol color 0");
    GracePrintf("s1 symbol size .3");
    GracePrintf("s1 symbol char 65");
    GracePrintf("s1 symbol fill pattern 0");
    GracePrintf("s1 symbol fill color 9");
    GracePrintf("s1 line linestyle 0");
    GracePrintf("s1 line color 1");
    GracePrintf("s1 fill type 0");
    GracePrintf("s1 fill rule 5");
    GracePrintf("s1 fill color 0");
    GracePrintf("s1 fill pattern 1");

//create set s2 and properties for graph g0

    GracePrintf("s2 on");
    GracePrintf("s2 hidden false");
    GracePrintf("s2 type xy");
    GracePrintf("s2 symbol 2");
    GracePrintf("s2 symbol color 14");
    GracePrintf("s2 symbol size .3");
    GracePrintf("s2 symbol char 65");
    GracePrintf("s2 symbol fill pattern 0");
    GracePrintf("s2 symbol fill color 9");
    GracePrintf("s2 line linestyle 0");
    GracePrintf("s2 line color 1");
    GracePrintf("s2 fill type 0");
    GracePrintf("s2 fill rule 5");
    GracePrintf("s2 fill color 0");
    GracePrintf("s2 fill pattern 1");

}


