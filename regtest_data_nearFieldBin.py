import math
import numpy as np
import logging, os
from Common.utilities import InputOutput as io
import matplotlib.pyplot as plt
from . import regtest_data

logger = logging.getLogger('__main__')

"""
Defines a literal CSV data type.
  -- data is saved in a list of list
  -- it require a file parser to produce such data
  -- it provides a comparison method to make literal comparison and produce a diff summary
  -- it provides a summary method to provide a summary.
"""

class NearFieldBin( regtest_data.PyTestData ):

  def diffSummary(self, other):
 
    if not self.__isComparable(other):
      return None

    compareRow = self.__compare(other)

    return compareRow

  def dataSummary(self):
    """
    To produce data summary that contains a dictionary 
    """
    return None

  def __isComparable(self, other):
    return True

  def __compare(self, other):
    # Retrieve information from the target file
    point_array_1 = self.data[0]
    E_1_dict = self.data[1]
    H_1_dict = self.data[2]

    # Retrieve information from tne reference file
    point_array_2 = other.data[0]
    E_2_dict = other.data[1]
    H_2_dict = other.data[2]


    if len(E_1_dict) != len(E_2_dict):
      # Number of frequencies in target not equals base
      tooltip = 'No. of frequencies in target '+str(len(E_2_dict))+' not equals to base '+str(len(E_1_dict))
      compareResult = []
      compareResult.append(['Frequency of H (Hz)', 'None', 'VIOLATION', None, tooltip, 4])
      compareResult.append(['Difference of H (A/m)', 'None', 
                            'VIOLATION', None, 'Error in calculating H (A/m)', 5])   
      compareResult.append(['Co-ordinate of H', 'None', 'VIOLATION', None, '', 6])
      compareResult.append(['Frequency of E (Hz)', 'None', 'VIOLATION', None, tooltip, 7])
      compareResult.append(['Difference of E (V/m)', 'None', 
                            'VIOLATION', None, 'Error in calculating E (V/m)', 8])   
      compareResult.append(['Co-ordinate of E', 'None', 'VIOLATION', None, '', 9])
      
      return compareResult
    
    if len(point_array_1) != len(point_array_2):
      # Number of points in target not equals base
      tooltip = 'No. of points in target '+str(len(point_array_2))+' not equals to base '+str(len(point_array_1))
      compareResult = []
      compareResult.append(['Frequency of H (Hz)', 'None', 'VIOLATION', None, tooltip, 4])
      compareResult.append(['Difference of H (A/m)', 'None', 
                            'VIOLATION', None, 'Error in calculating H (A/m)', 5])   
      compareResult.append(['Co-ordinate of H', 'None', 'VIOLATION', None, '', 6])
      compareResult.append(['Frequency of E (Hz)', 'None', 'VIOLATION', None, tooltip, 7])
      compareResult.append(['Difference of E (V/m)', 'None', 
                            'VIOLATION', None, 'Error in calculating E (V/m)', 8])   
      compareResult.append(['Co-ordinate of E', 'None', 'VIOLATION', None, '', 9])
      return compareResult
    
    #Calculation for H
    den_H_max = {}
    #Denominator
    for freq in H_2_dict:
        H_max = 0.0
        for H_2_iPoint in H_2_dict[freq]:
            H = H_2_dict[freq][H_2_iPoint]
            _H_mag = H[0]*H[0]+H[1]*H[1]+H[2]*H[2]+H[3]*H[3]+H[4]*H[4]+H[5]*H[5]
            _H_mag = math.sqrt(_H_mag)
            if _H_mag > H_max:
              H_max = _H_mag
        den_H_max[freq] = H_max
            
    max_diff_H = 0
    num_H_iPoint = -1   
    num_H_freq = -1
    H_2_val = -1
    H_1_val = -1
    plot_H = ''
    #Numerator
    for freq in H_2_dict:
        for H_2_iPoint in H_2_dict[freq]:            
            H = np.array(H_2_dict[freq][H_2_iPoint]) - np.array(H_1_dict[freq][H_2_iPoint])
            _num_H_mag = H[0]*H[0]+H[1]*H[1]+H[2]*H[2]+H[3]*H[3]+H[4]*H[4]+H[5]*H[5]
            _num_H_mag = math.sqrt(_num_H_mag)
            diff = _num_H_mag/(den_H_max[freq] + 1.0e-16)
            if (diff > max_diff_H):        
                num_H_freq = freq        
                num_H_iPoint = H_2_iPoint                
                max_diff_H = diff
                H_2_val = H_2_dict[freq][H_2_iPoint]
                H_1_val = H_1_dict[freq][H_2_iPoint]

    relDelta = max_diff_H
    h_relDiffStr = str(round( relDelta*100, 2)) + '%'
    h_cood = [-1,-1,-1] if num_H_iPoint == -1 else [format(elem, '.3e') for elem in point_array_2[num_H_iPoint]]
    H_2_val = [-1,-1,-1,-1,-1,-1] if H_2_val == -1 else [format(elem, '.3e') for elem in H_2_val]
    H_1_val = [-1,-1,-1,-1,-1,-1] if H_1_val == -1 else [format(elem, '.3e') for elem in H_1_val]
    #For plot
    if num_H_iPoint != -1:
        base_H = []; target_H = []
        for freq in H_2_dict:
            b_H = np.array(H_1_dict[freq][num_H_iPoint])
            t_H = np.array(H_2_dict[freq][num_H_iPoint])
            _b_H_mag = b_H[0]*b_H[0]+b_H[1]*b_H[1]+b_H[2]*b_H[2]+b_H[3]*b_H[3]+b_H[4]*b_H[4]+b_H[5]*b_H[5]
            _b_H_mag = math.sqrt(_b_H_mag)
            base_H.append(_b_H_mag)
            _t_H_mag = t_H[0]*t_H[0]+t_H[1]*t_H[1]+t_H[2]*t_H[2]+t_H[3]*t_H[3]+t_H[4]*t_H[4]+t_H[5]*t_H[5]
            _t_H_mag = math.sqrt(_t_H_mag)
            target_H.append(_t_H_mag)
        plot_H = self.plot('Plot of H at max diff', H_1_dict.keys(), target_H, base_H)

        # find the verdict
    key = 'e'
    verdict = self.verdict(1, relDelta, key)
    info = '[re(Hx),im(Hx),re(Hy),im(Hy),re(Hz),im(Hz)]\n'+str(H_2_val)+' vs '+str(H_1_val)
    info += self.tolerance_tooltip(key)
    compareResult = []
    compareResult.append(['Frequency of H (Hz)', str('%g'%num_H_freq), None, plot_H.replace(self.compareHTMLDir, '.'+os.sep) if plot_H else None, '', 4])
    compareResult.append(['Difference of H (A/m)', '(' + h_relDiffStr + ')', 
                          verdict, None, info, 5])   
    compareResult.append(['Co-ordinate of H', str(h_cood), None, None, '', 6])  

    #Calculation for E

    den_E_max = {}
    #Denominator
    for freq in E_2_dict:
        E_max = 0.0
        for E_2_iPoint in E_2_dict[freq]:
            E = E_2_dict[freq][E_2_iPoint]
            _E_mag = E[0]*E[0]+E[1]*E[1]+E[2]*E[2]+E[3]*E[3]+E[4]*E[4]+E[5]*E[5]
            _E_mag = math.sqrt(_E_mag)
            if _E_mag > E_max:
              E_max = _E_mag
        den_E_max[freq] = E_max
        
    max_diff_E = 0
    num_E_iPoint = -1
    num_E_freq = -1
    E_2_val = -1
    E_1_val = -1
    plot_E = ''
    #Numerator
    for freq in E_2_dict:
        for E_2_iPoint in E_2_dict[freq]:            
            E = np.array(E_2_dict[freq][E_2_iPoint]) - np.array(E_1_dict[freq][E_2_iPoint])
            _num_E_mag = E[0]*E[0]+E[1]*E[1]+E[2]*E[2]+E[3]*E[3]+E[4]*E[4]+E[5]*E[5]
            _num_E_mag = math.sqrt(_num_E_mag)
            diff = _num_E_mag/(den_E_max[freq] + 1.0e-16)            
            if (diff > max_diff_E):
              num_E_freq = freq              
              num_E_iPoint = E_2_iPoint
              max_diff_E = diff
              E_2_val = E_2_dict[freq][E_2_iPoint]
              E_1_val = E_1_dict[freq][E_2_iPoint]

    relDelta = max_diff_E
    e_relDiffStr = str(round( relDelta*100,2 ) ) + '%'
    e_cood = [-1,-1,-1]  if num_E_iPoint == -1 else [format(elem,'.3e') for elem in point_array_2[num_E_iPoint]]
    E_2_val = [-1,-1,-1,-1,-1,-1]  if E_2_val == -1 else [format(elem,'.3e') for elem in E_2_val]
    E_1_val = [-1,-1,-1,-1,-1,-1]  if E_1_val == -1 else [format(elem,'.3e') for elem in E_1_val]
    #For plot
    if num_E_iPoint != -1:
        base_E = []; target_E = []
        for freq in E_2_dict:
            b_E = np.array(E_1_dict[freq][num_E_iPoint])
            t_E = np.array(E_2_dict[freq][num_E_iPoint])
            _b_E_mag = b_E[0]*b_E[0]+b_E[1]*b_E[1]+b_E[2]*b_E[2]+b_E[3]*b_E[3]+b_E[4]*b_E[4]+b_E[5]*b_E[5]
            _b_E_mag = math.sqrt(_b_E_mag)
            base_E.append(_b_E_mag)
            _t_E_mag = t_E[0]*t_E[0]+t_E[1]*t_E[1]+t_E[2]*t_E[2]+t_E[3]*t_E[3]+t_E[4]*t_E[4]+t_E[5]*t_E[5]
            _t_E_mag = math.sqrt(_t_E_mag)
            target_E.append(_t_E_mag)
        plot_E = self.plot('Plot of E at max diff', E_1_dict.keys(), target_E, base_E)

    # find the verdict    
    key = 'e'
    verdict = self.verdict(1, relDelta, key)
    info = '[re(Ex),im(Ex),re(Ey),im(Ey),re(Ez),im(Ez)]\n'+str(E_1_val)+' vs '+str(E_2_val)
    info += self.tolerance_tooltip(key)
    
    compareResult.append(['Frequency of E (Hz)', str('%g'%num_E_freq), None, plot_E.replace(self.compareHTMLDir, '.'+os.sep) if plot_E else None, '', 7])
    compareResult.append(['Difference of E (V/m)', '(' + e_relDiffStr + ')', 
                          verdict, None, info, 8])   
    compareResult.append(['Co-ordinate of E', str(e_cood), None, None, '', 9])

    return compareResult

  def plot(self, title, freq, Ptarget, Pbase):
      """ produce a plot of the comparison using matplotlib """
      if title == 'Plot of E at max diff':
          key = "E"
      elif title == 'Plot of H at max diff':
          key = "H"
      plot_file = self.resourceFolder+os.sep+self.inputFile.split(os.sep)[-1].replace('.Nbin', '__'+key+'.html')
      io.make_deep_dir(self.resourceFolder)
      xlabel = 'Frequency'
      ylabel = 'Voltage(Volts)'
      plt.figure()
      plt.clf()
      plt.cla()
      res_plot, = plt.plot(freq, Pbase, 'bo', fillstyle='none', label="base")
      ref_plot, = plt.plot(freq, Ptarget, 'rx', label="target")
      plt.legend(loc="center left", prop={'size': 9}, bbox_to_anchor=(0.9, 1.05), ncol=1, shadow=True, fancybox=True)
      plt.grid(True)
      plt.xlabel(xlabel)
      plt.ylabel(ylabel)
      plt.title(title)
      file_name_ = self.inputFile.split(os.sep)[-1].split('.')[0]+'.png'
      file_name = file_name_.replace('/', '').replace('\\', '').replace('"', '')\
          .replace(':', '-').replace('*', '-').replace('?', '-').replace('<', '-')\
          .replace('>', '-').replace('|', '-').replace(' ', '')
      file_path = self.resourceFolder + os.sep + file_name
      plt.savefig(file_path)
      htmlcode = "<img src='%s'>\n" %('.'+os.sep+file_name)
      htmlcode += "<p></p>\n"
      plt.close()
      with open(plot_file, 'w') as htmlFile:
          htmlFile.write(htmlcode)
      return plot_file
