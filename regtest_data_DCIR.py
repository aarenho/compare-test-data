import logging
from . import regtest_data

logger = logging.getLogger('__main__')

class Sdc(regtest_data.PyTestData):

    def diffSummary(self, other):
        compareRow = self.__compare(other)
        return compareRow

    def __compare(self, other):
        """
        rtype: list of string
        """
        n = len(self.data) - 1
        maxDelta = 0.0
        relDelta = 0.0
        maxI = 1
        maxJ = 1
        sij = float(self.data[1][1])
        otherSij = float(other.data[1][1])
        for i in range(1, n+1):
            for j in range(1, n+1):
                delta = abs(float(self.data[i][j]) - float(other.data[i][j]))
                if delta > maxDelta:
                    maxDelta = delta
                    maxI = i
                    maxJ = j
                    sij = float( self.data[i][j] )
                    otherSij = float( other.data[i][j] )
                    if float(other.data[i][j]) == 0:
                        relDelta = 100; # asign a large value here
                    else:
                        relDelta = float(maxDelta) / float(other.data[i][j])            

        compareResult = []
        # find the verdict
        verdict = self.verdict( maxDelta, relDelta, 's' )

        compareResult.append(['max diff', str(round((maxDelta),2)) + ' (' + str(round( (relDelta)*100,2 ) ) + '%)', 
                            verdict, None, str(round(sij,2)) + ' vs. ' + str(round(otherSij,2)), 9])
        compareResult.append(['row', str(maxI), None, None, '', 9])
        compareResult.append(['col', str(maxJ), None, None, '', 9])
        return compareResult

class Ced(regtest_data.PyTestData):

    def diffSummary(self, other):
        compareRow = self.__compare(other)
        return compareRow

    def __compare(self, other):
        """
        rtype: list of strings
        """
        maxNodeVp = ''
        maxDeltaVp = 0.0
        maxNodeVn = ''
        maxDeltaVn = 0.0
        maxNodeI = ''
        maxDeltaI = 0.0
        for i in range(len(self.data)):
            deltaVp = abs(float(self.data[i][1]) - float(other.data[i][1]))
            deltaVn = abs(float(self.data[i][2]) - float(other.data[i][2]))
            deltaI = abs(float(self.data[i][3]) - float(other.data[i][3]))
            if deltaVp > maxDeltaVp:
                maxDeltaVp = deltaVp
                maxNodeVp = self.data[i][0]
            if deltaVn > maxDeltaVn:
                maxDeltaVn = deltaVn
                maxNodeVn = self.data[i][0]
            if deltaI > maxDeltaI:
                maxDeltaI = deltaI
                maxNodeI = self.data[i][0]
           
        compareResult = []

        verdict = self.verdict( maxDeltaVp, 0, 'vp' )
        compareResult.append(['maxDeltaVp', str(round((maxDeltaVp),2)), verdict, None, str(maxNodeVp), 9])

        verdict = self.verdict( maxDeltaVn, 0, 'vn' )
        compareResult.append(['maxDeltaVn', str(round((maxDeltaVn),2)), verdict, None, str(maxNodeVn), 9])

        verdict = self.verdict( maxDeltaI, 0, 'i' )
        compareResult.append(['maxDeltaI', str(round((maxDeltaI),2)), verdict, None, str(maxNodeI), 9])

        return compareResult


class PathresLrp(regtest_data.PyTestData):

    def diffSummary(self, other):
        compareRow = self.__compare(other)
        return compareRow

    def __compare(self, other):
        """
        rtype: list of string
        """      
        maxDelta = 0.0
        maxN1 = ''
        maxN2 = ''
        I = 0
        J = 1
        R = 2
        for i in range(len(self.data)):
            delta = abs(float(self.data[i][R]) - float(other.data[i][R]))
            if delta > maxDelta:
                maxDelta = delta
                maxN1 = self.data[i][I]
                maxN2 = self.data[i][J]
        #return maxDelta, maxN1, maxN2
        compareResult = []
        verdict = self.verdict( maxDelta, 0, 'vp' )
        compareResult.append(['maxDelta', str(round((maxDelta),2)), verdict, None, '', 9])
        compareResult.append(['max N1', str(maxN1), None, None, '', 9])
        compareResult.append(['max N2', str(maxN2), None, None, '', 9])
        return compareResult

class Resonance(regtest_data.PyTestData):

    def diffSummary(self, other):
        compareRow = self.__compare(other)
        return compareRow

    def __compare(self, other):
        """
        rtype: list of string
        """
        compareResult = []
        maxDelta = 0.0
        maxrelDiff = 0.0
        modeValue = 0
        basValue = 0.0
        tarValue = 0.0
        tablecol = 3
        for key in self.data.keys():
          if key != 'mode':
            for keyValue in range(len(self.data[key])):
              delta = abs(float(self.data[key][keyValue]) - float(other.data[key][keyValue]))              
              relDiff = delta/float(other.data[key][keyValue])
              if delta > maxDelta:
                maxDelta = delta                
                modeValue = self.data['mode'][keyValue]
                basValue = float(self.data[key][keyValue])
                tarValue = float(other.data[key][keyValue])
                maxrelDiff = delta/tarValue

            # find the verdict
            tolKey = 'E'
            verdict = self.verdict(maxDelta, maxrelDiff, tolKey)
            info = self.tolerance_tooltip(tolKey)                        

            # find the value string
            absDiffStr = str(round( maxDelta, 2 ))
            relDiffStr = str(round( maxrelDiff*100, 2 )) + '%'
            tablecol += 2
            compareResult.append(['Diff of '+key, absDiffStr + ' (' + relDiffStr + ')',  verdict, None, str(basValue)+' vs '+str(tarValue) + info, tablecol])
            compareResult.append(['mode at '+key+' diff max', str(modeValue), verdict, None, '', tablecol+1])
        return compareResult
   