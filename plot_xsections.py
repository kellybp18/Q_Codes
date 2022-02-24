import numpy as np
import pygmt
import pandas as pd
import os
import time

map_coords = np.array([-73.0,-68.0,-34.0,-29.0])

lonmin = -73.0
lonmax = -68.0
depmin = 10
depmax = -180

q_database = pd.read_csv('/Volumes/External/Attenuation/q_database.csv')
qs_model = pd.read_csv('/Volumes/External/Tomography/qs_model.csv')
elev_data = pd.read_table('/Users/bpk/Documents/AGU_2021/Illapel_topo15.xyz',sep='\t',dtype=float,names=['lon','lat','elev'])
stn_data = pd.read_table('/Users/bpk/Documents/BPK_Masters_2019/AGU_Fall_Meeting_2019/Illapel_Stns.gmt',sep=' ',dtype=float,usecols=[0,1,2],names=['lat','lon','elev'])

qs_model.loc[(qs_model['Qs'] > 0.0) & (qs_model['Qs'] < 75.0),'Qs'] = 75.0
qs_model.loc[(qs_model['Qs'] > 1500.0),'Qs'] = 1500.0

good_rays = q_database[q_database['judge_result'] == 'GOOD']
ev_list,indices = np.unique(good_rays['ev_id'],return_index=True)
unique_q_list = good_rays.iloc[indices]

q_max = np.max(qs_model['Qs']) + 10
q_min = np.min(qs_model['Qs'])
q_inc = 50
print(q_min,q_max,q_inc)

uniqlats = np.unique(qs_model['lat'])
uniqlons = np.unique(qs_model['lon'])
uniqdeps = np.unique(qs_model['dep'])
lonstep = (uniqlons[1] - uniqlons[0])
depstep = (uniqdeps[1] - uniqdeps[0])
surflonstep = round(lonstep/16,8)
surfdepstep = round(depstep/16,8)
print(surflonstep,surfdepstep)

#hitcounts = pd.DataFrame({'boxnum':[],'hitcount':[],'total_ray_dist':[]})
#
#dist = np.loadtxt('/Volumes/External/Tomography/dist.txt')
#
#for j in range(len(dist[:,0])):
#    blockdist = dist[j,:]
#    nonzerodists = blockdist[np.nonzero(blockdist)]
#    hitcount = len(nonzerodists)
#    totaldist = np.sum(nonzerodists)
#    hitcounts = hitcounts.append({'boxnum':j+1,'hitcount':hitcount,'total_ray_dist':totaldist},ignore_index=True)
#
#hitcounts.to_csv('/Volumes/External/Tomography/hitcounts.csv',index=False)
hitcounts = pd.read_csv('/Volumes/External/Tomography/hitcounts.csv')

os.system('cd /Volumes/External/Tomography/Figures')

