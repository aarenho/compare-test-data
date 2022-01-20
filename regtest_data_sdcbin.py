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


class SDCBIN(regtest_data.PyTestData):
    TOO_MANY_PORTS_TO_PROCESS = 10

    # SMALL_S_VALUE is used to calculate relative difference
    # relative diff =| (abs diff) / magnitude            if magnitude > SMALL_S_VALUE
    #                | abs diff                          otherwise
    SMALL_S_VALUE = 0.001

    def diffSummary(self, other):
        try:
            compareRow = self.__compare(other)
        except:
            logger.error(
                "Failed to Compare " + self.name + " v/s " + other.name + " " + self.resourceFolder.split(os.sep)[-1])
            compareRow = [['Error', 'Not Comparable', 'VIOLATION', None, 'Failed', 3]]
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
            compareResult = [['Error', 'Not Comparable', 'VIOLATION', None, 'ports are not equal', 3]]
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
            for sj in range(0, si + 1):  # s matrix is symmetric

                # Get S_si_sj for all frequencies
                idx += 2

                # skip off diagonal terms if port number is large
                if self.data.nPorts >= self.TOO_MANY_PORTS_TO_PROCESS:
                    if sj != si:
                        continue

                freq_1 = self.data.data[0]
                Sij_1_r = self.data.data[idx]
                Sij_1_i = self.data.data[idx + 1]
                freq_2 = other.data.data[0]
                Sij_2_r = other.data.data[idx]
                Sij_2_i = other.data.data[idx + 1]

                # get interpolator for the second curve
                data2_r_interpolator = Interpolator_Linear.LinearInterpolator(freq_2, Sij_2_r)
                data2_i_interpolator = Interpolator_Linear.LinearInterpolator(freq_2, Sij_2_i)

                # compare s parameter at this frequency
                for iRow in range(0, self.data.nFreqs):
                    # compute absolute delta
                    S2r = data2_r_interpolator.interpolate(freq_1[iRow])
                    S2i = data2_i_interpolator.interpolate(freq_1[iRow])
                    delta_r = math.fabs(Sij_1_r[iRow] - S2r)
                    delta_i = math.fabs(Sij_1_i[iRow] - S2i)
                    delta_sq = delta_r * delta_r + delta_i * delta_i
                    # compute relative delta
                    mag_sq = S2r * S2r + S2i * S2i
                    if (mag_sq > small_S_value_sq):
                        relDelta_sq = delta_sq / mag_sq
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

        # build the info line
        info = str(round(max1_r, 4))
        if max1_i >= 0:
            info = info + '+'
        info = info + str(round(max1_i, 4)) + 'i vs ' + str(round(max2_r, 4))
        if max2_i >= 0:
            info = info + '+'
        info = info + str(round(max2_i, 4)) + 'i' + '\nmax diff at freq with' + self.tolerance_tooltip(key)

        # assemble proper data to generate table
        compareResult = []
        compareResult.append(['max diff', str(round(maxDelta, 2)) + ' (' + str(round(maxDeltaRelative * 100, 2)) + '%)',
                              verdict, None, info, 9])
        compareResult.append(['f(Hz) at Max', str('%g' % maxDelta_frequency), None, None, '', 9])
        compareResult.append(['row at Max', str(maxDelta_row_1based), None, None, '', 9])
        compareResult.append(['col at Max', str(maxDelta_col_1based), None, None, '', 9])

        return compareResult