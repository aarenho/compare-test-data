from . import regtest_data
from Common.utilities import InputOutput as io
import logging, os
import math
import matplotlib.pyplot as plt

logger = logging.getLogger('__main__')

class FarField( regtest_data.PyTestData ):

    def dataSummary(self):
      """
      To produce data summary that contains a dictionary
      """
      return None

    def diffSummary(self, other):
        compareRow = self.__compare(other)
        return compareRow

    def __compare(self, other):
        Emag_target_base = {}
        for freq in self.data.keys():
            Emag_target_phi_theta = []; Emag_base_phi_theta = []
            phi_theta_dict1 = self.data[freq]
            phi_theta_dict2 = other.data[freq]
            for phi, theta in phi_theta_dict1.keys():
                arr = io.arrStrTofloat(phi_theta_dict1[(phi, theta)])
                # (a+ib)*(a-ib)=a2+b2
                _Emag = (arr[0] * arr[0]) + (arr[1] * arr[1]) + (arr[2] * arr[2]) + (arr[3] * arr[3]);
                _Emag = math.sqrt(_Emag)
                Emag_target_phi_theta.append(_Emag)
            for phi, theta in phi_theta_dict2.keys():
                arr = io.arrStrTofloat(phi_theta_dict2[(phi, theta)])
                # (a+ib)*(a-ib)=a2+b2
                _Emag = (arr[0] * arr[0]) + (arr[1] * arr[1]) + (arr[2] * arr[2]) + (arr[3] * arr[3])
                _Emag = math.sqrt(_Emag)
                Emag_base_phi_theta.append(_Emag)
            Emag_target_base[freq] = [max(Emag_target_phi_theta), max(Emag_base_phi_theta)]
        freqs = Emag_target_base.keys()
        Etarget = [Emag_target_base[freq][0] for freq in freqs]
        Ebase = [Emag_target_base[freq][1] for freq in freqs]

        io.make_deep_dir(self.resourceFolder)
        png_name = self.remove_special_chars(self.inputFile.split(os.sep)[-1].split('.')[0])
        plot_png = self.resourceFolder + os.sep + png_name + '_plot.png'
        self.plot(plot_png, 'Frequency', freqs, Etarget, Ebase)
        logplot_png = self.resourceFolder + os.sep + png_name + '_logplot.png'  # log
        deal_with_zero_freqs = self.deal_with_zero_frequency(freqs)
        print self.resourceFolder
        log_freqs = [math.log10(data) for data in deal_with_zero_freqs]
        self.plot(logplot_png, 'Frequency in log scale', log_freqs, Etarget, Ebase)
        htmlcode = "<img src='%s'>\n" % ('.' + os.sep + png_name + '_plot.png')
        htmlcode += "<p></p>\n"
        htmlcode += "<img src='%s'>\n" % ('.' + os.sep + png_name + '_logplot.png')
        htmlcode += "<p></p>\n"
        plot_file = self.resourceFolder + os.sep + self.inputFile.split(os.sep)[-1].replace('.dat','.html')
        with open(plot_file, 'w') as htmlFile:
            htmlFile.write(htmlcode)

        diff_dict = {}
        for freq, val in Emag_target_base.items():
            numerator = abs(val[0] - val[1])  # Absolute difference between two |E|
            denominator = val[1]
            if denominator < 1.e-20:
                denominator = 1e-20
            diff_dict[freq] = numerator / denominator
        rel_diff = max(diff_dict.values())

        for freq, val in diff_dict.items():
            if rel_diff == 0.0:
                diff_freq = 0.0
                denominator = 0.0
                break
            if val == rel_diff:
                diff_freq = freq
                denominator = Emag_target_base[freq][1]
                break
        abs_diff = rel_diff * denominator
        key = 'E'
        verdict = self.verdict(abs_diff, rel_diff, key)
        info = self.tolerance_tooltip(key)
        compareResult = []
        compareResult.append(['Frequency', str('%.5e'%float(diff_freq)), None, plot_file.replace(self.compareHTMLDir, '.'+os.sep), '', 4])
        compareResult.append(
            ['Difference of E (V/m)', str(io.roundToSigFigs(abs_diff,2)) + ' (' + str(round(float(rel_diff) * 100, 2)) + '%)',
             verdict, None, info, 7])
        return compareResult

    def plot(self, file_path, xlabel, freq, Etarget, Ebase):
        """ produce a plot of the comparison using matplotlib """
        title = 'Maximum radiation'
        ylabel = 'r|E|(dBV)'
        plt.figure()
        plt.clf()
        plt.cla()
        res_plot, = plt.plot(freq, Ebase, 'bo', fillstyle='none', label="base")
        ref_plot, = plt.plot(freq, Etarget, 'rx', label="target")
        plt.legend(loc="center left", prop={'size': 9}, bbox_to_anchor=(0.9, 1.05), ncol=1, shadow=True, fancybox=True)
        plt.grid(True)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.savefig(file_path)
        plt.close()
        return

    def remove_special_chars(self, file_name_):
        file_name = file_name_.replace('/', '').replace('\\', '').replace('"', '') \
            .replace(':', '-').replace('*', '-').replace('?', '-').replace('<', '-') \
            .replace('>', '-').replace('|', '-').replace(' ', '')
        return file_name

    def deal_with_zero_frequency(self, inlist):
        """If there is zero as the first frequency"""
        min_inlist = min(inlist)
        if min_inlist == 0:
            zero_idx = -1
            second_min_idx = 0
            for idx, num in enumerate(inlist):
                if num == 0:
                    zero_idx = idx
                else:
                    if inlist[second_min_idx] == 0:
                        second_min_idx += 1
                    if num < inlist[second_min_idx]:
                        second_min_idx = idx

            if zero_idx != -1:
                if inlist[second_min_idx] > 1:
                    inlist[zero_idx] = 1
                else:
                    inlist[zero_idx] = (0 + inlist[second_min_idx])/10

        return inlist
