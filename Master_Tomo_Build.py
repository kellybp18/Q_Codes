import numpy as np
import numpy.linalg as linalg
import scipy.optimize as sciop
import pandas as pd
import re

# DEFINE GRID
LAT_NORTH = -29.0
LAT_SOUTH = -34.0
LEN_LAT = 5.0 # degrees
Nblocks_lat = 27
LAT_INT = LEN_LAT/Nblocks_lat

LON_WEST = -73.0
LON_EAST = -68.0
LEN_LON = 5.0 # degrees
Nblocks_lon = 46
LON_INT = LEN_LON/Nblocks_lon

DEP_TOP = 0.0
DEP_BOT = -180.0
LEN_DEP = 180.0 # km
Nblocks_dep = 20
DEP_INT = LEN_DEP/Nblocks_dep

NBLOCKS=Nblocks_lat*Nblocks_lon*Nblocks_dep

latkm=LAT_INT*111.1949 # km per box
lonkm=LON_INT*95.3127 # km per box

RADIUS = 6371 # km

latrange = np.linspace(-34,-29,Nblocks_lat+1)
lonrange = np.linspace(-73,-68,Nblocks_lon+1)
deprange = np.linspace(0,-180,Nblocks_dep+1)

print('Total boxes in latitude direction:', Nblocks_lat)
print('Latitudes divided into increments of', LAT_INT,'degrees')
print('Latitudes divided into increments of', latkm, 'km')
print('Total boxes in longitude direction:', Nblocks_lon)
print('Longitude divided into increments of', LON_INT, 'degrees')
print('Longitudes divided into increments of', lonkm, 'km')
print('Total boxes in depth direction:', Nblocks_dep)
print('Depth divided into increments of', DEP_INT, 'km')
print('TOTAL NUMBER OF BOXES:', NBLOCKS)

# SET VALUES FOR NORM DAMPING AND GAMMA (Qp/Qs)
normd=500
GAMMA=1.6

# # CREATE TOMO BOX DATAFRAME (Uncomment block if you need to create it)
# boxpt = pd.DataFrame({'box_num':[],'lon_min':[],'lon_max':[],'lat_min':[],'lat_max':[],'dep_min':[], \
#                       'dep_max':[],'phi_degmin':[],'phi_degmax':[],'theta_degmin':[],'theta_degmax':[],'R_min':[], \
#                       'R_max':[],'phi_radmin':[],'phi_radmax':[],'theta_radmin':[],'theta_radmax':[]})

# boxnum = 1

# # For R, theta and phi, min and max vars correspond to the cartesian vars
# # they were converted from. Example: rmin = depmin + RADIUS, rmax = depmax + RADIUS
# # even though rmin would actually be greater than rmax since depths are negative.

# # Increment depth from top to bottom
# for i,dep in enumerate(deprange[:-1]):
#     depmin = dep
#     depmax = deprange[i+1]
#     rmin = depmin + RADIUS
#     rmax = depmax + RADIUS
#     # Increment latitude from north to south
#     for j,lat in enumerate(latrange[:-1]):
#         latmin = lat
#         latmax = latrange[j+1]
#         theta_dmin = 90 - latmin
#         theta_dmax = 90 - latmax
#         theta_rmin = np.deg2rad(theta_dmin)
#         theta_rmax = np.deg2rad(theta_dmax)
#         # Increment longitude from west to east
#         for k,lon in enumerate(lonrange[:-1]):
#             lonmin = lon
#             lonmax = lonrange[k+1]
#             phi_dmin = lonmin
#             phi_dmax = lonmax
#             phi_rmin = np.deg2rad(lonmin)
#             phi_rmax = np.deg2rad(lonmax)

#             assert (depmin > depmax) and (rmin > rmax)
#             assert (latmax > latmin) and (theta_dmin > theta_dmax)
#             assert (lonmax > lonmin) and (phi_dmax > phi_dmin)

#             boxpt = boxpt.append({'box_num':int(boxnum),'lon_min':lonmin,'lon_max':lonmax,'lat_min':latmin,'lat_max':latmax,'dep_min':depmin, \
#                       'dep_max':depmax,'phi_degmin':phi_dmin,'phi_degmax':phi_dmax,'theta_degmin':theta_dmin,'theta_degmax':theta_dmax,'R_min':rmin, \
#                       'R_max':rmax,'phi_radmin':phi_rmin,'phi_radmax':phi_rmax,'theta_radmin':theta_rmin,'theta_radmax':theta_rmax},ignore_index=True)

#             boxnum = boxnum + 1

# boxpt.to_csv('/Volumes/External/Tomography/boxpt.csv',index=False)
boxpt = pd.read_csv('/Volumes/External/Tomography/boxpt.csv')

# # CREATE VELOCITY MODEL MATRIX (uncomment block if you need to create it)
# velo_model = pd.DataFrame({'box_num':[],'p_velo':[],'s_velo':[],'num_pts_averaged':[]})

# p_velmod = pd.read_csv('/Users/bpk/Documents/BPK_Masters_2019/raytrace/Illapel_P_Velmod_New.csv',sep=',',dtype=float)
# s_velmod = pd.read_csv('/Users/bpk/Documents/BPK_Masters_2019/raytrace/Illapel_S_Velmod_New.csv',sep=',',dtype=float)

# p_velmod['vs'] = s_velmod['vs']
# # For each box in boxpt, average all points in the velocity models
# # that fit into the box dimensions.
# for bnum in boxpt['box_num']:
#     print('Working on box #',bnum,'in velo_model dataframe.')
#     dep_sort = p_velmod[(p_velmod['dep'] <= -1*boxpt['dep_max'][bnum-1]) & (p_velmod['dep'] >= -1*boxpt['dep_min'][bnum-1])]
#     lat_sort = dep_sort[(dep_sort['lat'] <= boxpt['lat_max'][bnum-1]) & (dep_sort['lat'] >= boxpt['lat_min'][bnum-1])]
#     lon_sort = lat_sort[(lat_sort['lon'] <= boxpt['lon_max'][bnum-1]) & (lat_sort['lon'] >= boxpt['lon_min'][bnum-1])]
#     totvelP = sum(lon_sort['vp'])
#     totvelS = sum(lon_sort['vs'])
#     vels_found = len(lon_sort['vp'])
#     avgP = totvelP/vels_found
#     avgS = totvelS/vels_found
#     velo_model = velo_model.append({'box_num':bnum,'p_velo':avgP,'s_velo':avgS,'num_pts_averaged':vels_found},ignore_index=True)

# velo_model.to_csv('/Volumes/External/Tomography/block_velo_model.csv',index=False)
velo_model = pd.read_csv('/Volumes/External/Tomography/block_velo_model.csv')

