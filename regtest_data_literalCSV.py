from Common.regData import regtest_data

"""
Defines a literal CSV data type.
  -- data is saved in a list of list
  -- it require a file parser to produce such data
  -- it provides a comparison method to make literal comparison and produce a diff summary
  -- it provides a summary method to provide a summary.
"""

class LiteralCSV( regtest_data.PyTestData ):

  def diffSummary(self, other): 
    return self.__compare(other)

  def __compare(self, other):

    if self.data.rows == [['File empty']] or other.data.rows == [['File empty']]:
      compareResult =  [['TXT', 'Identical', 'PASS', None, 'File(s) empty', 9]]
      return compareResult
    elif self.data.rows == [['Parsing failed']] or other.data.rows == [['Parsing failed']]: 
      compareResult = [['Error', 'Not Comparable','VIOLATION', None, 'Failed to Parse file(s)', 9 ]] 
      return compareResult
    elif not self.isComparable(other):
      compareResult =  [['TXT', 'Different','VIOLATION',None,'Number of Row(s)/Col(s) are different', 9 ]]      
      return compareResult

    try:
      numElem = 0
      if len(self.data.rows) > 0:
        numElem = len(self.data.rows[0])

      if numElem > 0:
        self.data.rows.sort(key = lambda x: tuple([x[i] for i in range(0, numElem) ] ) )
        other.data.rows.sort(key = lambda x: tuple([x[i] for i in range(0, numElem) ] ) )
    except:
      # that is ok, we can still continue
      nothing = 1

    for row in range(0, len(self.data.rows)):
      for col in range (0, len(self.data.rows[row])):
        try:
          if self.data.rows[row][col] != other.data.rows[row][col]:
            compareResult =  [['TXT', 'Different','VIOLATION',None,'Values are not equal', 9 ]]
        except:
          compareResult =  [['TXT', 'Different','VIOLATION',None,'open result to check difference', 9 ]]
    
    compareResult =  [['TXT', 'Identical', 'PASS', None, 'ASCII identical', 9]]
    return compareResult

  def dataSummary(self):
    """
    To produce data summary that contains a dictionary 
    """
    self.dataSummary = self.data.rows[0]

  def isComparable(self, other):
    numElem = 0
    numElem_other = 0
    if len(self.data.rows) > 0:
      numElem = len(self.data.rows[0])
      numRows = len(self.data.rows) 
    if len(other.data.rows) > 0:
      numElem_other = len(other.data.rows[0])
      numRows_other = len(other.data.rows)
    if (numElem != numElem_other) or (numRows != numRows_other):      
      return False

    return True
