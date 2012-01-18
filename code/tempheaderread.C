int read_header_data(char * header, struct setidata * frame) {
    // grab all data available in the header and place in an array to be
    // cleaned up later.
    char buf[4096];
    char c;
    int i,j,k;
    file = fopen("FILENAME", "r");
    char fields[100][100];
    i=0;
    j=0;
    k=0;
    do {
        c = getchar(file);
        if (c != "\n") {
            buf[i++] = c;
        }
        else {
            strcpy(fields[j++], buf);
            i=0;
        }
        k++;
    } while (k < headersize);

    sscanf(fields[0], "HEADER_SIZE %d", & frame.header_size);

    printf("headersize %d, frame.header_size %d", headersize, frame.header_size);


/*
    int datasize;
    for (i=0;i<DR_HEAER_SIZE; ) {
        if (strncmp(header+i, DATA_SIZE_STRING, strlen(DATA_SIZE_STRING))==0) {
            sscanf(header+i, "DATASIZE %d\n", &datasize);
        }
        i+=strlen(header+i);
    }
    return datasize;
*/
}
