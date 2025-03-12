# Code to plot the slab interface figure in GMT

import numpy as np
import pygmt
import pandas as pd
import os
import time

map_coords = np.array([-73.0,-68.0,-34.0,-29.0])
data_dir = '/Volumes/External/Tomography/'

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
qs_model = pd.read_csv(data_dir + 'qs_model.csv')
slab_contours = pd.read_csv(data_dir + 'Figures/interface_contours.csv',sep=',',names=['lon','lat','dep'])
rad_pattern = pd.read_csv(data_dir + 'Figures/rupture_radiation_track.txt',sep=' ',names=['lon','lat'])
eq_database = pd.read_csv('/Volumes/External/Attenuation/q_database.csv')
qs_initial = 450.0

# Find boxes directly above each point along each depth contour
# from 0 - 80 km depth, save their Qs value, and calculate distance along
# the fault surface for that point relative to the projection of the main
# shock onto the interface
interface = pd.DataFrame({'dist_along_strike':[],'slab_depth':[],'Qs':[],'lon':[],'lat':[]})

for row in range(len(slab_contours)):
    lon=slab_contours['lon'][row]
    lat=slab_contours['lat'][row]
    dep=slab_contours['dep'][row]

    unique_lons = np.unique(qs_model['lon'])
    unique_lats = np.unique(qs_model['lat'])
    unique_deps = np.unique(qs_model['dep'])

    # The purpose of this if is to ensure that the box closest to the point
    # on the slab contour is the box just above the interface, not below,
    # so that we don't capture high Qs from the slab which might be 
    # mistake for a high Qs anomaly on the interface.
    if dep < -3.0:
        unique_deps = unique_deps[np.where(unique_deps >= dep)]

    find_lon = unique_lons[np.argmin(np.abs(lon - unique_lons))]
    find_lat = unique_lats[np.argmin(np.abs(lat - unique_lats))]
    find_dep = unique_deps[np.argmin(np.abs(dep - unique_deps))]
    find_q = qs_model.loc[(qs_model['lon'] == find_lon) & (qs_model['lat'] == find_lat) & (qs_model['dep'] == find_dep),'Qs'].values[0]
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
    
    interface = interface.append({'dist_along_strike': dist, 'slab_depth': dep, 'Qs': find_q, 'lon': lon, 'lat': lat},ignore_index=True)

interface.to_csv(data_dir + 'Figures/interface_qs.csv',index=False)

# Calculate distance along fault surface for coords of the Okuwaki 2016 radiation pattern track
# and project onto the interface

interface_rad_pattern = pd.DataFrame({'dist_along_strike':[],'slab_depth':[]})
for coord in range(len(rad_pattern)):
    rad_lon = rad_pattern['lon'][coord]
    rad_lat = rad_pattern['lat'][coord]

    slab_lons = np.array(interface['lon'])
    slab_lats = np.array(interface['lat'])

    find_coord_index = np.argmin(np.abs(rad_lon - slab_lons) + np.abs(rad_lat - slab_lats))
    rad_dist = interface['dist_along_strike'][find_coord_index]
    rad_dep = interface['slab_depth'][find_coord_index]

    print(interface['lon'][find_coord_index],interface['lat'][find_coord_index],rad_dist,rad_dep)
    
    interface_rad_pattern = interface_rad_pattern.append({'dist_along_strike': rad_dist, 'slab_depth': rad_dep},ignore_index=True)

interface_rad_pattern.to_csv(data_dir + 'Figures/interface_rad_pattern.csv',index=False)