# # CREATE INITIAL Qs MODEL (uncomment block if you need to create it)
# m0 = np.zeros(len(boxpt['box_num']))

# init_qs_model = pd.read_csv('/Volumes/External/Tomography/Initial_Qs_Model.csv',sep=',',names=['Qlon_0','Qlat_0','Qdep_0','Q0'],dtype=float)

# # For each box in boxpt, average all points in the initial Q model
# # that fit into the box dimensions.
# for bnum in boxpt['box_num']:
#     bnum = int(bnum)
#     print('Working on box #',bnum,'in m0 array.')
#     dep_sort = init_qs_model[(init_qs_model['Qdep_0'] <= -1*boxpt['dep_max'][bnum-1]) & (init_qs_model['Qdep_0'] >= -1*boxpt['dep_min'][bnum-1])]
#     lat_sort = dep_sort[(dep_sort['Qlat_0'] <= boxpt['lat_max'][bnum-1]) & (dep_sort['Qlat_0'] >= boxpt['lat_min'][bnum-1])]
#     lon_sort = lat_sort[(lat_sort['Qlon_0'] <= boxpt['lon_max'][bnum-1]) & (lat_sort['Qlon_0'] >= boxpt['lon_min'][bnum-1])]
#     totQ = sum(lon_sort['Q0'])
#     numQs = len(lon_sort['Q0'])
#     avgQ = totQ/numQs
#     m0[bnum-1] = 1/avgQ

# np.savetxt('/Volumes/External/Tomography/m0.txt',m0)
m0 = np.loadtxt('/Volumes/External/Tomography/m0.txt')

# READ INPUT FILE; PREPARE T*, COVARIANCE T* (Cd), INVERSE COV T* (CdI), AND COORDS ARRAYS
all_rays = pd.read_csv('/Volumes/External/Attenuation/q_database.csv')
all_good_rays = pd.DataFrame(all_rays[all_rays['judge_result'] == 'GOOD'])
all_good_rays = all_good_rays.reset_index(drop=True)
assert len(all_good_rays) == 3852

t_star = all_good_rays['stacked_t_star']
std_t_star = all_good_rays['stdev_t_star']
var_t_star = std_t_star**2
Cd = np.zeros((len(t_star),len(t_star)))
CdI = np.zeros_like(Cd)
for n,var in enumerate(var_t_star):
    Cd[n,n] = var
    CdI[n,n] = 1/var

# # PREPARE COORDS ARRAY (uncomment block if you need to create it)
# event_list = np.unique(all_rays['ev_id'])
# assert len(event_list) == 708
# coords = pd.DataFrame({'ray_num':[],'lon':[],'lat':[],'dep':[],'box_num':[], \
#                       'R':[],'theta_deg':[],'theta_rad':[],'phi_deg':[], \
#                       'phi_rad':[],'X':[],'Y':[],'Z':[]})

# print(all_good_rays.head())
# # For each ray, find it's .gmt file, extract trabox coordinates, interpolate coordinates, populate COORDS array
# for o,event_id in enumerate(all_good_rays['ev_id']):
#     # Find GMT file
#     event_number = str(np.where(event_list == event_id)[0][0]+1)
#     station = all_good_rays['stn_id'][o]
#     rayfile = '/Users/bpk/Documents/BPK_Masters_2019/raytrace/Illapel_GMT_Files/E' + event_number + '-' + station + '.gmt'
#     print('Working on ray E' + event_number + '-' + station)
#     rayfile_list = open(rayfile,'r')

#     # Extract trabox coordinates
#     coord_list_lines = rayfile_list.read().splitlines()
#     coord_list_clean = [re.sub(' +',' ',s.strip()) for s in coord_list_lines]
#     coord_list_split = [t.split(' ') for t in coord_list_clean]
#     del coord_list_split[-1][3]
#     coord_array = np.array(coord_list_split,dtype=float)

#     # Interpolate
#     x = (coord_array[:,0] + 73)*95.31
#     y = (coord_array[:,1] + 34)*111.1949
#     z = coord_array[:,2]*-1
#     assert len(x) == len(y) == len(z)

#     data = np.array([x,y,z])
#     data = data.T

#     fit = np.polyfit(x,z,3)
#     x_new = np.linspace(x[0],x[-1],101)
#     z_new = np.polyval(fit,x_new)
#     z_new[-1] = 0.0
#     y_new = np.linspace(y[0],y[-1],101)

#     # Populate COORDS array
#     for p in range(len(x_new)):
#         lon_new = (x_new[p]/95.31) - 73
#         lat_new = (y_new[p]/111.1949) - 34
#         r_new = z_new[p] + RADIUS
#         thetad_new = 90 - lat_new
#         thetar_new = np.deg2rad(thetad_new)
#         phid_new = lon_new
#         phir_new = np.deg2rad(phid_new)
#         X_new = r_new*np.sin(thetar_new)*np.cos(phir_new)
#         Y_new = r_new*np.sin(thetar_new)*np.sin(phir_new)
#         Z_new = r_new*np.cos(thetar_new)
#         for q,bno in enumerate(boxpt['box_num']):
#             if boxpt['lon_min'][q] <= lon_new and lon_new <= boxpt['lon_max'][q] and \
#                boxpt['lat_min'][q] <= lat_new and lat_new <= boxpt['lat_max'][q] and \
#                boxpt['dep_max'][q] <= z_new[p] and z_new[p] <= boxpt['dep_min'][q]:
#                 coord_box = bno
#                 break
#         coords = coords.append({'ray_num':(o+1),'lon':lon_new,'lat':lat_new,'dep':z_new[p],'box_num':coord_box, \
#                                 'R':r_new,'theta_deg':thetad_new,'theta_rad':thetar_new,'phi_deg':phid_new, \
#                                 'phi_rad':phir_new,'X':X_new,'Y':Y_new,'Z':Z_new},ignore_index=True)

# coords.to_csv('/Volumes/External/Tomography/coords.csv',index=False)
coords = pd.read_csv('/Volumes/External/Tomography/coords.csv')

# # MAKE DIST ARRAY (uncomment block if you need to create it)
# dist = np.zeros((NBLOCKS,len(all_good_rays)))

# # Populate DIST array with ray segments in appropriate boxes
# for r in range(len(coords['ray_num'])-1):
#     ray1 = int(coords['ray_num'][r])
#     print('Working on ray #',ray1,'out of 3852.')
#     ray2 = int(coords['ray_num'][r+1])
#     box1 = int(coords['box_num'][r])
#     box2 = int(coords['box_num'][r+1])

