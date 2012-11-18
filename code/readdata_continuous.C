#include "setiread.h"
#include "seti_doppler.h"

extern "C" {
#include "aocoord/azzaToRaDec.h"
#include "setimysql.h"
}


int main(int argc, char** argv)
{
    //reading data values 
    int fd;
    int ctr_numhits=0;
    int num_records=0;
    ssize_t numbytes;
    int compare = 1;
    off_t offset = 0;
    char error_buf[ERROR_BUF_SIZE];
    int headersize=DR_HEAER_SIZE;
    int next_buffer_size=1;
    int datasize=next_buffer_size;
    char *header = (char *) malloc(DR_HEAER_SIZE);
    char *data = (char *) malloc(MAX_DATA_SIZE);

    //plotting variables
    int maxbin = 0;
    int maxvalue = 0;
    int xmax = (int) BINS;

    //data values
    int finebin = 0 ;
    int bytesread = 1;
    int value;
    int pfb_bin = 0;
    int fft_bin = 0;
    int fft_bin_loc= 0;
    int over_thresh = 0;
    int blank = 0;
    int event = 0;
    unsigned int pfb_fft_power = 0;
    unsigned int fields;
    long int i = 0;
    int j = 0;
    int k = 0;
    int ctr = 0;
    int counter=0;
    int beamnum = 0;
    double fstep,fscoarse = 0.0;
    double rfmin,rfctr = 0.0;
    double freq_fft_bin = 0.0;
    double bary_freq = 0.0;
    char rawfile[] = "largefile_MMMDDYYYY_HHMM";
    int gooddata=1;
    int goodfreq=1;

    long int fileposition=0;   //position in input file
    long int filesize;   //position in input file

    //create buffers
    struct spectral_data spectra;

    struct data_vals *data_ptr;
    data_ptr = (struct data_vals *)data;

    //create header structure
    struct setidata frame;

    // create time structure
    tm hittime;
    double spec_time;

    // create SQL structures
    unsigned long int specid;
    //strcpy(def_password, argv[2]);
    char sqlquery[1024];
    char hitquery[1024];

    // file variables
    FILE *datatext;


    // connect to mySQL database
    dbconnect();

#ifdef GRACE
    // Initialize grace plotting windows
    grace_init();
//    grace_open_deux(8192);
//    grace_init_deux(maxbin,maxvalue,xmax);
#endif

    //check for error opening file
    fd = open(argv[1], O_RDONLY);

    if(fd==-1)
    {
        snprintf(error_buf, ERROR_BUF_SIZE, "Error opening file %s", argv[1]);
        perror(error_buf);
        return 0;
    }

    //if we can't find a header, nothing to be done
    if(find_first_header(fd)==-1) return 0;

    //read header
    //make sure we are reading as much data as expected, otherwise might be at eof
    while(headersize==DR_HEAER_SIZE && datasize==next_buffer_size)
    {
        k = k+1;
	//reset dataflag to "good"
	gooddata=1;

	// read in the header data
        headersize = read(fd, (void *) header, DR_HEAER_SIZE);
	fileposition+=headersize;

//        int iii=0;
//        for(iii=0; iii<DR_HEAER_SIZE; iii++)
//            printf("%c", header[iii]);

	//get the size of spectra and parse header values
        next_buffer_size = read_header(header);

        read_header_data(header, &frame);

	//Read in data
        datasize = read(fd, (void *) data, next_buffer_size);
	fileposition+=datasize;

//        printf("Buffersize, datasize: %d %d\n", next_buffer_size, datasize);
//	int iii=0;
//	printf("Printing data header\n");
//	for(iii=0; iii<datasize; iii++)
//		printf("%c", data[iii]);

	//Parse data header
        beamnum = read_beam(data, datasize);
        read_data_header(data, &frame);

	//Convert to RA and Dec
        scramAzZatoRaDec(frame.agc_systime, frame.agc_time, frame.agc_az, frame.agc_za, 
                frame.alfashm_alfamotorposition, beamnum/2, 0, &frame.ra, &frame.dec,  &hittime);

	get_filename(argv[1], rawfile);
	printf("%s\n", rawfile);

	//Calculate MJD
	spec_time = time2mjd(frame.agc_systime, frame.agc_time);

        // creates query to config table
        // set digital_lo and board to be constants, because we figured we knew
        // what they were and that they weren't changing
        char bid[] = "B2";
        sprintf(sqlquery, "INSERT INTO config (thrscale, thrlimit, fftshift, pfbshift, beamnum, obstime, ra, decl, digital_lo, board, AGC_SysTime, AGC_Time, AGC_Az, AGC_Za, AlfaFirstBias, AlfaSecondBias, AlfaMotorPosition, IF1_rfFreq, synI_freqHz, IF1_synI_ampDB, IF1_if1FrqMHz, IF1_alfaFb, TT_TurretEncoder, TT_TurretDegrees, rawfile) VALUES (%ld, %ld, %ld, %ld, %d, %lf, %lf, %lf, %ld, '%s', %ld, %ld, %lf, %lf, %ld, %ld, %lf, %9.1lf, %9.1lf, %ld, %lf, %ld, %ld, %lf, '%s')", 
                frame.thrscale, frame.thrlimit, frame.fft_shift, frame.pfb_shift,
                beamnum, (double) ((int) spec_time), frame.ra, frame.dec, 200000000, bid, frame.agc_systime, frame.agc_time, 
                frame.agc_az, frame.agc_za, frame.alfashm_alfafirstbias, frame.alfashm_alfasecondbias, 
                frame.alfashm_alfamotorposition, frame.if1_rffreq, frame.if1_syni_freqhz_0, frame.if1_syni_ampdb_0, 
                frame.if1_if1frqmhz, frame.if1_alfafb, frame.tt_turretencoder, frame.tt_turretdegrees, rawfile);

#ifndef DEBUG
        // insert header data into serendipvv config table
        if (mysql_query(conn, sqlquery)) {
            fprintf(stderr, "Error inserting data into sql database... \n");
            exiterr(3);
        }

        // saves specid to be inserted at index in other sql tables
        if ((res = mysql_store_result(conn))==0 && mysql_field_count(conn)==0 && mysql_insert_id(conn)!=0) {
            specid = (unsigned long int) mysql_insert_id(conn);
        }
#endif

#ifdef DEBUG
	printf("%s\n", sqlquery);
	printf("Spec id: %d\n", specid);
#endif
        //doesn't do any bounds checking yet...
        spectra.numhits = read_data(data, datasize) - 4096;

	//printf("size of spectra %d\n",spectra.numhits);
	//header,data
	data_ptr = (struct data_vals *) (data+SETI_HEADER_SIZE_IN_BYTES);

    //======================== TEST FILE DATA DUMP ================

    /*
        FILE *datafile;
        char dataf[100];
        sprintf(dataf,"datafiles/datafile%d.dat",counter);
        datafile = fopen(dataf,"wb");
        fwrite(data,spectra.numhits,1,(FILE *)datafile);
        fflush(datafile);
        fclose(datafile);  
    */

		
    //==============================================

        num_records = read_data(data,datasize);
	ctr_numhits=0;

        //create file spectraldata and print file header
/*        char filename[BUFSIZ];
        sprintf(filename, "spectraldata%d", beamnum);
        datatext = fopen(filename,"w");
        fprintf(datatext, "specnum,beamnum,coarsebin,coarsepower,hitpower,fftbin\n");
*/
        //Calc values for freq_topo calc
        //Freq chan resolution
        fstep = 200000000.0/134217728;
        fscoarse = 200000000.0/4096;
	//Center of the BEE2 bandpass
        rfctr = frame.if1_rffreq - 50000000.0;
	//Right edge of the last bin is the lowest freq
	//because the RF band is flipped in the IF
//	rfmin=rfctr-0.5*fscoarse;
        rfmin=rfctr+0.5*fscoarse;

	//Check to see if there are too many hits
	if(num_records>0.9*frame.thrlimit*4096) {
	    gooddata=0;
	    fprintf(stderr, "Data bad...more than %5.0lf hits.\n",  0.9*frame.thrlimit*4096);
	}
//============================
//         LOOP OVER HITS
//=============================
	for(i=0;i< num_records ;i++)
	{
	    goodfreq=1;
	    fields = ntohl(data_ptr->raw_data);
	    fft_bin = slice(fields,15,0);
	    pfb_bin = slice(fields,12,15);
	    over_thresh = slice(fields,1,27);
	    blank = slice(fields,3,28);
	    event = slice(fields,1,31);
	    
	    pfb_fft_power = ntohl(data_ptr->overflow_cntr); //32.0
//	    pfb_fft_power = data_ptr->overflow_cntr; //32.0

	    //Rearrange the bins
	    //1) Reorder the FFT output order
	    //2) Reverse bins due to RF/IF flip
            pfb_bin = (pfb_bin + 2048) % 4096;
//	    pfb_bin = 4096 - pfb_bin;
	    pfb_bin = 4095 - pfb_bin;
	    fft_bin = (fft_bin + 16384) % 32768;
//	    fft_bin = 32768 - fft_bin;
	    fft_bin = 32767 - fft_bin;
            fft_bin_loc = fft_bin;
            fft_bin+=pfb_bin*32768;

	    freq_fft_bin =  rfmin + fstep*fft_bin;

	    //Check that the freq of the hit falls within the valid ranges
	    if(frame.if1_alfafb==1){
	        if(freq_fft_bin < NBF_FREQ_LO || freq_fft_bin > NBF_FREQ_HI)  goodfreq=0;
	    }
	    else if(frame.if1_alfafb==0){
                if(freq_fft_bin < ALFA_FREQ_LO || freq_fft_bin > ALFA_FREQ_HI)  goodfreq=0;
	    }
           
            value = (int) (pfb_fft_power);
            //printf("%d %d %d %d %d %d\n", pfb_bin, fft_bin, pfb_fft_power, blank, event, over_thresh);

	    if(value < 1)
	    {
                value = 1;
	    }

	    if(value > maxvalue)
	    {
                maxvalue = value;
                maxbin = fft_bin;
	    }

	   //populate coarse bin power
	    if(fft_bin_loc==16383)
	    {
                spectra.coarse_spectra[pfb_bin] = value;
	    }

            //Only generate string and insert into database if hit valid
	    if(fft_bin_loc!=16383 && goodfreq==1 && gooddata==1)
	    {
//                spectra.hits[ctr_numhits][0] = value;  
//                spectra.hits[ctr_numhits][1] = fft_bin;  

		//Calculate the frequency of the fine bins and barycenter
		bary_freq=freq_fft_bin+seti_dop_FreqOffsetAtBaryCenter(freq_fft_bin, 
			spec_time+2400000.5, frame.ra, frame.dec, 2000.0, AO_LAT, AO_LONG, AO_ELEV);


                //Prepare mysql query to insert hits
                sprintf(hitquery, "INSERT INTO hit (eventpower, meanpower, binnum, topocentric_freq, barycentric_freq, specid) VALUES (%f, %e, %d, %lf, %lf, %ld)", (double) value, (double) spectra.coarse_spectra[pfb_bin], fft_bin, freq_fft_bin, bary_freq, specid);

#ifndef DEBUG
                // insert header data into serendipvv config table
                if (mysql_query(conn, hitquery)) {
                    fprintf(stderr, "Error inserting data into sql database... \n");
                    exiterr(3);
                }
#endif

            }
            // fill spectraldata with available data and close file
//            fprintf(datatext, "%d, %d, %d, %e, %f, %d\n", k, beamnum, pfb_bin, (double) spectra.coarse_spectra[pfb_bin], (double) value, fft_bin);
	
            ctr_numhits++;
	    data_ptr++;
	    ctr++;		
	}//for(i=0; i<num_records; i++)
//        fclose(datatext);
#ifndef DEBUG
       if(load_blob(conn, specid, spectra.coarse_spectra)!=0)
       {
               fprintf(stderr, "Blob not loaded\n");
               specid=0;
       }
#endif

//	GracePrintf("autoticks");
//	GracePrintf("redraw");
//	GracePrintf("updateall");
//	GracePrintf("kill g0.s0");
//	GracePrintf("saveall \"plots/sample%d.agr\"",counter);
//	grace_init_deux(maxbin,log10(maxvalue),xmax);	

	counter++;
        
        for(i=0;i<4094;i++) {
            spectra.coarse_spectra[i] = spectra.coarse_spectra[i+1];
        }

#ifdef GRACE	
    	plot_beam(&spectra,beamnum);
        printf("num_records: %d spectra.numhits %d\n",num_records,spectra.numhits);
        usleep(200000);
    
	if(counter%10 == 0) { 
            printf("autoscaling...\n");
            GracePrintf("redraw");
            GracePrintf("updateall");
            GracePrintf("autoscale");

            /*
            //output pdf via grace

            GracePrintf("HARDCOPY DEVICE \"EPS\"");
            printf("start eps create\n");
            GracePrintf("PAGE SIZE 600, 600");
            GracePrintf("saveall \"sample.agr\"");
            GracePrintf("PRINT TO \"%s\"", "plot.eps");
            GracePrintf("PRINT");
            */

	}
#endif
    }
//=====================================================
/*
    // play with some text 
    for(i=0; i<10; i++){
         GracePrintf("WITH STRING %d", i);
         GracePrintf("STRING COLOR 0");
         GracePrintf("STRING FONT 8");

         GracePrintf("STRING DEF \"TEST\"");
         GracePrintf("STRING ON");

         GracePrintf("STRING LOCTYPE view");
         GracePrintf("STRING 0.70, %f", 0.95 - (((float) i) / 40.0) );
    }

    GracePrintf("redraw");

    sleep(5);
*/
//===========================================================

#ifdef GRACE
     if (GraceIsOpen()) {
         //Flush the output buffer and close Grace 
         GraceClose();
         // We are done 
         exit(EXIT_SUCCESS);
     } else {
         exit(EXIT_FAILURE);
     }
#endif

    //close file
    close(fd);
    
    return 0;
}


