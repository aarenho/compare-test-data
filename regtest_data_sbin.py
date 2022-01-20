import os
import math
import regtest_data
import regtest_plot
from Common.utilities import InputOutput as io
from Common.utilities import Interpolator_Linear
import logging

logger = logging.getLogger('__main__')

"""
Defines a literal CSV data type.
  -- data is saved in a list of list
  -- it require a file parser to produce such data
  -- it provides a comparison method to make literal comparison and produce a diff summary
  -- it provides a summary method to provide a summary.
"""

class SBIN( regtest_data.PyTestData ):

  TOO_MANY_PORTS_TO_PROCESS = 10

  # SMALL_S_VALUE is used to calculate relative difference
  # relative diff =| (abs diff) / magnitude            if magnitude > SMALL_S_VALUE
  #                | abs diff                          otherwise
  SMALL_S_VALUE = 0.001

  def diffSummary(self, other):
    try:
      compareRow = self.__compare(other)
    except:
      logger.error("Failed to Compare "+self.name+" v/s "+other.name+" "+self.resourceFolder.split(os.sep)[-1])
      compareRow = [['Error', 'Not Comparable','VIOLATION', None, 'Failed', 3 ]]
    return compareRow

  def dataSummary(self):
    """
    To produce data summary that contains a dictionary 
    """
    return None

  def __isComparable(self, other):
    if self.data.nPorts != other.data.nPorts:
      return False

    return True

  def __compare(self, other):
      if not self.__isComparable(other):
        compareResult = [['Error', 'Not Comparable','VIOLATION', None, 'ports are not equal', 3 ]]
        return compareResult

      if self.data.data == None and other.data.data == None:
         compareResult = []
         compareResult.append(['max diff', '--', None, None, 'Empty base and target', 9])
         compareResult.append(['f(Hz) at Max', '--', None, None, 'Empty base and target', 9])
         compareResult.append(['row at Max', '--', None, None, 'Empty base and target', 9])
         compareResult.append(['col at Max', '--', None, None, 'Empty base and target', 9])
         return compareResult

      PRECISION = 2
      # get max difference
      maxDelta = 0
      maxDeltaRelative = 0
      maxDelta_frequency = 0
      maxDelta_row_1based = 1
      maxDelta_col_1based = 1
      magnitude = 0
      self.maxIdx = 1
      max1_r = 0
      max1_i = 0
      max2_r = 0
      max2_i = 0

      small_S_value_sq = self.SMALL_S_VALUE * self.SMALL_S_VALUE

      # Check S_si_sj at all sampling frequency according to self sampling frequency points
      idx = -1
      for si in range(0, self.data.nPorts):
          for sj in range(0, si+1):  # s matrix is symmetric

              # Get S_si_sj for all frequencies
              idx += 2

              # skip off diagonal terms if port number is large
              if self.data.nPorts >= self.TOO_MANY_PORTS_TO_PROCESS:
                if sj != si:
                  continue

              freq_1 = self.data.data[0]
              Sij_1_r = self.data.data[idx]
              Sij_1_i = self.data.data[idx+1]
              freq_2 = other.data.data[0]
              Sij_2_r = other.data.data[idx]
              Sij_2_i = other.data.data[idx+1]
        
              # get interpolator for the second curve
              data2_r_interpolator = Interpolator_Linear.LinearInterpolator(freq_2, Sij_2_r)
              data2_i_interpolator = Interpolator_Linear.LinearInterpolator(freq_2, Sij_2_i)

              # compare s parameter at this frequency
              for iRow in range(0, self.data.nFreqs):
                  # compute absolute delta
                  S2r = data2_r_interpolator.interpolate(freq_1[iRow])
                  S2i = data2_i_interpolator.interpolate(freq_1[iRow])
                  delta_r = math.fabs( Sij_1_r[iRow] - S2r )
                  delta_i = math.fabs( Sij_1_i[iRow] - S2i )
                  delta_sq =  delta_r * delta_r + delta_i * delta_i
                  # compute relative delta
                  mag_sq =  S2r * S2r + S2i * S2i
                  if ( mag_sq > small_S_value_sq ):
                      relDelta_sq = delta_sq/mag_sq
                  else:
                      relDelta_sq = delta_sq
                      # record max difference
                  if (delta_sq > maxDelta):
                      maxDelta = delta_sq
                      maxDeltaRelative = relDelta_sq
                      maxDelta_frequency = freq_1[iRow]
                      maxDelta_row_1based = si + 1
                      maxDelta_col_1based = sj + 1
                      self.maxIdx = idx
                      magnitude = mag_sq
                      max1_r = Sij_1_r[iRow]
                      max1_i = Sij_1_i[iRow]
                      max2_r = S2r
                      max2_i = S2i

      self.maxDelta_row_1based = maxDelta_row_1based
      self.maxDelta_col_1based = maxDelta_col_1based

      maxDeltaRelative = math.sqrt(maxDeltaRelative)
      maxDelta = math.sqrt(maxDelta)

      # find the verdict
      key = 's'
      verdict = self.verdict(maxDelta, maxDeltaRelative, key)

      # create a plot for the significant curve
      frequency,frequency1,sValue_r,sValue_i,xLable,yLable,title,legend = self.get_plot_data( other )
      jsFile = 'syzplotter.js'
      io.make_deep_dir(self.resourceFolder)
      io.copy_one_file_to_another( jsFile, self.resourceFolder)
      plotFile = os.path.join(self.resourceFolder, 'splot.html')
      regtest_plot.Plot(jsFile, plotFile, frequency, sValue_r, sValue_i, xLable, yLable, title, legend)
      plot1File = os.path.join(self.resourceFolder, 'splot1.html')
      regtest_plot.Plot(jsFile, plot1File, frequency1, sValue_r, sValue_i, xLable+' in log scale', yLable, title, legend)
      with open(plotFile, 'a') as file1, open(plot1File, 'r') as file2:
        #file1.write(file2.read())
        for line in file2:
            if 'Max S parameter difference' in line:
              continue
            file1.write(line)
      io.remove_a_file(plot1File)

      # build the info line
      info = str(round(max1_r,4))
      if max1_i >= 0:
        info = info + '+'
      info = info + str(round(max1_i,4)) + 'i vs ' + str(round(max2_r,4))
      if max2_i >= 0:
         info = info + '+'
      info = info + str(round(max2_i,4))  + 'i' + '\nmax diff at freq with' +self.tolerance_tooltip(key)

      # assemble proper data to generate table
      compareResult = []
      compareResult.append(['max diff', str(round(maxDelta,2)) + ' (' + str(round( maxDeltaRelative*100,2 ) ) + '%)', 
                        verdict, plotFile.replace(self.compareHTMLDir, '.'+os.sep), info, 9])
      compareResult.append(['f(Hz) at Max', str('%g'%maxDelta_frequency), None, None, '', 9])
      compareResult.append(['row at Max', str(maxDelta_row_1based), None, None, '', 9])
      compareResult.append(['col at Max', str(maxDelta_col_1based), None, None, '', 9])

      return compareResult

  def get_plot_data(self, other):
      """Return the data necessary to plot using regtest_plot"""
      frequency = []; frequency1 = []; sValue_r = []; sValue_i = []
      # prepare data1
      frequency.append(self.deal_with_zero_frequency(self.data.data[0]))
      sValue_r.append(self.deal_with_zero_sParam_values(self.data.data[self.maxIdx]))
      sValue_i.append(self.deal_with_zero_sParam_values(self.data.data[self.maxIdx+1]))
      # prepare data2
      frequency.append(self.deal_with_zero_frequency(other.data.data[0]))
      sValue_r.append(self.deal_with_zero_sParam_values(other.data.data[self.maxIdx]))
      sValue_i.append(self.deal_with_zero_sParam_values(other.data.data[self.maxIdx+1]))
      # prepare data1 x scale in semilog to observe dc        
      selfdata = self.deal_with_zero_frequency(self.data.data[0][:])
      otherdata = self.deal_with_zero_frequency(other.data.data[0][:])
      frequency1.append([math.log10(data) for data in selfdata])
      frequency1.append([math.log10(data) for data in otherdata])
      sValue_r.append(self.deal_with_zero_sParam_values(self.data.data[self.maxIdx][:]))
      sValue_i.append(self.deal_with_zero_sParam_values(self.data.data[self.maxIdx+1][:]))
      # prepare data2 x scale in semilog to observe dc      
      sValue_r.append(self.deal_with_zero_sParam_values(other.data.data[self.maxIdx][:]))      
      sValue_i.append(self.deal_with_zero_sParam_values(other.data.data[self.maxIdx+1][:]))
      # legend = self.compareConfig.get_versionPair()
      xLable = 'Frequency(Hz)'
      yLable = 'S'
      title = "S_{!s}_{!s}".format( str(self.maxDelta_row_1based), str(self.maxDelta_col_1based) )
      legend = ['target', 'base']        
      return frequency,frequency1,sValue_r,sValue_i,xLable,yLable,title,legend

  def deal_with_zero_frequency(self, inlist):
      """If there is zero as the first frequency"""
      outlist = inlist
      if outlist[0] == 0:
        if outlist[1] > 1:
          outlist[0] = 1
        else:
          outlist[0] = (outlist[0]+outlist[1])/10
      return outlist

  def deal_with_zero_sParam_values(self, inlist):
      """If there is zeroes in S-Matrix"""         
      outlist = [dataPt+1e-10 if dataPt == 0 else dataPt for dataPt in inlist]
      return outlist


  def get_s_parameter(self, row, col):
      """Get the values of frequency, real and imaginary values of s-parameter at a row and col"""
      idx = -1    
      for si in range(0, self.data.nPorts):
          for sj in range(0, si+1):  # s matrix is symmetric
              idx += 2
              if si == row - 1 and sj == col - 1:
                  frequency = self.data.data[0]
                  sValue_r = self.data.data[idx]
                  sValue_i = self.data.data[idx+1]
                  return (frequency, sValue_r, sValue_i)

      return None