#     # Check current point is inside its box
#     assert boxpt['lon_min'][box1-1] <= coords['lon'][r] and coords['lon'][r] <= boxpt['lon_max'][box1-1]
#     assert boxpt['lat_min'][box1-1] <= coords['lat'][r] and coords['lat'][r] <= boxpt['lat_max'][box1-1]
#     #print(boxpt['dep_max'][box1-1],coords['dep'][r],boxpt['dep_min'][box1-1])
#     assert boxpt['dep_max'][box1-1] <= coords['dep'][r] and coords['dep'][r] <= boxpt['dep_min'][box1-1]

#     # If points on same ray path
#     if ray1 == ray2:
#         Xpt1 = coords['X'][r]
#         Xpt2 = coords['X'][r+1]
#         Ypt1 = coords['Y'][r]
#         Ypt2 = coords['Y'][r+1]
#         Zpt1 = coords['Z'][r]
#         Zpt2 = coords['Z'][r+1]

#         # Get vector components and length
#         X_comp = Xpt2 - Xpt1
#         Y_comp = Ypt2 - Ypt1
#         Z_comp = Zpt2 - Zpt1
#         vector_len = np.sqrt(X_comp**2 + Y_comp**2 + Z_comp**2)

#         # If points are in same box
#         if box1 == box2:
#             dist[box1-1][ray1-1] = vector_len + dist[box1-1][ray1-1]
        
#         # If points are not in same box
#         elif box1 != box2:
#             # Get R, theta, phi bounds for box 1 and box 2
#             thetamin_b1 = boxpt['theta_degmin'][box1-1]
#             thetamax_b1 = boxpt['theta_degmax'][box1-1]
#             thetamin_b2 = boxpt['theta_degmin'][box2-1]
#             thetamax_b2 = boxpt['theta_degmax'][box2-1]
#             phimin_b1 = boxpt['phi_degmin'][box1-1]
#             phimax_b1 = boxpt['phi_degmax'][box1-1]
#             phimin_b2 = boxpt['phi_degmin'][box2-1]
#             phimax_b2 = boxpt['phi_degmax'][box2-1]
#             Rmin_b1 = boxpt['R_min'][box1-1]
#             Rmax_b1 = boxpt['R_max'][box1-1]
#             Rmin_b2 = boxpt['R_min'][box2-1]
#             Rmax_b2 = boxpt['R_max'][box2-1]

#             # Case 1: Ray crosses from box1 to box2 only in theta direction
#             if (thetamin_b1 != thetamin_b2) and (thetamax_b1 != thetamax_b2) and \
#                (phimin_b1 == phimin_b2) and (phimax_b1 == phimax_b2) and \
#                (Rmin_b1 == Rmin_b2) and (Rmax_b1 == Rmax_b2):
#                 d_theta = coords['theta_deg'][r+1] - coords['theta_deg'][r]
#                 if d_theta < 0:
#                     theta_ref = np.deg2rad(thetamax_b1)
#                 elif d_theta > 0:
#                     theta_ref = np.deg2rad(thetamin_b1)
#                 cos2 = np.cos(theta_ref)**2
#                 a_theta = cos2*(X_comp**2 + Y_comp**2 + Z_comp**2) - Z_comp**2
#                 b_theta = 2*(cos2*(Xpt1*X_comp + Ypt1*Y_comp + Zpt1*Z_comp) - Zpt1*Z_comp)
#                 c_theta = cos2*(Xpt1**2 + Ypt1**2 + Zpt1**2) - Zpt1**2
#                 x1 = (-1*b_theta + np.sqrt(b_theta**2 - 4*a_theta*c_theta))/(2*a_theta)
#                 x2 = (-1*b_theta - np.sqrt(b_theta**2 - 4*a_theta*c_theta))/(2*a_theta)
#                 x1 = round(x1*1000)/1000
#                 x2 = round(x2*1000)/1000
#                 if 0 <= x1 and x1 <= 1.0:
#                     ratio = x1
#                     d1 = vector_len*ratio
#                     d2 = vector_len*(1-ratio)
#                 elif 0 <= x2 and x2 <= 1.0:
#                     ratio = x2
#                     d1 = vector_len*ratio
#                     d2 = vector_len*(1-ratio)
#                 else:
#                     d1 = 0
#                     d2 = 0
#                 dist[box1-1][ray1-1] = d1 + dist[box1-1][ray1-1]
#                 dist[box2-1][ray1-1] = d2 + dist[box2-1][ray1-1]
            
#             # Case 2: Ray crosses from box1 to box2 only in phi direction
#             elif (thetamin_b1 == thetamin_b2) and (thetamax_b1 == thetamax_b2) and \
#                (phimin_b1 != phimin_b2) and (phimax_b1 != phimax_b2) and \
#                (Rmin_b1 == Rmin_b2) and (Rmax_b1 == Rmax_b2):
#                 d_phi = coords['phi_deg'][r+1] - coords['phi_deg'][r]
#                 if d_phi < 0:
#                     phi_ref = np.deg2rad(phimin_b1)
#                 elif d_phi > 0:
#                     phi_ref = np.deg2rad(phimax_b1)
#                 ratio = (Ypt1 - Xpt1*np.tan(phi_ref))/(X_comp*np.tan(phi_ref) - Y_comp)
#                 d1 = vector_len*ratio
#                 d2 = vector_len*(1-ratio)
#                 dist[box1-1][ray1-1] = d1 + dist[box1-1][ray1-1]
#                 dist[box2-1][ray1-1] = d2 + dist[box2-1][ray1-1]
            
#             # Case 3: Ray crosses from box1 to box2 only in R direction
#             elif (thetamin_b1 == thetamin_b2) and (thetamax_b1 == thetamax_b2) and \
#                (phimin_b1 == phimin_b2) and (phimax_b1 == phimax_b2) and \
#                (Rmin_b1 != Rmin_b2) and (Rmax_b1 != Rmax_b2):
#                 dR = coords['R'][r+1] - coords['R'][r]
#                 if dR > 0:
#                     r_ref = Rmin_b1
#                 elif dR < 0:
#                     r_ref = Rmax_b1
                
#                 if coords['R'][r] == r_ref and coords['R'][r+1] == r_ref-1:
#                     dist[box2-1,ray1-1] = vector_len + dist[box2-1,ray1-1]
#                 else:
#                     a_R = vector_len**2
#                     b_R = 2*Xpt1*X_comp + 2*Ypt1*Y_comp + 2*Zpt1*Z_comp
#                     c_R = -1*(r_ref**2) + Xpt1**2 + Ypt1**2 + Zpt1**2
#                     x1 = (-1*b_R + np.sqrt(b_R**2 - 4*a_R*c_R))/(2*a_R)
#                     x2 = (-1*b_R - np.sqrt(b_R**2 - 4*a_R*c_R))/(2*a_R)
#                     x1 = round(x1*1000)/1000
#                     x2 = round(x2*1000)/1000
#                     if 0 <= x1 and x1 <= 1.0:
#                         ratio = x1
#                         d1 = vector_len*ratio
#                         d2 = vector_len*(1-ratio)
#                     elif 0 <= x2 and x2 <= 1.0:
#                         ratio = x2
#                         d1 = vector_len*ratio
#                         d2 = vector_len*(1-ratio)
#                     else:
#                         d1 = 0
#                         d2 = 0
#                     dist[box1-1][ray1-1] = d1 + dist[box1-1][ray1-1]
#                     dist[box2-1][ray1-1] = d2 + dist[box2-1][ray1-1]

