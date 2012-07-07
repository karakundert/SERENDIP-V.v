INCS = -I/usr/local/grace/include -I/usr/include/mysql
LIBS = -lstdc++ -lgrace_np -L/usr/local/grace/lib -Laocoord -lazzatoradec -L/usr/lib64/mysql -lmysqlclient
FLAG = NOGRACE
DEBUG = ABC 

default: test_diskbuf.C
	gcc -lstdc++ -g -o test_diskbuf test_diskbuf.C

plotter: setiread.o setimysql.o readdata.o setidoppler.o readdata_continuous.o Makefile
	gcc -g -o readdata setiread.o readdata.o ${LIBS} ${INCS}
	gcc -g -o readdata_continuous setiread.o setimysql.o setidoppler.o readdata_continuous.o ${LIBS} ${INCS}
quick:
	gcc -g -o quick_analyzer quick_analyzer.C ${LIBS} ${INCS}

readdata.o: readdata.C Makefile
	gcc -c readdata.C -o readdata.o ${INCS}	

readdata_continuous.o: readdata_continuous.C Makefile
	gcc -c readdata_continuous.C -o readdata_continuous.o ${INCS} -D${FLAG} -D${DEBUG}

setiread.o: setiread.C Makefile 
	gcc -c setiread.C -o setiread.o ${INCS} ${LIBS}

setimysql.o: setimysql.c Makefile
	gcc -c setimysql.c -o setimysql.o ${INCS}

setidoppler.o: seti_doppler.cpp Makefile
	gcc -c seti_doppler.cpp -o setidoppler.o -lm  

clean:
	@rm -rf *.o	

