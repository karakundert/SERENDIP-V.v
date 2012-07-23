def mysqlcommand(cmd):
    """This sends a command to the database to be executed. cmd is the command to be executed. Modifier can be any logical operator. The output is the MySQL output."""
    
    import MySQLdb
    cmd = cmd
    #open database connection
    db = MySQLdb.connect  ("server_name","user_name","password","db_name")

    #prepare cursor object
    cursor = db.cursor()

    #execute SQL query
    cursor.execute(cmd)

    #fetch the data
    data = cursor.fetchall()

    #close the database and cursor
    db.close()
    cursor.close()
 
    return data