#             # Case 4: Ray crosses through 3 boxes in phi and R directions
#             elif (thetamin_b1 == thetamin_b2) and (thetamax_b1 == thetamax_b2) and \
#                (phimin_b1 != phimin_b2) and (phimax_b1 != phimax_b2) and \
#                (Rmin_b1 != Rmin_b2) and (Rmax_b1 != Rmax_b2):
#                 dR = coords['R'][r+1] - coords['R'][r]
#                 if dR > 0:
#                     r_ref = Rmin_b1
#                 elif dR < 0:
#                     r_ref = Rmax_b1
#                 d_phi = coords['phi_deg'][r+1] - coords['phi_deg'][r]
#                 if d_phi < 0:
#                     phi_ref = np.deg2rad(phimin_b1)
#                 elif d_phi > 0:
#                     phi_ref = np.deg2rad(phimax_b1)
#                 xp = (Ypt1 - Xpt1*np.tan(phi_ref))/(X_comp*np.tan(phi_ref) - Y_comp)
#                 a_R = vector_len**2
#                 b_R = 2*Xpt1*X_comp + 2*Ypt1*Y_comp + 2*Zpt1*Z_comp
#                 c_R = -1*(r_ref**2) + Xpt1**2 + Ypt1**2 + Zpt1**2
#                 xr1 = (-1*b_R + np.sqrt(b_R**2 - 4*a_R*c_R))/(2*a_R)
#                 xr2 = (-1*b_R - np.sqrt(b_R**2 - 4*a_R*c_R))/(2*a_R)
#                 xr1 = round(xr1*1000)/1000
#                 xr2 = round(xr2*1000)/1000
#                 if 0 <= xr1 and xr1 <= 1.0:
#                     xr = xr1
#                 elif 0 <= xr2 and xr2 <= 1.0:
#                     xr = xr2
#                 if xr < xp:
#                     largeRatio = xp
#                     smallRatio = xr
#                 elif xp < xr:
#                     largeRatio = xr
#                     smallRatio = xp
#                 cross_1x = Xpt1 + smallRatio*X_comp
#                 cross_1y = Ypt1 + smallRatio*Y_comp
#                 cross_1z = Zpt1 + smallRatio*Z_comp
#                 cross_2x = Xpt1 + largeRatio*X_comp
#                 cross_2y = Ypt1 + largeRatio*Y_comp
#                 cross_2z = Zpt1 + largeRatio*Z_comp
#                 d1x = Xpt1 - cross_1x
#                 d1y = Ypt1 - cross_1y
#                 d1z = Zpt1 - cross_1z
#                 d1 = np.sqrt(d1x**2 + d1y**2 + d1z**2)
#                 d2x = cross_1x - cross_2x
#                 d2y = cross_1y - cross_2y
#                 d2z = cross_1z - cross_2z
#                 d2 = np.sqrt(d2x**2 + d2y**2 + d2z**2)
#                 avg2x = (cross_1x + cross_2x)/2
#                 avg2y = (cross_1y + cross_2y)/2
#                 avg2z = (cross_1z + cross_2z)/2
#                 r2 = np.sqrt(avg2x**2 + avg2y**2 + avg2z**2)
#                 theta2 = np.arccos(avg2z/r2)
#                 phi2 = np.arctan(avg2y/avg2x)
#                 d3x = cross_2x - Xpt2
#                 d3y = cross_2y - Ypt2
#                 d3z = cross_2z - Zpt2
#                 d3 = np.sqrt(d3x**2 + d3y**2 + d3z**2)
#                 for s,boxno in enumerate(boxpt['box_num']):
#                     if boxpt['phi_radmin'][s] <= phi2 and phi2 <= boxpt['phi_radmax'][s] and \
#                        boxpt['theta_radmax'][s] <= theta2 and theta2 <= boxpt['theta_radmin'][s] and \
#                        boxpt['R_max'][s] <= r2 and r2 <= boxpt['R_min'][s]:
#                         midbox = int(boxno)
#                         break
#                 dist[box1-1][ray1-1] = d1 + dist[box1-1][ray1-1]
#                 dist[midbox-1][ray1-1] = d2 + dist[midbox-1][ray1-1]
#                 dist[box2-1][ray1-1] = d3 + dist[box2-1][ray1-1]
            
