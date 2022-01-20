import logging
from . import regtest_data

logger = logging.getLogger('__main__')

"""
Defines a literal CSV data type.
  -- data is saved in a list of list
  -- it require a file parser to produce such data
  -- it provides a comparison method to make literal comparison and produce a diff summary
  -- it provides a summary method to provide a summary.
"""

class ImpedanceScan( regtest_data.LiteralCSV ):
  def diffSummary(self, other):
 
    if not self.__isComparable(other):
      return [['Error', 'Not Comparable','VIOLATION', None, 'open result to check difference', 9 ]]

    try:
      numRows = len(self.data.rows)
      numElem = 0
      if numRows > 0:
        numElem = len(self.data.rows[0])

      if numElem > 0:
        self.data.rows.sort(key = lambda x: tuple([x[i] for i in range(0, numElem) ] ) )
        other.data.rows.sort(key = lambda x: tuple([x[i] for i in range(0, numElem) ] ) )
    except:
      return [['Error', 'Sort data failed','VIOLATION', None, 'open result to check difference', 9 ]]
      

    for row in range(0, len(self.data.rows)):
      for col in range (0, len(self.data.rows[row])):
        try:
          if self.data.rows[row][col] != other.data.rows[row][col]:
            return  [['TXT', 'Different','VIOLATION',None,'open result to check difference', 9 ]]
        except:
          return  [['TXT', 'Different','VIOLATION',None,'open result to check difference', 9 ]]

    return  [['TXT', 'Identical', 'PASS', None, 'ASCII identical', 9]]

  def dataSummary(self):
    """
    To produce data summary that contains a dictionary 
    """
    self.dataSummary = self.data.rows[0]

