def generate(col_names,table_names,limit='',where=''):
  """ Generates a MySQL command.
      
      col_names is a string of the name(s) of the column(s), 
      separated by commas
      
      table_name(s) is a string of the name of the table(s), 
      separated by commas
      
      IF YOU USE COLUMNS FROM DIFFERENT TABLES:
      INCLUDE THE PREFIX "first letter of table" "dot" IN
      EACH COL_NAME. Ex: 'c.binnum' for column binnum in 
      table config. ALSO PLACE FIRST LETTER OF TABLE AFTER 
      EACH TABLE_NAME. Ex: 'hit h, config c'
      
      limit is a value that limits the number of output 
      results
     
      where is an optional string to include additional 
      constraints in the command

      the command is returned as a string """

  
  cmd = 'select straight_join %s from %s' %(col_names,table_names)
  # add additional info to string
  if where != '':
    cmd = cmd + ' where ' + where
  if limit != '':
    cmd = cmd + ' limit %s' %limit
  cmd = cmd + ';'

  return cmd
  
