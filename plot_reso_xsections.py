# Code to plot the cross-section resolution test in GMT.
# 
# For the high Q bar structure, set
# structure = 'bar'
#
# For the low Q bar structure, set
# structure = 'inverted_bar'

import numpy as np
import pygmt
import pandas as pd
import os
import time

map_coords = np.array([-73.0,-68.0,-34.0,-29.0])
data_dir = '/Volumes/External/Resolution_Tests/Latbox_49_Lonbox_46_Depbox_40/'
structure = 'bar'

lonmin = -73.0
lonmax = -70.0
depmin = 10
depmax = -72

q_database = pd.read_csv('/Volumes/External/Attenuation/q_database.csv')
elev_data = pd.read_table('/Users/bpk/Documents/AGU_2021/Illapel_topo15.xyz',sep='\t',dtype=float,names=['lon','lat','elev'])
stn_data = pd.read_table('/Users/bpk/Documents/BPK_Masters_2019/AGU_Fall_Meeting_2019/Illapel_Stns.gmt',sep=' ',dtype=float,usecols=[0,1,2],names=['lat','lon','elev'])
qs_initial_model = (1/450)*np.ones(90160)#np.loadtxt(data_dir + 'm0_mod.txt')

if structure == 'inverted_bar':
    bar_qs = 300
    else_qs = 900
elif structure == 'bar':
    bar_qs = 900
    else_qs = 300
else:
    raise ValueError('"structure" variable must equal "inverted_bar" or "bar".')
qs_model = pd.read_csv(data_dir + 'qs_model_' + structure + '.csv')
qs_synth_model = np.concatenate(((1/900)*np.ones(6762),(1/300)*np.ones(11270),(1/900)*np.ones(72128))) #np.loadtxt(data_dir + 'm0_synth.txt')

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

hitcounts = pd.DataFrame({'boxnum':[],'hitcount':[],'total_ray_dist':[]})

dist = np.loadtxt(data_dir + 'dist.txt')

for j in range(len(dist[:,0])):
   blockdist = dist[j,:]
   nonzerodists = blockdist[np.nonzero(blockdist)]
   hitcount = len(nonzerodists)
   totaldist = np.sum(nonzerodists)
   hitcounts = hitcounts.append({'boxnum':j+1,'hitcount':hitcount,'total_ray_dist':totaldist},ignore_index=True)

hitcounts.to_csv(data_dir + 'hitcounts.csv',index=False)
#hitcounts = pd.read_csv('/Volumes/External/Tomography/hitcounts.csv')

os.system('cd ' + data_dir + 'Figures')

