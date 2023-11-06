import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pyproj
from scipy.spatial.transform.rotation import Rotation

lat_scale = 111.1949 # km per deg latitude
lon_scale = 95.3127 # km per deg longitude

Qs_1 = 800.0
Qs_2 = 400.0

lon_pattern_1 = np.concatenate((np.tile([Qs_1,Qs_1,Qs_2,Qs_2],25),[Qs_1]))
lon_pattern_2 = np.concatenate((np.tile([Qs_2,Qs_2,Qs_1,Qs_1],25),[Qs_2]))

lat_pattern_1 = np.concatenate((np.tile(np.concatenate((lon_pattern_1,lon_pattern_1,lon_pattern_2,lon_pattern_2)),12),lon_pattern_1,lon_pattern_1,lon_pattern_2))
lat_pattern_2 = np.concatenate((np.tile(np.concatenate((lon_pattern_2,lon_pattern_2,lon_pattern_1,lon_pattern_1)),12),lon_pattern_2,lon_pattern_2,lon_pattern_1))

big_box_lon = np.linspace(-75.5,-65.5,101)
big_box_lat = np.linspace(-34.0,-29.0,51)
big_box_dep = np.linspace(-566.5,386.5,954)

z,y,x = np.meshgrid(big_box_dep,big_box_lat,big_box_lon,indexing='ij')

lon = x.flatten()
lat = y.flatten()
dep = z.flatten()

big_box_grid = np.concatenate((lon.reshape((len(lon),1)),lat.reshape((len(lat),1)),dep.reshape((len(dep),1))),axis=1)

count = 0
final_big_grid = np.array([])
for dep in big_box_dep:
    if count < 20:
        final_big_grid = np.concatenate((final_big_grid,lat_pattern_1))
    else:
        final_big_grid = np.concatenate((final_big_grid,lat_pattern_2))
    
    if count < 40:
        count = count + 1
    else:
        count = 0

box_plus_q = np.concatenate((big_box_grid,final_big_grid.reshape((len(final_big_grid),1))),axis=1)

x_section = box_plus_q[box_plus_q[:,1] == -31.0]
print(np.shape(x_section[:,0]))
x_section_x = x_section[:,0].reshape(954,101)
x_section_y = x_section[:,2].reshape(954,101)
x_section_z = x_section[:,3].reshape(954,101)

fig1, ax1 = plt.subplots()

b = ax1.pcolormesh(x_section_x, x_section_y, x_section_z, cmap='RdBu',shading='nearest')
ax1.axis([x_section[:,0].min(), x_section[:,0].max(), x_section[:,2].min(), x_section[:,2].max()])
fig1.colorbar(b, ax=ax1)

plt.show()

#np.savetxt('./box_plus_q.txt',box_plus_q,fmt=['%5.1f','%5.1f','%6.1f','%5.1f'])

# Perform rotation
box_plus_q[:,0] = (box_plus_q[:,0] - (-75.5))*lon_scale
box_plus_q[:,1] = (box_plus_q[:,1] - (-34.0))*lat_scale

rot_vector = np.array([0,1,0])*np.deg2rad(22.8)
Rot = Rotation.from_rotvec(rot_vector)
rot_apply = Rot.apply(box_plus_q[:,0:3])
rot_apply[:,0] = (rot_apply[:,0]/lon_scale) + (-75.5)
rot_apply[:,1] = (rot_apply[:,1]/lat_scale) + (-34.0)
print(rot_apply[:,0],rot_apply[:,1],rot_apply[:,2])

rot_box_plus_q = np.concatenate((rot_apply,box_plus_q[:,3].reshape(len(box_plus_q[:,3]),1)),axis=1)
print(len(np.where((rot_box_plus_q[:,0] <= -68.0) & (rot_box_plus_q[:,0] >= -73.0))[0]))
# rot_box_plus_q = rot_box_plus_q[np.where((rot_box_plus_q[:,0] <= -67.95) & (rot_box_plus_q[:,0] >= -73.05))[0],:]
# rot_box_plus_q = rot_box_plus_q[np.where((rot_box_plus_q[:,1] <= -29.0) & (rot_box_plus_q[:,1] >= -34.0))[0],:]
# rot_box_plus_q = rot_box_plus_q[np.where((rot_box_plus_q[:,2] <= 0.5) & (rot_box_plus_q[:,2] >= -180.5))[0],:]

x_section = rot_box_plus_q[rot_box_plus_q[:,1] == -31.6]
x_section_x = x_section[:,0].reshape(954,101)
x_section_y = x_section[:,2].reshape(954,101)
x_section_z = x_section[:,3].reshape(954,101)

fig2, ax2 = plt.subplots()

c = ax2.pcolormesh(x_section_x, x_section_y, x_section_z, cmap='RdBu',shading='nearest')
ax2.axis([x_section[:,0].min(), x_section[:,0].max(), x_section[:,2].min(), x_section[:,2].max()])
fig2.colorbar(c, ax=ax2)
plt.xlim(-73.0,-68.0)
plt.ylim(-180.0,10.0)

plt.show()

#np.savetxt('./rot_box_plus_q.txt',rot_box_plus_q,fmt=['%5.1f','%5.1f','%6.1f','%5.1f'])