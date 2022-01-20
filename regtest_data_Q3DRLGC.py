import numpy
from Common.utilities import InputOutput as io
from . import regtest_data
import logging

logger = logging.getLogger('__main__')

class Q3D_RLGC( regtest_data.PyTestData ):

  def diffSummary(self, other): 
    return self.__compare(other)

  def dataSummary(self):
    """
    To produce data summary that contains a dictionary 
    """
    return None

  def __compare(self, other):  
    RDC, LDC, RAC, LAC, G, C = self.data
    RDC2, LDC2, RAC2, LAC2, G2, C2 = other.data
    compareResult = []
    compareResult.extend( self.__compareMatrix( RDC, RDC2, "RDC") )
    compareResult.extend( self.__compareMatrix( LDC, LDC2, "LDC") )
    compareResult.extend( self.__compareMatrix( RAC, RAC2, "RAC") )
    compareResult.extend( self.__compareMatrix( LAC, LAC2, "LAC") )
    compareResult.extend( self.__compareMatrix( G, G2, "G") )
    compareResult.extend( self.__compareMatrix( C, C2, "C") )
    return compareResult

  def __average_diagonalElements(self, A, B):
      da = A.diagonal()
      db = B.diagonal()
      Ap = abs(numpy.outer(da, da))
      Bp = abs(numpy.outer(db, db))
      average = 0.5 * (numpy.sqrt(Ap, out=Ap) + numpy.sqrt(Bp, out=Bp))  # element wise sqrt
      return average

  def __compareMatrix(self, mat1, mat2, matName):
      compareResult = []
      epsilon = numpy.finfo(float).eps    # To avoid division by zero
      if mat1.size == 0 and mat2.size == 0:
         pass
      elif mat1.size != mat2.size:
        compareResult.append([matName, 'Diff in Size', 'VIOLATION', None, 'base,target '+matName+' matrices sizes differ', 9])      
      else:
        try:
            RDCdel = abs(mat1 - mat2)
            average = self.__average_diagonalElements(mat1, mat2)
            ## To avoid 0 in the denominator
            for i in range(0, len(average)):
                for j in range(0, len(average)):
                    DiagValue = abs(average[i][j])
                    if (DiagValue < 1.e-30):
                       average[i][j] = 1.0
            ##
            RDCrel = abs(RDCdel) / average
            absDiff = RDCdel.max()
            relDiff = RDCrel.max()
            for i in range(0, len(RDCrel)):
                for j in range(0, len(RDCrel)):
                    if RDCrel[i][j] == relDiff:
                        tolerance_string = 'Maximum difference found at matrix co-ordinates '+matName+'[row, col]: ['+str(i)+', '+str(j)+']'
                        break
            # find the verdict
            if 's' in self.parser.keyTolPair.keys():
              key = 's'
            else:
              key = 'CG' if matName in ('C', 'G') else 'RL'
            verdict = self.verdict(absDiff, relDiff, key)

            # find the value string
            absDiffStr = str(io.roundToSigFigs(absDiff, 2))
            relDiffStr = str(io.roundToSigFigs(relDiff*100, 2)) + '%'
            tolerance_string += self.tolerance_tooltip(key)
        except Exception as e:
            tolerance_string = 'Critical error while comparing, please take a look at the result file'
            absDiffStr = 'Err'
            relDiffStr = 'Err'
            verdict = 'VIOLATION'
        compareResult.append([matName, absDiffStr + ' (' + relDiffStr + ')',  verdict, None, tolerance_string+'\ndiff = max(abs(base matrix-target matrix))\nrel dif = max(abs(target matrix-base matrix)/diagonal_avg)', 9])
      return compareResult