# Create csv of aftershock location data within 10 km of the interface, and two more split by early vs late origin date
eq_database_interface = eq_database[eq_database['ev_dep'] <= 80.0].reset_index(drop=True)
interface_eqs = pd.DataFrame({'eq_lat':[],'eq_depth':[]})
interface_eqs_early = pd.DataFrame({'eq_lat':[],'eq_depth':[]})
interface_eqs_late = pd.DataFrame({'eq_lat':[],'eq_depth':[]})
for eq in np.unique(eq_database_interface['ev_id']):
    eq_lat = eq_database_interface.loc[(eq_database_interface['ev_id'] == eq),'ev_lat'].values[0]
    eq_lon = eq_database_interface.loc[(eq_database_interface['ev_id'] == eq),'ev_lon'].values[0]
    eq_dep = eq_database_interface.loc[(eq_database_interface['ev_id'] == eq),'ev_dep'].values[0]
    eq_date = int(eq[0:5])
    print(eq_lon,eq_lat,eq_dep,eq_date)

    find_coord_index = np.argmin(np.abs(eq_lon - slab_lons) + np.abs(eq_lat - slab_lats))
    eq_dist = interface['dist_along_strike'][find_coord_index]
    eq_slab_dep = interface['slab_depth'][find_coord_index]

    if np.abs(eq_slab_dep - (-1*eq_dep)) <= 10.0:
        interface_eqs = interface_eqs.append({'eq_lat': eq_lat, 'eq_depth': eq_slab_dep},ignore_index=True)
        if eq_date < 15350:
            interface_eqs_early = interface_eqs_early.append({'eq_lat':eq_lat,'eq_depth':eq_slab_dep},ignore_index=True)
        else:
            interface_eqs_late = interface_eqs_late.append({'eq_lat':eq_lat,'eq_depth':eq_slab_dep},ignore_index=True)
    else:
        continue

interface_eqs.to_csv(data_dir + 'Figures/interface_eqs.csv',index=False)
interface_eqs_early.to_csv(data_dir + 'Figures/interface_eqs_early.csv',index=False)
interface_eqs_late.to_csv(data_dir + 'Figures/interface_eqs_late.csv',index=False)

# Create slab contour figure to assess correctness (Hayes et al)
fig = pygmt.Figure()
fig.grdcontour(grid='/Users/bpk/Documents/AGU_2021/Illapel_Slab2_Surface.grd',
               interval=5,
               annotation=20,
               projection='m3.5c',
               region=[lonmin,lonmax,latmin,latmax])
fig.basemap(projection='m3.5c',
            region=[lonmin,lonmax,latmin,latmax],
            frame=['WSNe','a1f0.5'],
            )
fig.coast(projection='m3.5c',
              region=[lonmin,lonmax,latmin,latmax],
              borders='1/thick,black',
              shorelines='thick,black'
              )
fig.plot(data='/Users/bpk/Documents/BPK_Masters_2019/Illapel_Events/main_shock.loc',
                projection='m3.5c',
                region=[lonmin,lonmax,latmin,latmax],
                style='a0.2',
                color='yellow',
                pen='0.1p,black',
                incols=[1,0]
                )
fig.plot(data=(data_dir+'Figures/rupture_radiation_track.txt'),
                projection='m3.5c',
                region=[lonmin,lonmax,latmin,latmax],
                pen='thick,red'
                )
fig.savefig((data_dir + 'Figures/slab_fig.png'))

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

