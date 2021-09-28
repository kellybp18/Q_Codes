import numpy as np
#import pandas as pd
import matplotlib.pyplot as plt
import re
#
def read_spectra():
    """This function reads in all of the spectra from
    the filtering event directories, picks t7 and t8,
    and calculates t* and Qs"""

    spec_file = "/tmp/ratio.spec"
    spec = open(spec_file,"r")
    spec_list = spec.read().splitlines()[30:235]
    spec_list_clean = [re.sub(' +',' ',s.strip()) for s in spec_list]
    spec_list_split = [t.split(' ') for t in spec_list_clean]
    spec_list_split[-1].append("0")
    spec_data = np.array(spec_list_split,dtype=float)
    spec_data = np.reshape(spec_data,-1)
    freq_array = (50/1024)*np.array(range(1024), dtype=float)
    linefit_x_data = freq_array[511:819]
    linefit_y_data = spec_data[511:819]
    linefit_coeffs = np.polyfit(linefit_x_data,linefit_y_data,1)
    slope = linefit_coeffs[0]
    y_int = linefit_coeffs[1]
    residuals = np.array(np.zeros(len(linefit_x_data)),dtype=float)
    for idx,x in enumerate(linefit_x_data):
        y_hat = slope*x + y_int
        residual = linefit_y_data[idx] - y_hat
        residuals[idx] = residual
    max_residual = max(residuals)
    freq_band_x_data = freq_array[0:410]
    freq_band_y_data = spec_data[0:410]
    i = len(freq_band_x_data) - 1
    while i >= 0 :
        y_hat_band = slope*freq_band_x_data[i] + y_int
        residual_band = freq_band_y_data[i] - y_hat_band
        if residual_band > max_residual:
            t_eight = freq_band_x_data[i]
            break
        i -= 1

    if 't_eight' in locals():
        pass
    else:
        t_eight = 19.970703125
           
    spec.seek(0)
    labels_line = re.sub(' +',' ',spec.read().splitlines()[2].strip())
    labels_line = labels_line.split(' ')
    labels_array = np.array(labels_line,dtype=float)
    t_seven_close = labels_array[1]
    if t_seven_close > 15.0:
        t_seven_close = 15.0
    if (t_eight - t_seven_close) < 4.0:
        t_eight_est = t_seven_close + 4.0
        t_eight_idx = (np.abs(freq_band_x_data - t_eight_est)).argmin()
        t_eight = freq_band_x_data[t_eight_idx]
    index = (np.abs(freq_band_x_data - t_seven_close)).argmin()
    t_seven = freq_band_x_data[index]

    # spec.seek(0)
    # times_line = re.sub(' +',' ',spec.read().splitlines()[8].strip())
    # times_line = times_line.split(' ')
    # times_array = np.array(times_line,dtype=float)
    # tp = times_array[2]
    # ts = times_array[3]

    print(t_seven, t_eight)

    # t_seven_index = np.where(freq_band_x_data == t_seven)
    # t_seven_index = int(t_seven_index[0])
    # t_eight_index = np.where(freq_band_x_data == t_eight)
    # t_eight_index = int(t_eight_index[0])
    # print(t_seven_index,t_eight_index)
    # final_linefit_x_data = freq_band_x_data[t_seven_index:t_eight_index]
    # final_linefit_y_data = freq_band_y_data[t_seven_index:t_eight_index]
    # final_linefit_coeffs = np.polyfit(final_linefit_x_data,final_linefit_y_data,1)
    # final_slope = final_linefit_coeffs[0]
    # aob2p = (ts/tp)**2
    # tstar = final_slope/(-3.1415926535)
    # qs = (ts - 4.0*tp/(3.0*aob2p))/tstar
    # q_data[stn_lines.index(stn)][0] = qs
    # q_data[stn_lines.index(stn)][1] = tstar
    # q_data[stn_lines.index(stn)][2] = t_seven
    # q_data[stn_lines.index(stn)][3] = t_eight

    spec.seek(0)
    spec.close()

    dropfile = open("/tmp/freq_picks.txt","w")
    dropfile.write(str(t_seven) + "\n" + str(t_eight))
    dropfile.close
    
    return

read_spectra()