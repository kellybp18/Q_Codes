# Code to plot the slab interface resolution test in GMT. For the high Q bar structure, set
# qs_model = pd.read_csv(data_dir + 'qs_model_bar.csv') and 
# qs_synth_model = np.concatenate(((1/300)*np.ones(6762),(1/900)*np.ones(11270),(1/300)*np.ones(72128))).
#
# For the low Q bar structure, set
# qs_model = pd.read_csv(data_dir + 'qs_model_inverted_bar.csv') and
# qs_synth_model = np.concatenate(((1/900)*np.ones(6762),(1/300)*np.ones(11270),(1/900)*np.ones(72128)))

import numpy as np
import pygmt
import pandas as pd
import os
import time

map_coords = np.array([-73.0,-68.0,-34.0,-29.0])
data_dir = '/Volumes/External/Resolution_Tests/Latbox_49_Lonbox_46_Depbox_40/'

# Set up area
latmin = -33.0
latmax = -29.5
lonmin = -73.0
lonmax = -69.0
depmin = 10
depmax = -72

# Illapel Mw 8.5 coords
main_shock_lon = -71.67
main_shock_lat = -31.57
main_shock_dep = -20.7

# Read in necessary files
qs_model = pd.read_csv(data_dir + 'qs_model_inverted_bar.csv')
slab_contours = pd.read_csv(data_dir + 'Figures/interface_contours.csv',sep=',',names=['lon','lat','dep'])
eq_database = pd.read_csv('/Volumes/External/Attenuation/q_database.csv')
qs_initial = 450.0
qs_synth_model = np.concatenate(((1/900)*np.ones(6762),(1/300)*np.ones(11270),(1/900)*np.ones(72128))) #np.loadtxt(data_dir + 'm0_synth.txt')

# Find boxes directly above each point along each depth contour
# from 0 - 80 km depth, save their Qs value, and calculate distance along
# the fault surface for that point relative to the projection of the main
# shock onto the interface
interface = pd.DataFrame({'dist_along_strike':[],'slab_depth':[],'Qs':[],'lon':[],'lat':[],'box_num':[]})

for row in range(len(slab_contours)):
    lon=slab_contours['lon'][row]
    lat=slab_contours['lat'][row]
    dep=slab_contours['dep'][row]

    unique_lons = np.unique(qs_model['lon'])
    unique_lats = np.unique(qs_model['lat'])
    unique_deps = np.unique(qs_model['dep'])
    if dep < -3.0:
        unique_deps = unique_deps[np.where(unique_deps >= dep)]

    find_lon = unique_lons[np.argmin(np.abs(lon - unique_lons))]
    find_lat = unique_lats[np.argmin(np.abs(lat - unique_lats))]
    find_dep = unique_deps[np.argmin(np.abs(dep - unique_deps))]
    find_q = qs_model.loc[(qs_model['lon'] == find_lon) & (qs_model['lat'] == find_lat) & (qs_model['dep'] == find_dep),'Qs'].values[0]
    find_boxnum = int(qs_model.loc[(qs_model['lon'] == find_lon) & (qs_model['lat'] == find_lat) & (qs_model['dep'] == find_dep),'box_num'].values[0])

    if find_q > 1500.0:
        find_q = 1500.0
    elif find_q > 0.0 and find_q < 75.0:
        find_q = 75.0

    contour_points = slab_contours[slab_contours['dep'] == dep]
    mainshock_ref_lon = (contour_points['lon'][contour_points['lat'] == -31.6].values[0] - contour_points['lon'][contour_points['lat'] == -31.5].values[0])*(-0.3) \
                         + contour_points['lon'][contour_points['lat'] == -31.6].values[0]
    if lat < main_shock_lat:
        points = contour_points[(contour_points['lat'] < main_shock_lat) & (contour_points['lat'] >= lat)].append({'lon':mainshock_ref_lon,'lat':main_shock_lat,'dep':dep},ignore_index=True)
        dist = np.sum(np.sqrt((np.diff(points['lon'])*95.31)**2 + np.diff((points['lat'])*111.1)**2))*-1 #in km
    elif lat > main_shock_lat:
        points = pd.concat([pd.DataFrame({'lon':mainshock_ref_lon,'lat':main_shock_lat,'dep':dep},index=[0]),contour_points[(contour_points['lat'] > main_shock_lat) & (contour_points['lat'] <= lat)]]).reset_index(drop=True)
        dist = np.sum(np.sqrt((np.diff(points['lon'])*95.31)**2 + np.diff((points['lat'])*111.1)**2)) #in km
    
    interface = interface.append({'dist_along_strike': dist, 'slab_depth': dep, 'Qs': find_q, 'lon': lon, 'lat': lat, 'box_num': find_boxnum},ignore_index=True)

interface.to_csv(data_dir + 'Figures/interface_qs.csv',index=False)

