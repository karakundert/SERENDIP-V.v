def hist(freq_type='topo',increment_log=1,where=''):
    """A function to create a histogram command for MySQL. 

    freq_type is the frequency to be binned, either 'topo' or
    'bary' or 'binnum'.

    x is the log of the binning increment. 

    where is a string that allows you to further narrow the 
    results. do not include the word 'where' or the semicolon at 
    the end. all column names MUST be prefixed with the first 
    letter of the table name and a period, like c.obstime or 
    h.eventpower. include h.specid=c.specid if referencing both 
    config and hit tables. all other common syntax rules apply.

    Output is a string that contains the command to be sent to 
    the MySQL database."""
    
    # create full column name from freq_type
    if freq_type=='topo':
      freq_type = 'h.topocentric_freq'
    elif freq_type=='bary':
      freq_type = 'h.barycentric_freq'
    elif freq_type=='binnum':
      freq_type = 'h.binnum' 

    # change increment_log to a negative number
    increment_log = -1*increment_log

    # if statement to determine proper output
    if not where: 
      cmd = "select round(%s,%d) as bin, count(*) as count from hit h group by bin ;" %(freq_type,increment_log)
    elif 'c.' in where:
      #include the query modifier
      cmd = "select straight_join round(%s,%d) as bin, count(*) as count from config c, hit h where %s group by bin ;" %(freq_type,increment_log,where)
    else: cmd = "select round(%s,%d) as bin, count(*) as count from hit h where %s group by bin ;" %(freq_type,increment_log,where)
    return cmd
