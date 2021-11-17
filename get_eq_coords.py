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
for i in indices:
    print("%9.5f %9.5f %7.4f" % (unique_q_list['ev_lon'][i],unique_q_list['ev_lat'][i],unique_q_list['ev_dep'][i]),file=ev_file)

