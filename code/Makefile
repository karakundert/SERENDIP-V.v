INCS = -I/usr/local/grace/include -I/usr/include/mysql
LIBS = -lstdc++ -lgrace_np -L/usr/local/grace/lib -Laocoord -lazzatoradec -L/usr/lib64/mysql -lmysqlclient


default: test_diskbuf.C
	gcc -lstdc++ -g -o test_diskbuf test_diskbuf.C

plotter: setiread.o setimysql.o readdata.o readdata_continuous.o Makefile
	gcc -g -o readdata setiread.o readdata.o ${LIBS} ${INCS}
	gcc -g -o readdata_continuous setiread.o setimysql.o readdata_continuous.o ${LIBS} ${INCS}
quick:
	gcc -g -o quick_analyzer quick_analyzer.C ${LIBS} ${INCS}

readdata.o: readdata.C Makefile
	gcc -c readdata.C -o readdata.o ${INCS}	

readdata_continuous.o: readdata_continuous.C Makefile
	gcc -c readdata_continuous.C -o readdata_continuous.o ${INCS}

setiread.o: setiread.C Makefile 
	gcc -c setiread.C -o setiread.o ${INCS}
    
clean:
	@rm -rf *.o	