for i in uniqlats:
    latslice = qs_model[qs_model['lat'] == i]
    latslice_nozero = latslice[latslice['Qs'] != 0]
    np_latslice_nozero = np.array(latslice[latslice['Qs'] != 0])
    if np_latslice_nozero.size == 0:
        continue
    currentqmin = np.min(latslice['Qs'])
    lat_round = np.round(i,2)

    latslice_boxnums = np.array(latslice['box_num'])
    hitcount_boxes = hitcounts.loc[latslice_boxnums-1,:]
    hitcount_data = pd.DataFrame(latslice.loc[:,['lon','dep']])
    hitcount_data = hitcount_data.join(hitcount_boxes)
    mindist = np.min(hitcount_data['total_ray_dist'])
    maxdist = np.max(hitcount_data['total_ray_dist'])

    # Get data for earthquake plotting of earthquakes within one box width
    half_lonstep = lonstep/2
    minlat = lat_round - half_lonstep
    maxlat = lat_round + half_lonstep
    hold_eqs = unique_q_list[unique_q_list['ev_lat'] >= minlat]
    eqs = hold_eqs[hold_eqs['ev_lat'] <= maxlat]

    # Get data for station plotting

    surf_data = pd.DataFrame(latslice.loc[:,['lon','dep','Qs']])
    surf_data.to_csv(('/Volumes/External/Tomography/Figures/surfgrid_'+str(lat_round)+'.xyz'),header=None,index=None,sep=' ',mode='w')

    os.system(('gmt blockmean /Volumes/External/Tomography/Figures/surfgrid_'+str(lat_round)+'.xyz -R-73/-68/-180/0 -I'+str(surflonstep)+'/'+str(surfdepstep)+' > /Volumes/External/Tomography/Figures/surfgridmed_'+str(lat_round)+'.xyz'))
    time.sleep(3)
    os.system(('gmt surface /Volumes/External/Tomography/Figures/surfgridmed_'+str(lat_round)+'.xyz -G/Volumes/External/Tomography/Figures/surfgridmed_'+str(lat_round)+'.grd -I'+str(surflonstep)+'/'+str(surfdepstep)+' -Lu1500.0 -R-73/-68/-180/0 -Tb1i0'))
    time.sleep(5)
    print("Okay")

    fig = pygmt.Figure()
    pygmt.xyz2grd(x=np.ascontiguousarray(latslice_nozero['lon']),
                y=np.ascontiguousarray(latslice_nozero['dep']),
                z=np.ascontiguousarray(latslice_nozero['Qs']),
                outgrid = ('/Volumes/External/Tomography/Figures/Q_'+str(lat_round)+'.grd'),
                region=[uniqlons[0],uniqlons[-1],uniqdeps[0],uniqdeps[-1]],
                spacing=(str(lonstep)+'+e/'+str(depstep)+'+e'))
    pygmt.grdclip(('/Volumes/External/Tomography/Figures/surfgridmed_'+str(lat_round)+'.grd'),
                outgrid=('/Volumes/External/Tomography/Figures/surfgridclip_'+str(lat_round)+'.grd'),
                below=[75,np.nan])
    #pygmt.config(COLOR_NAN='white')
    #pygmt.makecpt(cmap='seis',
    #            series=[q_min,q_max,q_inc],
    #            continuous=True,
    #            background='o')
    fig.grdimage(('/Volumes/External/Tomography/Figures/Q_'+str(lat_round)+'.grd'),
                cmap='/Volumes/External/Tomography/Figures/qs.cpt',
                projection='x4.0/0.06',
                region=[lonmin,lonmax,depmax,depmin],
                interpolation='n')
    fig.basemap(projection='x4.0/0.06',
                region=[lonmin,lonmax,depmax,depmin],
                frame=['WSne','xa1f0.5+lLongitude','ya10f10+l"Depth (km)"'],
                )
    fig.colorbar(frame=['xc/Volumes/External/Tomography/Figures/cbar_annots.txt+LQs'],
                 cmap='/Volumes/External/Tomography/Figures/qs.cpt',
                 position='JMR+o0.75c/0c+w7c/0.5c+n"No Data"')
    fig.savefig(('/Volumes/External/Tomography/Figures/'+str(lat_round)+'_slice.png'))

    fig2 = pygmt.Figure()
    #pygmt.makecpt(cmap='seis',
    #            series=(str(q_min)+'/'+str(q_max)+'/'+str(q_inc)),
    #            continuous=True,
    #            background='o')
    pygmt.grdtrack(points='',
                grid='/Users/bpk/Documents/AGU_2021/Illapel_topo15.grd',
                outfile='/Volumes/External/Tomography/Figures/topo_track.txt',
                region=[lonmin,lonmax,depmax,depmin],
                profile=('-73/' + str(lat_round) + '/-68/' + str(lat_round) + '+i0.1'))
    topo_track = pd.read_table('/Volumes/External/Tomography/Figures/topo_track.txt',sep='\t',dtype=float,names=['lon','lat','dep'])
#    os.system("awk '{print $1,($3/1000)}' </Volumes/External/Tomography/Figures/topo_track.txt> /Volumes/External/Tomography/Figures/topoline.xy")
#    time.sleep(2)
    pygmt.grdtrack(points='',
                grid='/Users/bpk/Documents/BPK_Masters_2019/Illapel_Map/Illapel_Slab2_Contours.grd',
                outfile='/Volumes/External/Tomography/Figures/slab_track.txt',
                region=[lonmin,lonmax,depmax,depmin],
                profile=('-73/' + str(lat_round) + '/-68/' + str(lat_round) + '+i0.1'),
                interpolation='n',
                skiprows=True)
    slab = pd.read_table('/Volumes/External/Tomography/Figures/slab_track.txt',sep='\t',dtype=float,names=['lon','lat','dep'])
    first_row = pd.DataFrame({'lon':[-73.0],'lat':[lat_round],'dep':[(topo_track['dep'][0]/1000)]},index=[0])
    slab = pd.concat([first_row,slab]).reset_index(drop = True)
    print(slab.head())