# Perform masking of the interface figure Qs distribution where there is no data
os.system(('gmt blockmean ' + data_dir + 'Figures/interface_qs.csv -R-170.0/250.0/-80.0/0.0 -I1.25/0.125 >  ' + data_dir + 'Figures/interfacemaskmed.xyz'))
time.sleep(3)
os.system(('gmt surface ' + data_dir + 'Figures/interfacemaskmed.xyz -G' + data_dir + 'Figures/interfacemaskmed.grd -I1.25/0.125 -Lu1500.0 -R-170.0/250.0/-80.0/0.0 -Tb1i0'))
time.sleep(5)
os.system(('gmt grdclip ' + data_dir + 'Figures/interfacemaskmed.grd -G' + data_dir + 'Figures/interfacemaskclip.grd -Sb75.0/NaN'))
time.sleep(5)

interface.loc[(interface['Qs'] == 0.0),'Qs'] = qs_initial
interface.to_csv(data_dir + 'Figures/interface_qs_w_init_model.csv',index=False)

os.system(('gmt blockmean ' + data_dir + 'Figures/interface_qs_w_init_model.csv -R-170.0/250.0/-80.0/0.0 -I1.25/0.125 >  ' + data_dir + 'Figures/interfacesurfmed.xyz'))
time.sleep(3)
os.system(('gmt surface ' + data_dir + 'Figures/interfacesurfmed.xyz -G' + data_dir + 'Figures/interfacesurfmed.grd -I1.25/0.125 -Lu1500.0 -R-170.0/250.0/-80.0/0.0 -Tb1i0'))
time.sleep(5)
os.system(('gmt grdmath ' + data_dir + 'Figures/interfacesurfmed.grd ' + data_dir + 'Figures/interfacemaskclip.grd OR = ' + data_dir + 'Figures/interfacemasksurfmed.grd'))
time.sleep(3)
print("Okay")

# Create interface figure
fig2 = pygmt.Figure()
pygmt.grdclip((data_dir + 'Figures/interfacemasksurfmed.grd'),
            outgrid=(data_dir + 'Figures/interfacesurfclip.grd'),
            below=[75,75.0])
fig2.grdimage((data_dir + 'Figures/interfacesurfclip.grd'),
            cmap=data_dir + 'Figures/qs_surf.cpt',
            projection='x0.03/0.075',
            region=[-125.0,230.0,-80.0,-15.0],
            interpolation='n')
fig2.grdcontour(grid=(data_dir + 'Figures/interfacesurfclip.grd'),
            interval=200,
            annotation="400+f5p",
            projection='x0.03/0.075',
            region=[-125.0,230.0,-80.0,-15.0],
            pen='0.23,black')
fig2.basemap(projection='x0.03/0.075',
            region=[-125.0,230.0,-80.0,-15.0],
            frame=['WSte','xa50f25+l"Distance Along Strike (km)"','ya10f5+l"Slab Depth (km)"'],
            )
fig2.basemap(projection='x3.33/0.075',
            region=[-32.7,-29.5,-80.0,-15.0],
            frame=['lbNr','xa1f0.5+l"Latitude (deg)"'])
fig2.colorbar(frame=['xc' + data_dir + 'Figures/cbar_annots.txt+LQs'],
                cmap=data_dir + 'Figures/qs.cpt',
                position='JMR+o0.5c/0c+w4.92c/0.4c+n"No Data"')
fig2.savefig((data_dir + 'Figures/interface_res_test.png'))

interface_boxnums = np.array(interface['box_num'])

fig4 = pygmt.Figure()
pygmt.xyz2grd(x=np.ascontiguousarray(interface['lat']),
            y=np.ascontiguousarray(interface['slab_depth']),
            z=1/qs_synth_model[interface_boxnums.astype(int)],
            outgrid = (data_dir + 'Figures/Q_synth_interface.grd'),
            region=[-32.7,-29.5,-80.0,-15.0],
            spacing=(str(0.102)+'+e/'+str(1.0)+'+e'))
fig4.grdimage((data_dir + 'Figures/Q_synth_interface.grd'),
            cmap=data_dir + 'Figures/qs.cpt',
            projection='x3.33/0.075',
            region=[-32.7,-29.5,-80.0,-15.0],
            interpolation='n')
fig4.basemap(projection='x0.03/0.075',
            region=[-125.0,230.0,-80.0,-15.0],
            frame=['WSte','xa50f25+l"Distance Along Strike (km)"','ya10f5+l"Slab Depth (km)"'],
            )
fig4.basemap(projection='x3.33/0.075',
            region=[-32.7,-29.5,-80.0,-15.0],
            frame=['lbNr','xa1f0.5+l"Latitude (deg)"'])
fig4.colorbar(frame=['xc' + data_dir + 'Figures/cbar_annots.txt+LQs'],
                cmap=data_dir + 'Figures/qs.cpt',
                position='JMR+o0.5c/0c+w4.92c/0.4c+n"No Data"')
fig4.savefig((data_dir + 'Figures/interface_synth_slice.png'))