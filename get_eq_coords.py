# Create list of earthquake locations
import numpy as np
import pandas as pd

q = pd.read_csv('/Volumes/External/Attenuation/q_database.csv')

ev_list,indices = np.unique(q['ev_id'],return_index=True)

unique_q_list = q.iloc[indices]

print(len(ev_list))
print(unique_q_list)
print(unique_q_list['ev_lat'][2])
ev_file = open('/Users/bpk/Documents/BPK_Masters_2019/raytrace/Illapel_GMT_Files/ev_coords.txt','w')
distfile = open('/Users/bpk/Documents/BPK_Masters_2019/raytrace/Illapel_GMT_Files/cartesian_all.gmt','w')
for i in indices:
    print("%9.5f %9.5f %8.4f" % (unique_q_list['ev_lon'][i],unique_q_list['ev_lat'][i],unique_q_list['ev_dep'][i]),file=ev_file)
    dislon = 95.31*np.abs(unique_q_list['ev_lon'][i]-(-73.0))
    dislat = 111.1949*np.abs(unique_q_list['ev_lat'][i]-(-34.0))
    print("%9.5f %9.5f %8.4f" % (dislon,dislat,unique_q_list['ev_dep'][i]),file=distfile)