#    os.system("awk '{print $1,$3}' </Volumes/External/Tomography/Figures/slab_track.txt> /Volumes/External/Tomography/Figures/slabline.xy")
#    time.sleep(2)
    fig2.grdimage(('/Volumes/External/Tomography/Figures/surfgridclip_'+str(lat_round)+'.grd'),
                projection='x4.0/0.06',
                cmap='/Volumes/External/Tomography/Figures/qs_surf.cpt',
                region=[lonmin,lonmax,depmax,depmin],
                interpolation='n')
    fig2.basemap(projection='x4.0/0.06',
                region=[lonmin,lonmax,depmax,depmin],
                frame=['WSne','xa1f1+lLongitude','ya10f5+l"Depth (km)"'],
                )
    fig2.plot(x=topo_track['lon'],y=topo_track['dep']/1000,
                projection='x4.0/0.06',
                region=[lonmin,lonmax,depmax,depmin],
                pen='thick,darkbrown')
    fig2.plot(x=slab['lon'],y=slab['dep'],
                projection='x4.0/0.06',
                region=[lonmin,lonmax,depmax,depmin],
                pen='thick,black')
    fig2.plot(x=np.array(eqs['ev_lon'],dtype=float),y=np.array(-1*eqs['ev_dep'],dtype=float),
                projection='x4.0/0.06',
                region=[lonmin,lonmax,depmax,depmin],
                style='c0.1',
                color='white',
                pen='thin,black')
    fig2.plot(x=np.array(stn_data['lon'],dtype=float),y=np.array(-1*stn_data['elev'],dtype=float),
                projection='x4.0/0.06',
                region=[lonmin,lonmax,depmax,depmin],
                style='t0.2',
                color='cyan',
                pen='thin,black')
    fig2.colorbar(frame=['xc/Volumes/External/Tomography/Figures/cbar_annots.txt+LQs'],
                 cmap='/Volumes/External/Tomography/Figures/qs.cpt',
                 position='JMR+o0.75c/0c+w7c/0.5c')
    fig2.savefig(('/Volumes/External/Tomography/Figures/'+str(lat_round)+'_slice_surf.png'))

    fig3 = pygmt.Figure()
    pygmt.xyz2grd(x=np.array(hitcount_data['lon']),
                y=np.array(hitcount_data['dep']),
                z=np.array(hitcount_data['total_ray_dist']),
                outgrid = ('/Volumes/External/Tomography/Figures/hitcounts_'+str(lat_round)+'.grd'),
                region=[uniqlons[0],uniqlons[-1],uniqdeps[0],uniqdeps[-1]],
                spacing=(str(lonstep)+'+e/'+str(depstep)+'+e'))
    pygmt.makecpt(cmap='seis',
                series=(str(mindist)+'/'+str(maxdist)+'/'+str((maxdist-mindist)/30)),
                continuous=True,
                background='o')
    fig3.grdimage(('/Volumes/External/Tomography/Figures/hitcounts_'+str(lat_round)+'.grd'),
                projection='x4.0/0.06',
                region=[lonmin,lonmax,depmax,depmin],
                interpolation='n')    
    fig3.basemap(projection='x4.0/0.06',
                region=[lonmin,lonmax,depmax,depmin],
                frame=['WSne','xa1f1+lLongitude','ya10f5+l"Depth (km)"'],
                )
    fig3.text(x=np.array(hitcount_data['lon']),
              y=np.array(hitcount_data['dep']),
              text=np.array(np.array(hitcount_data['hitcount'],dtype=int),dtype=str),
              projection='x4.0/0.06',
              region=[lonmin,lonmax,depmax,depmin])
    fig3.colorbar(frame=['x+l"Sum of Ray Distances in Box"','y+lkm'],
                 position='JMR+o0.75c/0c+w7c/0.5c')
    fig3.savefig(('/Volumes/External/Tomography/Figures/'+str(lat_round)+'_hitcounts.png'))