for i in uniqlats:
    latslice = qs_model[qs_model['lat'] == i]
    latslice_nozero = latslice[latslice['Qs'] != 0]
    np_latslice_nozero = np.array(latslice[latslice['Qs'] != 0])
    if np_latslice_nozero.size == 0:
        continue
    currentqmin = np.min(latslice['Qs'])
    lat_round = np.round(i,2)

    mask_data = pd.DataFrame(latslice.loc[:,['lon','dep','Qs']])
    mask_data.to_csv((data_dir + 'Figures/maskgrid_'+str(lat_round)+'.xyz'),header=None,index=None,sep=' ',mode='w')

    os.system(('gmt blockmean ' + data_dir + 'Figures/maskgrid_'+str(lat_round)+'.xyz -R-73/-68/-180/0 -I'+str(surflonstep)+'/'+str(surfdepstep)+' > ' + data_dir + 'Figures/maskgridmed_'+str(lat_round)+'.xyz'))
    time.sleep(3)
    os.system(('gmt surface ' + data_dir + 'Figures/maskgridmed_'+str(lat_round)+'.xyz -G' + data_dir + 'Figures/maskgridmed_'+str(lat_round)+'.grd -I'+str(surflonstep)+'/'+str(surfdepstep)+' -Lu1500.0 -R-73/-68/-180/0 -Tb1i0'))
    time.sleep(5)
    os.system(('gmt grdclip ' + data_dir + 'Figures/maskgridmed_'+str(lat_round)+'.grd -G' + data_dir + 'Figures/maskgridclip_'+str(lat_round)+'.grd -Sb75.0/NaN'))
    time.sleep(5)

    latslice_boxnums = np.array(latslice['box_num'])
    for lbox in latslice_boxnums:
        if latslice.loc[int(lbox-1),'Qs'] == 0.0:
            latslice.loc[int(lbox-1),'Qs'] = 1/(qs_initial_model[int(lbox-1)])

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
    surf_data.to_csv((data_dir + 'Figures/surfgrid_'+str(lat_round)+'.xyz'),header=None,index=None,sep=' ',mode='w')

    os.system(('gmt blockmean ' + data_dir + 'Figures/surfgrid_'+str(lat_round)+'.xyz -R-73/-68/-180/0 -I'+str(surflonstep)+'/'+str(surfdepstep)+' > ' + data_dir + 'Figures/surfgridmed_'+str(lat_round)+'.xyz'))
    time.sleep(3)
    os.system(('gmt surface ' + data_dir + 'Figures/surfgridmed_'+str(lat_round)+'.xyz -G' + data_dir + 'Figures/surfgridmed_'+str(lat_round)+'.grd -I'+str(surflonstep)+'/'+str(surfdepstep)+' -Lu1500.0 -R-73/-68/-180/0 -Tb1i0'))
    time.sleep(5)
    os.system(('gmt grdmath ' + data_dir + 'Figures/surfgridmed_'+str(lat_round)+'.grd ' + data_dir + 'Figures/maskgridclip_'+str(lat_round)+'.grd OR = ' + data_dir + 'Figures/surfmaskgridmed_'+str(lat_round)+'.grd'))
    time.sleep(3)
    print("Okay")

    fig = pygmt.Figure()
    pygmt.xyz2grd(x=np.ascontiguousarray(latslice_nozero['lon']),
                y=np.ascontiguousarray(latslice_nozero['dep']),
                z=np.ascontiguousarray(latslice_nozero['Qs']),
                outgrid = (data_dir + 'Figures/Q_'+str(lat_round)+'.grd'),
                region=[uniqlons[0],uniqlons[-1],uniqdeps[0],uniqdeps[-1]],
                spacing=(str(lonstep)+'+e/'+str(depstep)+'+e'))
    pygmt.grdclip((data_dir + 'Figures/surfmaskgridmed_'+str(lat_round)+'.grd'),
                outgrid=(data_dir + 'Figures/surfgridclip_'+str(lat_round)+'.grd'),
                below=[75,75.0])
    #pygmt.config(COLOR_NAN='white')
    #pygmt.makecpt(cmap='seis',
    #            series=[q_min,q_max,q_inc],
    #            continuous=True,
    #            background='o')
    fig.grdimage((data_dir + 'Figures/Q_'+str(lat_round)+'.grd'),
                cmap=data_dir + 'Figures/qs.cpt',
                projection='x4.0/0.06',
                region=[lonmin,lonmax,depmax,depmin],
                interpolation='n')
    fig.basemap(projection='x4.0/0.06',
                region=[lonmin,lonmax,depmax,depmin],
                frame=['WSne','xa1f0.5+lLongitude','ya10f10+l"Depth (km)"'],
                )
    fig.colorbar(frame=['xc' + data_dir + 'Figures/cbar_annots.txt+LQs'],
                 cmap=data_dir + 'Figures/qs.cpt',
                 position='JMR+o0.75c/0c+w7c/0.5c+n"No Data"')
    fig.savefig((data_dir + 'Figures/'+str(lat_round)+'_slice.png'))

    fig2 = pygmt.Figure()
    #pygmt.makecpt(cmap='seis',
    #            series=(str(q_min)+'/'+str(q_max)+'/'+str(q_inc)),
    #            continuous=True,
    #            background='o')
    pygmt.grdtrack(points='',
                grid='/Users/bpk/Documents/AGU_2021/Illapel_topo15.grd',
                outfile=data_dir + 'Figures/topo_track.txt',
                region=[lonmin,lonmax,depmax,depmin],
                profile=('-73/' + str(lat_round) + '/-68/' + str(lat_round) + '+i0.1'))
    topo_track = pd.read_table(data_dir + 'Figures/topo_track.txt',sep='\t',dtype=float,names=['lon','lat','dep'])