#             # Case 5: Ray crosses through 3 boxes in theta and R directions
#             elif (thetamin_b1 != thetamin_b2) and (thetamax_b1 != thetamax_b2) and \
#                (phimin_b1 == phimin_b2) and (phimax_b1 == phimax_b2) and \
#                (Rmin_b1 != Rmin_b2) and (Rmax_b1 != Rmax_b2):
#                 dR = coords['R'][r+1] - coords['R'][r]
#                 if dR > 0:
#                     r_ref = Rmin_b1
#                 elif dR < 0:
#                     r_ref = Rmax_b1
#                 d_theta = coords['theta_deg'][r+1] - coords['theta_deg'][r]
#                 if d_theta < 0:
#                     theta_ref = np.deg2rad(thetamax_b1)
#                 elif d_theta > 0:
#                     theta_ref = np.deg2rad(thetamin_b1)
#                 cos2 = np.cos(theta_ref)**2
#                 a_theta = cos2*(X_comp**2 + Y_comp**2 + Z_comp**2) - Z_comp**2
#                 b_theta = 2*(cos2*(Xpt1*X_comp + Ypt1*Y_comp + Zpt1*Z_comp) - Zpt1*Z_comp)
#                 c_theta = cos2*(Xpt1**2 + Ypt1**2 + Zpt1**2) - Zpt1**2
#                 xt1 = (-1*b_theta + np.sqrt(b_theta**2 - 4*a_theta*c_theta))/(2*a_theta)
#                 xt2 = (-1*b_theta - np.sqrt(b_theta**2 - 4*a_theta*c_theta))/(2*a_theta)
#                 xt1 = round(xt1*1000)/1000
#                 xt2 = round(xt2*1000)/1000
#                 if 0 <= xt1 and xt1 <= 1.0:
#                     xt = xt1
#                 elif 0 <= xt2 and xt2 <= 1.0:
#                     xt = xt2
#                 a_R = vector_len**2
#                 b_R = 2*Xpt1*X_comp + 2*Ypt1*Y_comp + 2*Zpt1*Z_comp
#                 c_R = -1*(r_ref**2) + Xpt1**2 + Ypt1**2 + Zpt1**2
#                 xr1 = (-1*b_R + np.sqrt(b_R**2 - 4*a_R*c_R))/(2*a_R)
#                 xr2 = (-1*b_R - np.sqrt(b_R**2 - 4*a_R*c_R))/(2*a_R)
#                 xr1 = round(xr1*1000)/1000
#                 xr2 = round(xr2*1000)/1000
#                 if 0 <= xr1 and xr1 <= 1.0:
#                     xr = xr1
#                 elif 0 <= xr2 and xr2 <= 1.0:
#                     xr = xr2
#                 if xr < xt:
#                     largeRatio = xt
#                     smallRatio = xr
#                 elif xt < xr:
#                     largeRatio = xr
#                     smallRatio = xt
#                 cross_1x = Xpt1 + smallRatio*X_comp
#                 cross_1y = Ypt1 + smallRatio*Y_comp
#                 cross_1z = Zpt1 + smallRatio*Z_comp
#                 cross_2x = Xpt1 + largeRatio*X_comp
#                 cross_2y = Ypt1 + largeRatio*Y_comp
#                 cross_2z = Zpt1 + largeRatio*Z_comp
#                 d1x = Xpt1 - cross_1x
#                 d1y = Ypt1 - cross_1y
#                 d1z = Zpt1 - cross_1z
#                 d1 = np.sqrt(d1x**2 + d1y**2 + d1z**2)
#                 d2x = cross_1x - cross_2x
#                 d2y = cross_1y - cross_2y
#                 d2z = cross_1z - cross_2z
#                 d2 = np.sqrt(d2x**2 + d2y**2 + d2z**2)
#                 avg2x = (cross_1x + cross_2x)/2
#                 avg2y = (cross_1y + cross_2y)/2
#                 avg2z = (cross_1z + cross_2z)/2
#                 r2 = np.sqrt(avg2x**2 + avg2y**2 + avg2z**2)
#                 theta2 = np.arccos(avg2z/r2)
#                 phi2 = np.arctan(avg2y/avg2x)
#                 d3x = cross_2x - Xpt2
#                 d3y = cross_2y - Ypt2
#                 d3z = cross_2z - Zpt2
#                 d3 = np.sqrt(d3x**2 + d3y**2 + d3z**2)
#                 for s,boxno in enumerate(boxpt['box_num']):
#                     if boxpt['phi_radmin'][s] <= phi2 and phi2 <= boxpt['phi_radmax'][s] and \
#                        boxpt['theta_radmax'][s] <= theta2 and theta2 <= boxpt['theta_radmin'][s] and \
#                        boxpt['R_max'][s] <= r2 and r2 <= boxpt['R_min'][s]:
#                         midbox = int(boxno)
#                         break
#                 dist[box1-1][ray1-1] = d1 + dist[box1-1][ray1-1]
#                 dist[midbox-1][ray1-1] = d2 + dist[midbox-1][ray1-1]
#                 dist[box2-1][ray1-1] = d3 + dist[box2-1][ray1-1]

#             # Case 6: Ray crosses through 3 boxes in theta and phi directions
#             elif (thetamin_b1 != thetamin_b2) and (thetamax_b1 != thetamax_b2) and \
#                (phimin_b1 != phimin_b2) and (phimax_b1 != phimax_b2) and \
#                (Rmin_b1 == Rmin_b2) and (Rmax_b1 == Rmax_b2):
#                 d_theta = coords['theta_deg'][r+1] - coords['theta_deg'][r]
#                 if d_theta < 0:
#                     theta_ref = np.deg2rad(thetamax_b1)
#                 elif d_theta > 0:
#                     theta_ref = np.deg2rad(thetamin_b1)
#                 d_phi = coords['phi_deg'][r+1] - coords['phi_deg'][r]
#                 if d_phi < 0:
#                     phi_ref = np.deg2rad(phimin_b1)
#                 elif d_phi > 0:
#                     phi_ref = np.deg2rad(phimax_b1)
#                 xp = (Ypt1 - Xpt1*np.tan(phi_ref))/(X_comp*np.tan(phi_ref) - Y_comp)
#                 cos2 = np.cos(theta_ref)**2
#                 a_theta = cos2*(X_comp**2 + Y_comp**2 + Z_comp**2) - Z_comp**2
#                 b_theta = 2*(cos2*(Xpt1*X_comp + Ypt1*Y_comp + Zpt1*Z_comp) - Zpt1*Z_comp)
#                 c_theta = cos2*(Xpt1**2 + Ypt1**2 + Zpt1**2) - Zpt1**2
#                 xt1 = (-1*b_theta + np.sqrt(b_theta**2 - 4*a_theta*c_theta))/(2*a_theta)
#                 xt2 = (-1*b_theta - np.sqrt(b_theta**2 - 4*a_theta*c_theta))/(2*a_theta)
#                 xt1 = round(xt1*1000)/1000
#                 xt2 = round(xt2*1000)/1000
#                 if 0 <= xt1 and xt1 <= 1.0:
#                     xt = xt1
#                 elif 0 <= xt2 and xt2 <= 1.0:
#                     xt = xt2
#                 if xp < xt:
#                     largeRatio = xt
#                     smallRatio = xp
#                 elif xt < xp:
#                     largeRatio = xp
#                     smallRatio = xt
#                 cross_1x = Xpt1 + smallRatio*X_comp
#                 cross_1y = Ypt1 + smallRatio*Y_comp
#                 cross_1z = Zpt1 + smallRatio*Z_comp
#                 cross_2x = Xpt1 + largeRatio*X_comp
#                 cross_2y = Ypt1 + largeRatio*Y_comp
#                 cross_2z = Zpt1 + largeRatio*Z_comp
#                 d1x = Xpt1 - cross_1x
#                 d1y = Ypt1 - cross_1y
#                 d1z = Zpt1 - cross_1z
#                 d1 = np.sqrt(d1x**2 + d1y**2 + d1z**2)
#                 d2x = cross_1x - cross_2x
#                 d2y = cross_1y - cross_2y
#                 d2z = cross_1z - cross_2z
#                 d2 = np.sqrt(d2x**2 + d2y**2 + d2z**2)
#                 avg2x = (cross_1x + cross_2x)/2
#                 avg2y = (cross_1y + cross_2y)/2
#                 avg2z = (cross_1z + cross_2z)/2
#                 r2 = np.sqrt(avg2x**2 + avg2y**2 + avg2z**2)
#                 theta2 = np.arccos(avg2z/r2)
#                 phi2 = np.arctan(avg2y/avg2x)
#                 d3x = cross_2x - Xpt2
#                 d3y = cross_2y - Ypt2
#                 d3z = cross_2z - Zpt2
#                 d3 = np.sqrt(d3x**2 + d3y**2 + d3z**2)
#                 for s,boxno in enumerate(boxpt['box_num']):
#                     if boxpt['phi_radmin'][s] <= phi2 and phi2 <= boxpt['phi_radmax'][s] and \
#                        boxpt['theta_radmax'][s] <= theta2 and theta2 <= boxpt['theta_radmin'][s] and \
#                        boxpt['R_max'][s] <= r2 and r2 <= boxpt['R_min'][s]:
#                         midbox = int(boxno)
#                         break
#                 dist[box1-1][ray1-1] = d1 + dist[box1-1][ray1-1]
#                 dist[midbox-1][ray1-1] = d2 + dist[midbox-1][ray1-1]
#                 dist[box2-1][ray1-1] = d3 + dist[box2-1][ray1-1]

