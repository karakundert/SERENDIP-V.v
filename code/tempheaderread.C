int read_header_data(char * header, struct * frame) {
    int i;
    int datasize;
    for (i=0;i<DR_HEAER_SIZE; ) {
        if (strncmp(header+i, DATA_SIZE_STRING, strlen(DATA_SIZE_STRING))==0) {
            sscanf(header+i, "DATASIZE %d\n", &datasize);
        }
        i+=strlen(header+i);
    }
    return datasize;
}