# Calculate distance along fault surface for coords of the Okuwaki 2016 time windowed
# radiation pattern contours
for t in np.array([[0,5],[6,10],[11,15],[16,20],[21,25],[26,30],[31,35],[36,40],[41,45], \
                   [46,50],[51,55],[56,60],[61,65],[66,70],[71,75],[76,80],[81,85],[-1,-1],[-2,-2]],dtype=int):
    contour_rad_pattern = pd.DataFrame({'lat':[],'slab_depth':[]})

    t1 = t[0]
    t2 = t[1]
    if t1 == -1 and t2 == -1:
        time_window = pd.read_csv(data_dir+'Figures/okuwaki_rad_pattern/total_highmag_rad.gmt',sep = ', ',names=['lon','lat'])
    elif t1 == -2 and t2 == -2:
        print('Do Nothing')
    else:
        time_window = pd.read_csv(data_dir+'Figures/okuwaki_rad_pattern/' + str(t1) + '-' + str(t2) + '_sec.gmt',sep = ', ',names=['lon','lat'])
    
    for contour in range(len(time_window)):
        contour_lon = time_window['lon'][contour]
        contour_lat = time_window['lat'][contour]

        if str(contour_lon) == 'n':
            contour_rad_pattern = contour_rad_pattern.append({'lat': '>', 'slab_depth': ''},ignore_index=True)
        else:
            contour_lon = float(contour_lon)
            contour_lat = float(contour_lat)
            find_coord_index = np.argmin(np.abs(contour_lon - slab_lons) + np.abs(contour_lat - slab_lats))
            #rad_dist = interface['dist_along_strike'][find_coord_index]
            rad_dep = interface['slab_depth'][find_coord_index]
            #print(rad_dist,rad_dep)
            contour_rad_pattern = contour_rad_pattern.append({'lat': contour_lat, 'slab_depth': rad_dep},ignore_index=True)
    print(contour_rad_pattern)
    if t1 == -1 and t2 == -1:
        contour_rad_pattern.to_csv(data_dir + 'Figures/okuwaki_rad_pattern/total_highmag_rad.csv',index=False)
    elif t1 == -2 and t2 == -2:
        print('Do Nothing')
    else:
        contour_rad_pattern.to_csv(data_dir + 'Figures/okuwaki_rad_pattern/'+str(t1) + '-' + str(t2) + '_sec.csv',index=False)

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
    fig2.plot(x=np.array([0.0]),
                y=np.array([-31.0]),
                projection='x0.03/0.075',
                region=[-125.0,230.0,-80.0,-15.0],
                style='a0.3',
                color='yellow',
                pen='0.1p,black'
                )
    # fig2.plot(data=(data_dir+'Figures/interface_rad_pattern.csv'),
    #             projection='x0.02/0.06',
    #             region=[-125.0,250.0,-80.0,-15.0],
    #             pen='thick,red'
    #             )
    if t1 == -1 and t2 == -1:
        fig2.plot(data=(data_dir + 'Figures/okuwaki_rad_pattern/total_highmag_rad.csv'),
                projection='x3.33/0.075',
                region=[-32.7,-29.5,-80.0,-15.0],
                color='red',
                transparency=50
                )
        fig2.plot(data=(data_dir + 'Figures/okuwaki_rad_pattern/total_highmag_rad.csv'),
                projection='x3.33/0.075',
                region=[-32.7,-29.5,-80.0,-15.0],
                pen='0.5p,black',
                )
        fig2.plot(x=np.array([0.0]),
                y=np.array([-31.0]),
                projection='x0.03/0.075',
                region=[-125.0,230.0,-80.0,-15.0],
                style='a0.3',
                color='yellow',
                pen='0.1p,black'
                )
    elif t1 == -2 and t2 == -2:
        print('Do Nothing')
    else:
        fig2.plot(data=(data_dir + 'Figures/okuwaki_rad_pattern/'+str(t1) + '-' + str(t2) + '_sec.csv'),
                    projection='x3.33/0.075',
                    region=[-32.7,-29.5,-80.0,-15.0],
                    pen='thick,white'
                    )
    fig2.basemap(projection='x3.33/0.075',
                region=[-32.7,-29.5,-80.0,-15.0],
                frame=['lbNr','xa1f0.5+l"Latitude (deg)"'])
    fig2.colorbar(frame=['xc' + data_dir + 'Figures/cbar_annots.txt+LQs'],
                    cmap=data_dir + 'Figures/qs.cpt',
                    position='JMR+o0.5c/0c+w4.92c/0.4c+n"No Data"')
    if t1 == -1 and t2 == -1:
        fig2.savefig((data_dir + 'Figures/interface_total_highmag_rad.png'))
    elif t1 == -2 and t2 == -2:
        fig2.savefig((data_dir + 'Figures/interface.png'))
    else:
        fig2.savefig((data_dir + 'Figures/interface_'+ str(t1) + '-' + str(t2) +'.png'))

# Create interface figure with finite fault vectors
fig3 = pygmt.Figure()
pygmt.grdclip((data_dir + 'Figures/interfacemasksurfmed.grd'),
            outgrid=(data_dir + 'Figures/interfacesurfclip.grd'),
            below=[75,75.0])
fig3.grdimage((data_dir + 'Figures/interfacesurfclip.grd'),
            cmap=data_dir + 'Figures/qs_surf.cpt',
            projection='x0.03/0.075',
            region=[-125.0,230.0,-80.0,-15.0],
            interpolation='n')
# fig3.grdcontour(grid=(data_dir + 'Figures/interfacesurfclip.grd'),
#             interval=200,
#             annotation="400+f5p",
#             projection='x0.02/0.06',
#             region=[-125.0,250.0,-80.0,-15.0],
#             pen='0.23,black')
fig3.basemap(projection='x0.03/0.075',
            region=[-125.0,230.0,-80.0,-15.0],
            frame=['WSte','xa50f25+l"Distance Along Strike (km)"','ya10f5+l"Slab Depth (km)"'],
            )
