import pandas as pd
import numpy as np
from pandas.io.parquet import to_parquet

s_velmod = pd.read_csv('/Users/bpk/Documents/BPK_Masters_2019/raytrace/Illapel_S_Velmod_New.csv',sep=',')
p_velmod = s_velmod.copy(deep=True)
#p_velmod = pd.read_csv('/Users/bpk/Documents/BPK_Masters_2019/raytrace/Illapel_P_Velmod_New.csv',sep=',')

p_velmod['vp'] = p_velmod['vs']*1.735
p_velmod.pop('vs')
p_velmod['vp'] = p_velmod['vp'].round(3)
print(s_velmod.tail())
print(p_velmod.tail())
#print(p_velmod.head())

s_file = open('/Users/bpk/Documents/BPK_Masters_2019/raytrace/Illapel_S_Velmod_0-180.xyzv','w')
p_file = open('/Users/bpk/Documents/BPK_Masters_2019/raytrace/Illapel_P_Velmod_0-180.xyzv','w')

for i,lon in enumerate(s_velmod['lon']):
    print("%5.1f %5.1f %3d %5.3f" % (s_velmod['lon'][i],s_velmod['lat'][i],s_velmod['dep'][i],s_velmod['vs'][i]),file=s_file)
    print("%5.1f %5.1f %3d %5.3f" % (p_velmod['lon'][i],p_velmod['lat'][i],p_velmod['dep'][i],p_velmod['vp'][i]),file=p_file)