#             # Case 7: Ray crosses through 4 boxes in R, theta and phi directions
#             elif (thetamin_b1 != thetamin_b2) and (thetamax_b1 != thetamax_b2) and \
#                (phimin_b1 != phimin_b2) and (phimax_b1 != phimax_b2) and \
#                (Rmin_b1 != Rmin_b2) and (Rmax_b1 != Rmax_b2):
#                 dR = coords['R'][r+1] - coords['R'][r]
#                 if dR > 0:
#                     r_ref = Rmin_b1
#                 elif dR < 0:
#                     r_ref = Rmax_b1
#                 d_theta = coords['theta_deg'][r+1] - coords['theta_deg'][r]
#                 if d_theta < 0:
#                     theta_ref = np.deg2rad(thetamax_b1)
#                 elif d_theta > 0:
#                     theta_ref = np.deg2rad(thetamin_b1)
#                 d_phi = coords['phi_deg'][r+1] - coords['phi_deg'][r]
#                 if d_phi < 0:
#                     phi_ref = np.deg2rad(phimin_b1)
#                 elif d_phi > 0:
#                     phi_ref = np.deg2rad(phimax_b1)
#                 if coords['R'][r] == r_ref and coords['R'][r+1] == r_ref-1:
#                     xr = 0
#                 else:
#                     a_R = vector_len**2
#                     b_R = 2*Xpt1*X_comp + 2*Ypt1*Y_comp + 2*Zpt1*Z_comp
#                     c_R = -1*(r_ref**2) + Xpt1**2 + Ypt1**2 + Zpt1**2
#                     xr1 = (-1*b_R + np.sqrt(b_R**2 - 4*a_R*c_R))/(2*a_R)
#                     xr2 = (-1*b_R - np.sqrt(b_R**2 - 4*a_R*c_R))/(2*a_R)
#                     xr1 = round(xr1*1000)/1000
#                     xr2 = round(xr2*1000)/1000
#                     if 0 <= xr1 and xr1 <= 1.0:
#                         xr = xr1
#                     elif 0 <= xr2 and xr2 <= 1.0:
#                         xr = xr2
#                 xp = (Ypt1 - Xpt1*np.tan(phi_ref))/(X_comp*np.tan(phi_ref) - Y_comp)
#                 cos2 = np.cos(theta_ref)**2
#                 a_theta = cos2*(X_comp**2 + Y_comp**2 + Z_comp**2) - Z_comp**2
#                 b_theta = 2*(cos2*(Xpt1*X_comp + Ypt1*Y_comp + Zpt1*Z_comp) - Zpt1*Z_comp)
#                 c_theta = cos2*(Xpt1**2 + Ypt1**2 + Zpt1**2) - Zpt1**2
#                 xt1 = (-1*b_theta + np.sqrt(b_theta**2 - 4*a_theta*c_theta))/(2*a_theta)
#                 xt2 = (-1*b_theta - np.sqrt(b_theta**2 - 4*a_theta*c_theta))/(2*a_theta)
#                 xt1 = round(xt1*1000)/1000
#                 xt2 = round(xt2*1000)/1000
#                 if 0 <= xt1 and xt1 <= 1.0:
#                     xt = xt1
#                 elif 0 <= xt2 and xt2 <= 1.0:
#                     xt = xt2
#                 if max(xr,xt,xp) == xp:
#                     largeRatio = xp
#                     if xt > xr:
#                         midRatio = xt
#                         smallRatio = xr
#                     elif xr > xt:
#                         midRatio = xr
#                         smallRatio = xt
#                 elif max(xr,xt,xp) == xt:
#                     largeRatio = xt
#                     if xp > xr:
#                         midRatio = xp
#                         smallRatio = xr
#                     elif xr > xp:
#                         midRatio = xr
#                         smallRatio = xp
#                 elif max(xr,xt,xp) == xr:
#                     largeRatio = xr
#                     if xp > xt:
#                         midRatio = xp
#                         smallRatio = xt
#                     elif xt > xp:
#                         midRatio = xt
#                         smallRatio = xp
#                 cross_1x = Xpt1 + smallRatio*X_comp
#                 cross_1y = Ypt1 + smallRatio*Y_comp
#                 cross_1z = Zpt1 + smallRatio*Z_comp
#                 cross_2x = Xpt1 + midRatio*X_comp
#                 cross_2y = Ypt1 + midRatio*Y_comp
#                 cross_2z = Zpt1 + midRatio*Z_comp
#                 cross_3x = Xpt1 + largeRatio*X_comp
#                 cross_3y = Ypt1 + largeRatio*Y_comp
#                 cross_3z = Zpt1 + largeRatio*Z_comp
#                 d1x = Xpt1 - cross_1x
#                 d1y = Ypt1 - cross_1y
#                 d1z = Zpt1 - cross_1z
#                 d1 = np.sqrt(d1x**2 + d1y**2 + d1z**2)
#                 d2x = cross_1x - cross_2x
#                 d2y = cross_1y - cross_2y
#                 d2z = cross_1z - cross_2z
#                 d2 = np.sqrt(d2x**2 + d2y**2 + d2z**2)
#                 avg2x = (cross_1x + cross_2x)/2
#                 avg2y = (cross_1y + cross_2y)/2
#                 avg2z = (cross_1z + cross_2z)/2
#                 r2 = np.sqrt(avg2x**2 + avg2y**2 + avg2z**2)
#                 theta2 = np.arccos(avg2z/r2)
#                 phi2 = np.arctan(avg2y/avg2x)
#                 d3x = cross_2x - cross_3x
#                 d3y = cross_2y - cross_3y
#                 d3z = cross_2z - cross_3z
#                 d3 = np.sqrt(d3x**2 + d3y**2 + d3z**2)
#                 avg3x = (cross_2x + cross_3x)/2
#                 avg3y = (cross_2y + cross_3y)/2
#                 avg3z = (cross_2z + cross_3z)/2
#                 r3 = np.sqrt(avg3x**2 + avg3y**2 + avg3z**2)
#                 theta3 = np.arccos(avg3z/r3)
#                 phi3 = np.arctan(avg3y/avg3x)
#                 d4x = cross_3x - Xpt2
#                 d4y = cross_3y - Ypt2
#                 d4z = cross_3z - Zpt2
#                 d4 = np.sqrt(d4x**2 + d4y**2 + d4z**2)
#                 for s,boxno in enumerate(boxpt['box_num']):
#                     if boxpt['phi_radmin'][s] <= phi2 and phi2 <= boxpt['phi_radmax'][s] and \
#                        boxpt['theta_radmax'][s] <= theta2 and theta2 <= boxpt['theta_radmin'][s] and \
#                        boxpt['R_max'][s] <= r2 and r2 <= boxpt['R_min'][s]:
#                         midbox2 = int(boxno)
#                         break
#                 for s,boxno in enumerate(boxpt['box_num']):
#                     if boxpt['phi_radmin'][s] <= phi3 and phi3 <= boxpt['phi_radmax'][s] and \
#                        boxpt['theta_radmax'][s] <= theta3 and theta3 <= boxpt['theta_radmin'][s] and \
#                        boxpt['R_max'][s] <= r3 and r3 <= boxpt['R_min'][s]:
#                         midbox3 = int(boxno)
#                         break
#                 dist[box1-1][ray1-1] = d1 + dist[box1-1][ray1-1]
#                 dist[midbox2-1][ray1-1] = d2 + dist[midbox2-1][ray1-1]
#                 dist[midbox3-1][ray1-1] = d3 + dist[midbox3-1][ray1-1]
#                 dist[box2-1][ray1-1] = d4 + dist[box2-1][ray1-1]
    
