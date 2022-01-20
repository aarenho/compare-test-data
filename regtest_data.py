import decimal
import logging

logger = logging.getLogger('__main__')

"""
We got all types of result data. How to process them?


Ultimate Goal:
  Given a input file with known format, provide a class that is able to
    1) produce a data summary in the form of a dictionary: { 'name': value, ... }
    2) produce a compare summary, when comparing with a given "other object"
       of the same class, in the form of a dictionary : { 'name': value, ...}
    3) Other formats of summaries???

Implementation:
  "PyTest File" contains all sorts of data that are saved in either ASCII or binary files.
    -- It requires a 'reader' to understand the format of the file to read them to get
       the raw data from the file.

  "PyTest Comparator" are formated data that is parsed from the contents of a "PyTest File"
    -- After the file is read, a parser need to be used to re-organize the data into 
       some meaningful format for easy processing.

       Best to have:
        The specific format of PyTest Comparator should be general enough to reduce the processing
        complexity. Ideally, we hope to have only a few standard formats to cover all senarioes.

  In general, a file reader can be implemented separately from data parser. However, they can be combined
  such that for a given input file, the parser is able to grab necessary data.
  
  PyTestData class can be used as a parent class for all other data types. 
  PytestData takes a specialized parser to read and parse input file to produce a
            intermediate data collection, 
  which can be used to generate:
    a compare summary and a data summary
  
  To define a specialized data type. 
    1) define your customized parser, for example, see parser_csv.py
    2) define a new data class derive from PyTestData. In order to use your
       customized parser, instantiate your object by providing your customized parser:
         newObject = MyData( 'inputFileName.txt', MyParser )

    3) define diffSummary function.
    4) define dataSummary function.

    See 'regtest_data_literalCSV.py' for an usage example.
"""

class PyTestData:
    """
    Base class for data that Pytest used to generate different reports.

    For example:
      1) SIwave test produces test.slog file. PyTestData can be obtained from test.slog file using "parser_slog.SIwave_SYZ_slog"
      2) SIwave test produces test.sbin file. PyTestData can also be obtained from sbin.dat file using "parser_sbin.sbin"
      3) SIwave test produces testSegmentsZ.txt file. PyTestData can also be obtained from testSegmentsZ.txt file using "parser_csv.Parser_CSV"

      So a PyTestData can be obtained from a "input file" using an appropriate parser.

    All data in pytest has a way to compare with another data of same class and produce a dictionary containing name-"value and attributes" pairs
      Note that the unit of the value can be included in the name.
      For the purpose of uniform HTML report table gneration, specific formats of the "value and attributes" list is helpful. See other parts of
      PyTest for the usage examples.

    Any class derived from PyTestData need to implement at least:
      1)  diffSummary( other ) to return a dictionary.
      2)  dataSummary() to return a dictionary

    """
    def __init__(self, compareHTMLDir = '', resourceFolder='' ):
      self.keyTolPair = {}
      self.compareHTMLDir = compareHTMLDir
      self.resourceFolder = resourceFolder
      self.name = ''

    def verdict( self, absDiff, relDiff, key ):
        decision = self.verdictTimeMem(absDiff, relDiff, key)
        if decision is not None:
          return decision
        if abs(absDiff) > self.keyTolPair[key][0] and abs(relDiff) > self.keyTolPair[key][2]:
          return 'VIOLATION'
        elif abs(absDiff) > self.keyTolPair[key][1] and abs(relDiff) > self.keyTolPair[key][3]:
          return 'WARNING'
        else:
          return 'PASS'

    def verdictTimeMem( self, absDiff, relDiff, key ):
        if any(substring in key for substring in ['Time', 'time', 'Memory', 'memory', 'Sec', 'sec']):
          if absDiff > self.keyTolPair[key][0] and relDiff > self.keyTolPair[key][2]:
            decision = 'VIOLATION'
          elif absDiff > self.keyTolPair[key][1] and relDiff > self.keyTolPair[key][3]:
            decision = 'WARNING'
          else:
            decision = 'PASS'
        else:
          decision = None
        return decision

    def SetParser( self, parser ):
      self.parser = parser
  
    def Read(self, input):
      self.inputFile = input
      self.data = self.parser.Parse(input)
      self.exception = self.parser.exception
      self.keyTolPair = self.parser.keyTolPair

    def diff(self, other):
      if (self.exception is not None) or (other.exception is not None):
          msg = 'version '
          if self.exception is not None:
            msg = msg + self.name + ':' + self.exception
            verdict = 'VIOLATION'
          if other.exception is not None:
            msg = msg + other.name + ':' + other.exception
            verdict = 'VIOLATION'
          if (self.exception is not None) and (other.exception is not None):
            verdict = 'PASS'
          compareResult = [[ 'Exception', msg, verdict, None, '', 3]]
      else:
        compareResult = self.diffSummary(other)    
      return compareResult 

    def summary(self):
      return self.dataSummary()

    def diffSummary(self, other):
      logger.error("Please implement for your specific data type.")
      return None

    def dataSummary(self):
      logger.error("Please implement for your specific data type.")
      return None
    
    def tolerance_tooltip(self, key):
        tolerance_tooltip = '\ntolerance:\nVIOLATION: >'+self.to_NiceFormatString(self.keyTolPair[key][0])+'and(>'+self.to_percent(self.keyTolPair[key][2])+')\nWARNING: >'+\
                            self.to_NiceFormatString(self.keyTolPair[key][1])+'and(>'+self.to_percent(self.keyTolPair[key][3])+')'
        return tolerance_tooltip
  
    def to_NiceFormatString(self, float):
        if abs(float) > 100 or ( abs(float) < 0.01 and float != 0 ):
          return ('%.'+str(1) + 'E') % decimal.Decimal(float)
        else:
          return str(float)     

    def to_percent(self, float ):
        return str(float*100) + '%'

