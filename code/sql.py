# this script will connect to the serendipvv MySQL database on sting and 
# query the database for information. only works if the user has the 
# appropriate SSH tunnel established with sting.
#
# make sure that the environment variable PASS is set with the root password to
# sting before running the program

import MySQLdb
import numpy
import matplotlib.pyplot as plt
import sys
import os

env = os.getenv("PASS")
if env is not None:
    # open connection to serendipvv database on sting
    db = MySQLdb.connect(host='127.0.0.1',db='serendipvv',port=3306,passwd=env,user='root')
    print "connected to database"
else:
    print "please set environment variable PASS"
    sys.exit(1)

c = db.cursor()

# find and display MySQL version number
c.execute("SELECT VERSION()")
data = c.fetchone()
print "Database version: %s" % data

# set maximum value of variable for query
variables = "ra, decl"
table = "config"
limiter = "specid"
max_value = 100

# query the database for information
c.execute("""SELECT %s FROM %s WHERE %s < %s""" % (variables, table, limiter, max_value))

# fetch and print returned information
rows = c.fetchall()

RA = numpy.zeros(99)
DEC = numpy.zeros(99)
count = 0

for row in rows:
	x = float(row[0])
	y = float(row[1])

        print "%s, %s" % (row[0], row[1])

        RA[count] = x
        DEC[count] = y

        count += 1

print RA
print DEC

plt.scatter(RA, DEC)
plt.show()

# close database connection
db.close()

print "connection to database closed"