#     # If points not on same ray path
#     elif ray1 != ray2:
#         continue

# np.savetxt('/Volumes/External/Tomography/dist.txt',dist)
print('GO')
chunk = 0
dist_pd = pd.DataFrame()
for dist_tfr in pd.read_table('/Volumes/External/Tomography/dist.txt',sep=' ',header=None,chunksize=1000,iterator=True):
    chunk = chunk + 1
    dist_pd = pd.concat([dist_pd,dist_tfr],ignore_index=True)
dist_pd.head()
dist = dist_pd.to_numpy()
dist = np.loadtxt('/Volumes/External/Tomography/dist.txt')

# MAKE TRAVEL TIME ARRAY TT_SP
tt_sp = np.zeros((len(all_good_rays),NBLOCKS))

# Populate TT_SP array by dividing distance of a ray path in a block by the block's velocity
for i in range(NBLOCKS):
    print('Working on block #',i+1,'out of',NBLOCKS)
    for j in range(len(all_good_rays)):
        tt_p = dist[i,j]/velo_model['p_velo'][i]
        tt_s = dist[i,j]/velo_model['s_velo'][i]
        sminp = tt_s - tt_p*(1/GAMMA)
        tt_sp[j,i] = sminp

# PERFORM INVERSION

# Allocate space
g_mod = np.zeros(((np.shape(CdI)[0]+(Nblocks_lat*Nblocks_lon*(Nblocks_dep-2))+((Nblocks_lat-2)*Nblocks_lon*Nblocks_dep)+(Nblocks_lat*(Nblocks_lon-2)*Nblocks_dep)),NBLOCKS),dtype=np.float32)
g = g_mod[:np.shape(CdI)[0],:]
dr = g_mod[np.shape(CdI)[0]:(np.shape(CdI)[0]+(Nblocks_lat*Nblocks_lon*(Nblocks_dep-2))),:]
dtheta = g_mod[(np.shape(CdI)[0]+(Nblocks_lat*Nblocks_lon*(Nblocks_dep-2))):(np.shape(CdI)[0]+(Nblocks_lat*Nblocks_lon*(Nblocks_dep-2))+((Nblocks_lat-2)*Nblocks_lon*Nblocks_dep)),:]
dphi = g_mod[(np.shape(CdI)[0]+(Nblocks_lat*Nblocks_lon*(Nblocks_dep-2))+((Nblocks_lat-2)*Nblocks_lon*Nblocks_dep)):,:]

# Predicted data
dpre = tt_sp@m0

# Incorporate measurement reliability using inverse covariance
g[:,:] = CdI@tt_sp

# Data perturbations weighted by inverse covariance
ddt = CdI@(t_star - dpre)

# Incorporate smoothing/roughening
wtR = 10000000
wtTHETA = 10000000
wtPHI = 10000000

# # Set up indexing for DR, DTHETA, DPHI matrices
# indx = np.zeros((Nblocks_dep,Nblocks_lat,Nblocks_lon),dtype=int)
# count = 0
# for i in range(Nblocks_dep):
#     for j in range(Nblocks_lat):
#         for k in range(Nblocks_lon):
#             indx[i,j,k] = count
#             count = count + 1

# # Populate DR matrix
# rown = 0
# dr = np.zeros((Nblocks_lat*Nblocks_lon*(Nblocks_dep-2),NBLOCKS),dtype=np.float32)
# for j in range(Nblocks_lat):
#     for k in range(Nblocks_lon):
#         for i in range(Nblocks_dep)[1:-1]:
#             Rint = deprange[i-1] - deprange[i]
#             facR = wtR/(Rint**2)
#             dr[rown,indx[i-1,j,k]] = facR
#             dr[rown,indx[i,j,k]] = -2*facR
#             dr[rown,indx[i+1,j,k]] = facR
#             rown = rown + 1
#             print('Working on row',rown,'out of',(Nblocks_lat*Nblocks_lon*(Nblocks_dep-2)))

# #np.savetxt('/Volumes/External/Tomography/dr.txt',dr)
# #dr = np.loadtxt('/Volumes/External/Tomography/dr.txt')

# # Populate DTHETA matrix
# rown = 0
# dtheta = np.zeros(((Nblocks_lat-2)*Nblocks_lon*Nblocks_dep,NBLOCKS),dtype=np.float32)
# for k in range(Nblocks_lon):
#     for i in range(Nblocks_dep):
#         for j in range(Nblocks_lat)[1:-1]:
#             thetaint = (latrange[j] - latrange[j-1])*111.1949
#             factheta = wtTHETA/(thetaint**2)
#             dtheta[rown,indx[i,j-1,k]] = factheta
#             dtheta[rown,indx[i,j,k]] = -2*factheta
#             dtheta[rown,indx[i,j+1,k]] = factheta
#             rown = rown + 1
#             print('Working on row',rown,'out of',((Nblocks_lat-2)*Nblocks_lon*Nblocks_dep))

