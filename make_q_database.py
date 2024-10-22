# Reads in data from all event folders in /Volumes/External/Attenuation
# for each event-station pair, placing all necessary information such as
# Q, t*, locations, times, magnitude, etc.
#
# NOTE: 4 rays have GOOD result judgements, but have been manually set
# to BAD because their .gmt files are empty (trabox didn't converge).
# Therefore, DO NOT RUN this program to remake the q_database unless
# absolutely necessary. E222-IL12, E126-IL04, E179-IL16, E21-IL13,
# E229-IL04, E401-IL07, E429-IL04, E488-IL07, E508-IL01 did not
# converge with TRABOX. If not already labeled 'BAD', mark them
# 'BAD' manually.

import numpy as np
import pandas as pd
import re
import glob, os
from datetime import datetime

def build_database():
    """This function builds a pandas dataframe full of event-station
    pairs and their statistical variables of interest."""

    q_database = pd.DataFrame({'ev_id':[],'stn_id':[],'mag':[],'stacked_qs':[],'stacked_t_star':[], \
                               'mean_qs':[],'mean_t_star':[],'stdev_qs':[],'stdev_t_star':[],'t7':[],'t8':[],'judge_result':[], \
                               'ev_lat':[],'ev_lon':[],'ev_dep':[],'stn_lat':[],'stn_lon':[], \
                               'azim':[],'b_azim':[],'ev_origin':[],'ev_wvfrm_start':[],'ev_p_arrival':[], \
                               'ev_s_arrival':[],'outliers_removed':[],'max_amp':[]})

    event_dirs = open('/Volumes/External/Attenuation/event_directories.txt','r')
    events = event_dirs.read().splitlines()

    for event_label in events:
        event_id = event_label

        time_array = event_label.split('_')
        julian = time_array[0]
        year = "20" + julian[0:2]
        day_num = julian[2:]
        hour = time_array[1]
        minute = time_array[2]
        seconds = time_array[3]
        date = datetime.strptime(year + "-" + day_num, "%Y-%j").strftime("%m-%d-%Y")
        date = str(date) + " " + hour + ":" + minute + ":" + seconds

        data_dir = "/Volumes/External/Attenuation/" + event_label
        os.chdir(data_dir)
        outfiles = glob.glob("*.out")
        outfiles.remove('qs.out')
        outfiles.remove('qsmean.out')
        stations = [file.replace('.out', '') for file in outfiles]
        for count,stn in enumerate(stations):
            if (stn == 'IL12') and (float(julian) < 16005):
                station_id = 'IL01'
            elif (stn == 'IL23') and (float(julian) < 16007):
                station_id = 'IL17'
            else:
                station_id = stn

            ofilename = data_dir + '/' + stn + '.out'
            ofile = open(ofilename,'r')
            ofile_list = ofile.read().splitlines()
            get_ev_info = ofile_list[0].split(' ')
            event_lat = get_ev_info[0]
            event_lon = get_ev_info[1]
            event_dep = get_ev_info[2]
            event_mag = get_ev_info[3]
            get_stn_info = ofile_list[2].split(' ')
            station_lat = get_stn_info[1]
            station_lon = get_stn_info[2]
            azimuth = get_stn_info[5]
            back_azimuth = get_stn_info[6]
            get_p_and_s_arrivals = ofile_list[5].split(' ')
            psec = get_p_and_s_arrivals[5] + 's'
            ssec = get_p_and_s_arrivals[7] + 's'
            get_q_info = ofile_list[405].split(' ')
            t_seven = get_q_info[1]
            t_eight = get_q_info[3]
            sum_qs = get_q_info[6]
            sum_t_star = get_q_info[9]
            get_all_q_lines = np.array([k.split(' ') for k in ofile_list[5:405]])
            q_list = [float(x) for x in get_all_q_lines[:,0]]
            t_list = [float(y) for y in get_all_q_lines[:,1]]
            q1,q3 = np.percentile(q_list,[25,75])
            iqr = q3 - q1
            low_bound = q1 - 1.5*iqr
            high_bound = q3 + 1.5*iqr
            remove_outlier = 'NO'
            for j,q_value in enumerate(q_list):
                if (q_value < low_bound) or (q_value > high_bound):
                    q_list[j] = np.nan
                    t_list[j] = np.nan
                    remove_outlier = 'YES'
            ofile.seek(0)
            ofile.close()

            if remove_outlier == 'YES':
                avg_qs = np.nanmean(q_list)
                std_qs = np.nanstd(q_list)
                avg_t_star = np.nanmean(t_list)
                std_t_star = np.nanstd(t_list)
            elif remove_outlier == 'NO':
                sfilename = data_dir + '/' + stn + '.stats'
                sfile = open(sfilename,'r')
                sfile_list = sfile.read().splitlines()
                get_mean_qs = sfile_list[4:]
                get_mean_qs_clean = [re.sub(' +',' ',s.strip()) for s in get_mean_qs]
                avg_qs = get_mean_qs_clean[0].split(' ')[3]
                std_qs = get_mean_qs_clean[2].split(' ')[5]
                if std_qs == '**********':
                    std_qs = 'NaN'
                avg_t_star = get_mean_qs_clean[7].split(' ')[3]
                std_t_star = get_mean_qs_clean[9].split(' ')[5]
                if std_t_star == '**********':
                    std_t_star = 'NaN'
                sfile.seek(0)
                sfile.close()

            
            asc_filename = data_dir + '/' + stn + '.asc'
            asc_file = open(asc_filename,'r')
            asc_file_list = asc_file.read().splitlines()
            get_ptpamp = asc_file_list[0].split(' ')
            get_ptpamp_clean = list(filter(('').__ne__,get_ptpamp))
            ptpamp = get_ptpamp_clean[2]
            get_origin = asc_file_list[14:16]
            get_origin_clean = [re.sub(' +',' ',t.strip()) for t in get_origin]
            wyear = get_origin_clean[0].split(' ')[0]
            wday = get_origin_clean[0].split(' ')[1]
            whour = get_origin_clean[0].split(' ')[2]
            wminute = get_origin_clean[0].split(' ')[3]
            wsec = get_origin_clean[0].split(' ')[4]
            wmsec = get_origin_clean[1].split(' ')[0]
            wdate = datetime.strptime(wyear + "-" + wday, "%Y-%j").strftime("%m-%d-%Y")
            wdate = str(wdate) + " " + whour + ":" + wminute + ":" + wsec + '.' + wmsec
            
            #if ((float(std_qs) <= 75) and (float(avg_qs) <= 300)) or ((float(std_qs) <= 75) and (float(avg_qs) <= 300))
            
            if (abs(float(avg_qs) - float(sum_qs)) <= float(std_qs)) and (float(std_qs) <= 0.15*float(avg_qs)) and (75 <= float(sum_qs) <= 1500) and (75 <= float(avg_qs) <= 1500):
                judge = 'GOOD'
            else:
                judge = 'BAD'
            
            q_database = q_database.append({'ev_id':event_id,'stn_id':station_id,'mag':float(event_mag), \
                                            'stacked_qs':float(sum_qs),'stacked_t_star':float(sum_t_star), \
                                            'mean_qs':float(avg_qs),'mean_t_star':float(avg_t_star),'stdev_qs':float(std_qs),'stdev_t_star':float(std_t_star), \
                                            't7':float(t_seven),'t8':float(t_eight),'judge_result':judge,'ev_lat':float(event_lat),'ev_lon':float(event_lon), \
                                            'ev_dep':float(event_dep),'stn_lat':float(station_lat),'stn_lon':float(station_lon), \
                                            'azim':float(azimuth),'b_azim':float(back_azimuth),'ev_origin':date,'ev_wvfrm_start':wdate, \
                                            'ev_p_arrival':psec,'ev_s_arrival':ssec,'outliers_removed':remove_outlier,'max_amp':float(ptpamp)},ignore_index=True)
    print(q_list)
    return q_database

q_database = build_database()
q_database = q_database[q_database['ev_dep'] >= 0.0]
q_database['ev_origin'] = pd.to_datetime(q_database['ev_origin'],format='%m-%d-%Y %H:%M:%S.%f')
q_database['ev_wvfrm_start'] = pd.to_datetime(q_database['ev_wvfrm_start'],format='%m-%d-%Y %H:%M:%S.%f')
q_database['ev_p_arrival'] = q_database['ev_wvfrm_start'] + pd.to_timedelta(q_database['ev_p_arrival'])
q_database['ev_s_arrival'] = q_database['ev_wvfrm_start'] + pd.to_timedelta(q_database['ev_s_arrival'])
q_database.pop('ev_wvfrm_start')

print(q_database.head(5))

q_database.to_csv('/Volumes/External/Attenuation/q_database.csv',index=False)