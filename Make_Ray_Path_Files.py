import numpy as np
import pandas as pd

q = pd.read_csv('/Volumes/External/Attenuation/q_database.csv')

ev_list,indices = np.unique(q['ev_id'],return_index=True)

unique_q_list = q['ev_id'].iloc[indices].reset_index(drop=True)

print(unique_q_list)
last_event_num = 0

ray_file = open('/Users/bpk/Documents/AGU_2021/RayQsList.txt','w')
ev_file = open('/Users/bpk/Documents/AGU_2021/EventInfo.txt','w')
good_rays = q[q['judge_result'] == 'GOOD'].reset_index(drop=True)
for i,event in enumerate(good_rays['ev_id']):
    event_num = unique_q_list.index[unique_q_list == event].to_list()[0] + 1
    event_lon = good_rays['ev_lon'][i]
    event_lat = good_rays['ev_lat'][i]
    event_dep = good_rays['ev_dep'][i]
    if event_num != last_event_num:
        print("%8.4f %8.4f %8.4f" % (event_lon,event_lat,event_dep),file=ev_file)
    last_event_num = event_num

    print(event_num)
    ray_q = good_rays['stacked_qs'][i]
    stn = good_rays['stn_id'][i]
    gmt_filename = '/Users/bpk/Documents/BPK_Masters_2019/raytrace/Illapel_GMT_Files/E' + str(event_num) + '-' + stn + '.gmt'
    print(gmt_filename)
    print("%s %4d" % (gmt_filename,int(np.round(ray_q,decimals=0))),file=ray_file)