# #np.savetxt('/Volumes/External/Tomography/dtheta.txt',dtheta)
# #dtheta = np.loadtxt('/Volumes/External/Tomography/dtheta.txt')

# # Populate DPHI matrix
# rown = 0
# dphi = np.zeros((Nblocks_lat*(Nblocks_lon-2)*Nblocks_dep,NBLOCKS),dtype=np.float32)
# for i in range(Nblocks_dep):
#     for j in range(Nblocks_lat):
#         for k in range(Nblocks_lon)[1:-1]:
#             phiint = (lonrange[k] - lonrange[k-1])*95.31
#             facphi = wtPHI/(phiint**2)
#             dphi[rown,indx[i,j,k-1]] = facphi
#             dphi[rown,indx[i,j,k]] = -2*facphi
#             dphi[rown,indx[i,j,k+1]] = facphi
#             rown = rown + 1
#             print('Working on row',rown,'out of',(Nblocks_lat*(Nblocks_lon-2)*Nblocks_dep))

# #np.savetxt('/Volumes/External/Tomography/dphi.txt',dphi)
# #dphi = np.loadtxt('/Volumes/External/Tomography/dphi.txt')

ttsp2 = tt_sp

# Create modified G matrix with roughening/smoothing
# g_mod = np.concatenate((g,dr,dtheta,dphi),axis=0)
newrows = len(g_mod[:,0]) - len(g[:,0])

# Pad data vector with zeros
dmod = np.append(ddt,np.zeros(newrows))

# # Find columns of unsampled model parameters
# rmlist = np.array([],dtype=int)
# for col in range(len(g_mod[0,:])):
#     print('Working on column #',col+1,'out of',len(g_mod[0,:]))
#     for row in range(len(all_good_rays)):
#         elem = g_mod[row,col]
#         if elem != 0:
#             break
#         if row == len(all_good_rays)-1:
#             rmlist = np.append(rmlist,col)

# # GwoSMOOTH = g

# # Remove unsampled columns from g_mod and m0_mod
# cols2rm = np.flip(rmlist)
# print(len(cols2rm))
# m0_mod = m0
# for column in cols2rm:
#     print('Working on column #',column)
#     g_mod = np.delete(g_mod,column,1)
#     print('Worked')
#     ttsp2 = np.delete(ttsp2,column,1)
#     m0_mod = np.delete(m0_mod,column)

# # print('Done')

# np.savetxt('/Volumes/External/Tomography/g_mod.txt',g_mod)
# np.savetxt('/Volumes/External/Tomography/ttsp2.txt',ttsp2)
# np.savetxt('/Volumes/External/Tomography/m0_mod.txt',m0_mod)
# np.savetxt('/Volumes/External/Tomography/rmlist.txt',rmlist)
g_mod = np.loadtxt('/Volumes/External/Tomography/g_mod.txt')
ttsp2 = np.loadtxt('/Volumes/External/Tomography/ttsp2.txt')
m0_mod = np.loadtxt('/Volumes/External/Tomography/m0_mod.txt')
rmlist = np.loadtxt('/Volumes/External/Tomography/rmlist.txt')
cols2rm = np.flip(rmlist)

print(np.shape(g_mod))
print(np.nonzero(g_mod))
print(np.count_nonzero(np.isnan(g_mod)))
print(np.count_nonzero(np.isinf(g_mod)))

# Using Menke nonneg method

# Identity matrix
H_i = np.eye(NBLOCKS - len(cols2rm))

# Constraint matrix
Qmax = 1500
h = np.zeros(len(m0_mod))
for i,m_param in enumerate(m0_mod):
    h[i] = (1/Qmax) - m_param

# SVD of g_mod
#g_mod = g_mod.astype(np.float64)
print('Starting svd')
Up,Lp,Vp = linalg.svd(g_mod,full_matrices=False)
print('Done with svd')

# Make diagonal matrix of inverse singular values
r_lambda = Lp**-1
Lpi = np.diag(r_lambda)

Hp = (-1*H_i)@Vp.T@Lpi
hp = h - (H_i@Vp.T@Lpi)@Up.T@dmod
hp = np.reshape(hp,(len(hp),1))

print(np.shape(Hp),np.shape(hp))

Gp = np.transpose(np.concatenate((Hp,hp),axis=1))
dp = np.append(np.zeros(len(Hp[0,:])),[1])
print('we are here')
mpp = sciop.nnls(Gp,dp)[0]

print(np.shape(Gp),np.shape(mpp))

# Calculate prediction error
ep = dp - (Gp @ mpp)
mp = (-1*ep[:-1])/ep[-1]

# DM gives the perturbations to the starting model
dm = Vp.T @ Lpi @ ((Up.T @ dmod) - mp)

# Create Q model
cnt = 0
qmod_full = np.zeros(NBLOCKS)
qmod_prtl = np.zeros(NBLOCKS - len(rmlist))
for k in range(NBLOCKS):
    if k in rmlist:
        qmod_full[k] = 0
    else:
        qmod_full[k] = (dm[cnt] + m0_mod[cnt])**-1
        qmod_prtl[cnt] = dm[cnt] + m0_mod[cnt]
        cnt = cnt + 1

# Write Q model to output file
q_model = pd.DataFrame({'box_num':[],'R':[],'theta':[],'phi':[],'lon':[], \
                        'lat':[],'dep':[],'Qs':[]})

for i in range(NBLOCKS):
    block_num = i+1
    avg_R = (boxpt['R_min'][i] + boxpt['R_max'][i])/2
    avg_theta_rad = (boxpt['theta_radmin'][i] + boxpt['theta_radmax'][i])/2
    avg_phi_rad = (boxpt['phi_radmin'][i] + boxpt['phi_radmax'][i])/2
    avg_lon = (boxpt['lon_min'][i] + boxpt['lon_max'][i])/2
    avg_lat = (boxpt['lat_min'][i] + boxpt['lat_max'][i])/2
    avg_dep = (boxpt['dep_min'][i] + boxpt['dep_max'][i])/2
    blockQ = qmod_full[i]
    q_model = q_model.append({'box_num':block_num,'R':avg_R,'theta':avg_theta_rad,'phi':avg_phi_rad,'lon':avg_lon, \
                              'lat':avg_lat,'dep':avg_dep,'Qs':blockQ}, ignore_index = True)

q_model.to_csv('/Volumes/External/Tomography/qs_model.csv',index=False)