fig3.basemap(projection='x3.33/0.075',
            region=[-32.7,-29.5,-80.0,-15.0],
            frame=['lbNr','xa1f0.5+l"Latitude (deg)"'])
fig3.plot(data=(data_dir + 'Figures/finite_fault/slip_contours.csv'),
            projection='x0.03/0.075',
            region=[-125.0,230.0,-80.0,-15.0],
            color='purple',
            transparency=80
            )
fig3.contour(data=(data_dir + 'Figures/finite_fault/rake_and_slip_data.csv'),
            projection='x0.03/0.075',
            region=[-125.0,230.0,-80.0,-15.0],
            levels='0.2+0.2',
            pen='0.7p,purple',
            incols="0:1,3+d7.9833",
            )
fig3.plot(data=(data_dir + 'Figures/finite_fault/rake_and_slip_data.csv'),
            projection='x0.03/0.075',
            region=[-125.0,230.0,-80.0,-15.0],
            style='v0.15c+e',
            pen='0.3p,black',
            color='white',
            incols="0:2,3+d7.9833"
            )
fig3.plot(x=np.array([0.0]),
            y=np.array([-31.0]),
            projection='x0.03/0.075',
            region=[-125.0,230.0,-80.0,-15.0],
            style='a0.3',
            color='yellow',
            pen='0.1p,black'
            )
fig3.colorbar(frame=['xc' + data_dir + 'Figures/cbar_annots.txt+LQs'],
                cmap=data_dir + 'Figures/qs.cpt',
                position='JMR+o0.5c/0c+w4.92c/0.4c+n"No Data"')
fig3.savefig((data_dir + 'Figures/interface_finite_fault.png'))

# Create interface figures with aftershock seismicity within 10.0 km of the slab, and two more divided by origin date
time_file_strs = ['','_early','_late']
eq_colors = ['white','blanchedalmond','plum']
for idx,timestr in enumerate(time_file_strs):
    fig4 = pygmt.Figure()
    pygmt.grdclip((data_dir + 'Figures/interfacemasksurfmed.grd'),
                outgrid=(data_dir + 'Figures/interfacesurfclip.grd'),
                below=[75,75.0])
    fig4.grdimage((data_dir + 'Figures/interfacesurfclip.grd'),
                cmap=data_dir + 'Figures/qs_surf.cpt',
                projection='x0.03/0.075',
                region=[-125.0,230.0,-80.0,-15.0],
                interpolation='n')
    fig4.grdcontour(grid=(data_dir + 'Figures/interfacesurfclip.grd'),
                interval=200,
                annotation="400+f5p",
                projection='x0.03/0.075',
                region=[-125.0,230.0,-80.0,-15.0],
                pen='0.23,black')
    fig4.basemap(projection='x0.03/0.075',
                region=[-125.0,230.0,-80.0,-15.0],
                frame=['WSte','xa50f25+l"Distance Along Strike (km)"','ya10f5+l"Slab Depth (km)"'],
                )
    fig4.basemap(projection='x3.33/0.075',
                region=[-32.7,-29.5,-80.0,-15.0],
                frame=['lbNr','xa1f0.5+l"Latitude (deg)"'])
    fig4.plot(data=(data_dir + 'Figures/interface_eqs' + timestr + '.csv'),
                projection='x3.33/0.075',
                region=[-32.7,-29.5,-80.0,-15.0],
                style='c0.1',
                pen='0.2p,black',
                color=eq_colors[idx],
                )
    fig4.plot(x=np.array([0.0]),
                y=np.array([-31.0]),
                projection='x0.03/0.075',
                region=[-125.0,230.0,-80.0,-15.0],
                style='a0.3',
                color='yellow',
                pen='0.2p,black'
                )
    fig4.colorbar(frame=['xc' + data_dir + 'Figures/cbar_annots.txt+LQs'],
                    cmap=data_dir + 'Figures/qs.cpt',
                    position='JMR+o0.5c/0c+w4.92c/0.4c+n"No Data"')
    fig4.savefig((data_dir + 'Figures/interface_seismicity' + timestr + '.png'))