#    os.system("awk '{print $1,($3/1000)}' </Volumes/External/Tomography/Figures/topo_track.txt> /Volumes/External/Tomography/Figures/topoline.xy")
#    time.sleep(2)
    pygmt.grdtrack(points='',
                grid='/Users/bpk/Documents/BPK_Masters_2019/Illapel_Map/Illapel_Slab2_Contours.grd',
                outfile=data_dir + 'Figures/slab_track.txt',
                region=[lonmin,lonmax,depmax,depmin],
                profile=('-73/' + str(lat_round) + '/-68/' + str(lat_round) + '+i0.1'),
                interpolation='n',
                skiprows=True)
    slab = pd.read_table(data_dir + 'Figures/slab_track.txt',sep='\t',dtype=float,names=['lon','lat','dep'])
    first_row = pd.DataFrame({'lon':[-73.0],'lat':[lat_round],'dep':[(topo_track['dep'][0]/1000)]},index=[0])
    slab = pd.concat([first_row,slab]).reset_index(drop = True)
    print(slab.head())
#    os.system("awk '{print $1,$3}' </Volumes/External/Tomography/Figures/slab_track.txt> /Volumes/External/Tomography/Figures/slabline.xy")
#    time.sleep(2)
    fig2.grdimage((data_dir + 'Figures/surfgridclip_'+str(lat_round)+'.grd'),
                projection='x4.0/0.06',
                cmap=data_dir + 'Figures/qs_surf.cpt',
                region=[lonmin,lonmax,depmax,depmin],
                interpolation='n')
    fig2.grdcontour(grid=(data_dir + 'Figures/surfgridclip_'+str(lat_round)+'.grd'),
                interval=200,
                annotation='400+f5p',
                projection='x4.0/0.06',
                region=[lonmin,lonmax,depmax,depmin])
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
    fig2.colorbar(frame=['xc' + data_dir + 'Figures/cbar_annots.txt+LQs'],
                 cmap=data_dir + 'Figures/qs.cpt',
                 position='JMR+o0.5c/0c+w4.92c/0.4c+n"No Data"')
    fig2.savefig((data_dir + 'Figures/'+str(lat_round)+'_slice_surf.png'))

    fig3 = pygmt.Figure()
    pygmt.xyz2grd(x=np.array(hitcount_data['lon']),
                y=np.array(hitcount_data['dep']),
                z=np.array(hitcount_data['total_ray_dist']),
                outgrid = (data_dir + 'Figures/hitcounts_'+str(lat_round)+'.grd'),
                region=[uniqlons[0],uniqlons[-1],uniqdeps[0],uniqdeps[-1]],
                spacing=(str(lonstep)+'+e/'+str(depstep)+'+e'))
    pygmt.makecpt(cmap='seis',
                series=(str(mindist)+'/'+str(maxdist)+'/'+str((maxdist-mindist)/30)),
                continuous=True,
                background='o')
    fig3.grdimage((data_dir + 'Figures/hitcounts_'+str(lat_round)+'.grd'),
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
    fig3.savefig((data_dir + 'Figures/'+str(lat_round)+'_hitcounts.png'))

    fig4 = pygmt.Figure()
    pygmt.xyz2grd(x=np.ascontiguousarray(latslice['lon']),
                y=np.ascontiguousarray(latslice['dep']),
                z=1/qs_synth_model[latslice_boxnums.astype(int)],
                outgrid = (data_dir + 'Figures/Q_synth'+str(lat_round)+'.grd'),
                region=[uniqlons[0],uniqlons[-1],uniqdeps[0],uniqdeps[-1]],
                spacing=(str(lonstep)+'+e/'+str(depstep)+'+e'))
    fig4.grdimage((data_dir + 'Figures/Q_synth'+str(lat_round)+'.grd'),
                cmap=data_dir + 'Figures/qs.cpt',
                projection='x4.0/0.06',
                region=[lonmin,lonmax,depmax,depmin],
                interpolation='n')
    fig4.basemap(projection='x4.0/0.06',
                region=[lonmin,lonmax,depmax,depmin],
                frame=['WSne','xa1f0.5+lLongitude','ya10f10+l"Depth (km)"'],
                )
    fig4.colorbar(frame=['xc' + data_dir + 'Figures/cbar_annots.txt+LQs'],
                 cmap=data_dir + 'Figures/qs.cpt',
                 position='JMR+o0.5c/0c+w4.92c/0.4c+n"No Data"')
    fig4.savefig((data_dir + 'Figures/'+str(lat_round)+'synth_slice.png'))

    # Create ratio plots between recovered Q and synthetic Q structure

    os.system(('gmt grdmath Y -15.75 GT Y -38.25 LT ADD ' + data_dir + 'Figures/surfgridclip_' + str(lat_round) + '.grd MUL ' + str(else_qs) + ' DIV Y -15.75 LE Y -38.25 GE MUL '\
            + data_dir + 'Figures/surfgridclip_' + str(lat_round) + '.grd MUL ' + str(bar_qs) + ' DIV ADD = ' + data_dir + 'Figures/lat_ratio_' + str(lat_round) + '.grd'))
    time.sleep(5)

    fig5 = pygmt.Figure()
    fig5.grdimage((data_dir + 'Figures/lat_ratio_' + str(lat_round) + '.grd'),
                projection='x4.0/0.06',
                cmap=data_dir + 'Figures/qs_ratio.cpt',
                region=[lonmin,lonmax,depmax,depmin],
                interpolation='n')
    fig5.grdcontour(grid=(data_dir + 'Figures/lat_ratio_' + str(lat_round) + '.grd'),
                interval=data_dir + 'Figures/qs_ratio.cpt',
                annotation='0.25+f7p',
                projection='x4.0/0.06',
                region=[lonmin,lonmax,depmax,depmin])
    fig5.basemap(projection='x4.0/0.06',
                region=[lonmin,lonmax,depmax,depmin],
                frame=['WSne','xa1f1+lLongitude','ya10f5+l"Depth (km)"'],
                )
    fig5.plot(x=topo_track['lon'],y=topo_track['dep']/1000,
                projection='x4.0/0.06',
                region=[lonmin,lonmax,depmax,depmin],
                pen='thick,darkbrown')
    fig5.plot(x=slab['lon'],y=slab['dep'],
                projection='x4.0/0.06',
                region=[lonmin,lonmax,depmax,depmin],
                pen='thick,black')
    fig5.plot(x=np.array(eqs['ev_lon'],dtype=float),y=np.array(-1*eqs['ev_dep'],dtype=float),
                projection='x4.0/0.06',
                region=[lonmin,lonmax,depmax,depmin],
                style='c0.1',
                color='white',
                pen='thin,black')
    fig5.plot(x=np.array(stn_data['lon'],dtype=float),y=np.array(-1*stn_data['elev'],dtype=float),
                projection='x4.0/0.06',
                region=[lonmin,lonmax,depmax,depmin],
                style='t0.2',
                color='cyan',
                pen='thin,black')
    fig5.colorbar(frame=['xc' + data_dir + 'Figures/cbar_annots_ratio.txt+L"Qs Ratio"'],
                    cmap=data_dir + 'Figures/qs_ratio.cpt',
                    position='JMR+o0.5c/0c+w4.92c/0.4c+e+n"No Data"')
    fig5.savefig((data_dir + 'Figures/lat_ratio_' + str(lat_round) + '.png'))