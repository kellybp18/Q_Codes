# Code to plot the depth-slice resolution test in GMT. 
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
structure = 'inverted_bar'

lonmin = -73.0
lonmax = -69.0
latmin = -33.0
latmax = -29.5
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
qs_synth_model = np.concatenate(((1/else_qs)*np.ones(6762),(1/bar_qs)*np.ones(11270),(1/else_qs)*np.ones(72128)))#np.loadtxt(data_dir + 'm0_synth_new.txt')

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
latstep = (uniqlats[1] - uniqlats[0])
surflonstep = round(lonstep/16,8)
surflatstep = round(latstep/16,8)
print(surflonstep,surflatstep)

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

for i in uniqdeps:
    lonmin = -73.0
    depslice = qs_model[qs_model['dep'] == i]
    depslice_nozero = depslice[depslice['Qs'] != 0]
    np_depslice_nozero = np.array(depslice[depslice['Qs'] != 0])
    if np_depslice_nozero.size == 0:
        continue
    currentqmin = np.min(depslice['Qs'])
    dep_round = np.round(i,2)

    mask_data = pd.DataFrame(depslice.loc[:,['lon','lat','Qs']])
    mask_data.to_csv((data_dir + 'Figures/maskdepgrid_'+str(dep_round)+'.xyz'),header=None,index=None,sep=' ',mode='w')

    os.system(('gmt blockmean ' + data_dir + 'Figures/maskdepgrid_'+str(dep_round)+'.xyz -R-73/-68/-34/-29 -I'+str(surflonstep)+'/'+str(surflatstep)+' > ' + data_dir + 'Figures/maskdepgridmed_'+str(dep_round)+'.xyz'))
    time.sleep(3)
    os.system(('gmt surface ' + data_dir + 'Figures/maskdepgridmed_'+str(dep_round)+'.xyz -G' + data_dir + 'Figures/maskdepgridmed_'+str(dep_round)+'.grd -I'+str(surflonstep)+'/'+str(surflatstep)+' -Lu1500.0 -R-73/-68/-34/-29 -Tb1i0'))
    time.sleep(5)
    os.system(('gmt grdclip ' + data_dir + 'Figures/maskdepgridmed_'+str(dep_round)+'.grd -G' + data_dir + 'Figures/maskdepgridclip_'+str(dep_round)+'.grd -Sb75.0/NaN'))
    time.sleep(5)

    depslice_boxnums = np.array(depslice['box_num'])
    for dbox in depslice_boxnums:
        if depslice.loc[int(dbox-1),'Qs'] == 0.0:
            depslice.loc[int(dbox-1),'Qs'] = 1/(qs_initial_model[int(dbox-1)])

    hitcount_boxes = hitcounts.loc[depslice_boxnums-1,:]
    hitcount_data = pd.DataFrame(depslice.loc[:,['lon','lat']])
    hitcount_data = hitcount_data.join(hitcount_boxes)
    mindist = np.min(hitcount_data['total_ray_dist'])
    maxdist = np.max(hitcount_data['total_ray_dist'])

    # Get data for earthquake plotting of earthquakes within one box width
    # half_lonstep = lonstep/2
    # minlat = lat_round - half_lonstep
    # maxlat = lat_round + half_lonstep
    # hold_eqs = unique_q_list[unique_q_list['ev_lat'] >= minlat]
    # eqs = hold_eqs[hold_eqs['ev_lat'] <= maxlat]

    # Get data for station plotting

    surf_data = pd.DataFrame(depslice.loc[:,['lon','lat','Qs']])
    surf_data.to_csv((data_dir + 'Figures/surfdepgrid_'+str(dep_round)+'.xyz'),header=None,index=None,sep=' ',mode='w')

    os.system(('gmt blockmean ' + data_dir + 'Figures/surfdepgrid_'+str(dep_round)+'.xyz -R-73/-68/-34/-29 -I'+str(surflonstep)+'/'+str(surflatstep)+' > ' + data_dir + 'Figures/surfdepgridmed_'+str(dep_round)+'.xyz'))
    time.sleep(3)
    os.system(('gmt surface ' + data_dir + 'Figures/surfdepgridmed_'+str(dep_round)+'.xyz -G' + data_dir + 'Figures/surfdepgridmed_'+str(dep_round)+'.grd -I'+str(surflonstep)+'/'+str(surflatstep)+' -Lu1500.0 -R-73/-68/-34/-29 -Tb1i0'))
    time.sleep(5)
    os.system(('gmt grdmath ' + data_dir + 'Figures/surfdepgridmed_'+str(dep_round)+'.grd ' + data_dir + 'Figures/maskdepgridclip_'+str(dep_round)+'.grd OR = ' + data_dir + 'Figures/surfmaskdepgridmed_'+str(dep_round)+'.grd'))
    time.sleep(3)
    print("Okay")

    slab = pd.read_table('/Users/bpk/Documents/BPK_Masters_2019/Illapel_Map/Illapel_Slab2_Contours.txt',sep=' ',dtype=float,names=['lon','lat','dep'])

    fig = pygmt.Figure()
    pygmt.xyz2grd(x=np.ascontiguousarray(depslice_nozero['lon']),
                y=np.ascontiguousarray(depslice_nozero['lat']),
                z=np.ascontiguousarray(depslice_nozero['Qs']),
                outgrid = (data_dir + 'Figures/Qdep_'+str(dep_round)+'.grd'),
                region=[uniqlons[0],uniqlons[-1],uniqlats[0],uniqlats[-1]],
                spacing=(str(lonstep)+'+e/'+str(latstep)+'+e'))
    pygmt.grdclip((data_dir + 'Figures/surfmaskdepgridmed_'+str(dep_round)+'.grd'),
                outgrid=(data_dir + 'Figures/surfdepgridclip_'+str(dep_round)+'.grd'),
                below=[75,75.0])
    #pygmt.config(COLOR_NAN='white')
    #pygmt.makecpt(cmap='seis',
    #            series=[q_min,q_max,q_inc],
    #            continuous=True,
    #            background='o')
    fig.grdimage((data_dir + 'Figures/Qdep_'+str(dep_round)+'.grd'),
                cmap=data_dir + 'Figures/qs.cpt',
                projection='m3.5c',
                region=[lonmin,lonmax,latmin,latmax],
                interpolation='n')
    fig.basemap(projection='m3.5c',
                region=[lonmin,lonmax,latmin,latmax],
                frame=['WSNe','a1f0.5'],
                )
    fig.coast(projection='m3.5c',
              region=[lonmin,lonmax,latmin,latmax],
              borders='1/thin,black',
              shorelines='thin,black'
              )
    fig.plot(data='/Users/bpk/Documents/AGU_2021/Illapel_Slab_20.txt',projection='m3.5c',region=[lonmin,lonmax,latmin,latmax],pen='thick,white')
    fig.plot(data='/Users/bpk/Documents/AGU_2021/Illapel_Slab_40.txt',projection='m3.5c',region=[lonmin,lonmax,latmin,latmax],pen='thick,white')
    fig.plot(data='/Users/bpk/Documents/AGU_2021/Illapel_Slab_60.txt',projection='m3.5c',region=[lonmin,lonmax,latmin,latmax],pen='thick,white')
    fig.plot(data='/Users/bpk/Documents/AGU_2021/Illapel_Slab_80.txt',projection='m3.5c',region=[lonmin,lonmax,latmin,latmax],pen='thick,white')
    fig.plot(data='/Users/bpk/Documents/AGU_2021/Illapel_Slab_100.txt',projection='m3.5c',region=[lonmin,lonmax,latmin,latmax],pen='thick,white')
    # fig.plot(data='/Users/bpk/Documents/AGU_2021/Illapel_Slab_120.txt',projection='m3.5c',region=[lonmin,lonmax,latmin,latmax],pen='thick,white')
    # fig.plot(data='/Users/bpk/Documents/AGU_2021/Illapel_Slab_140.txt',projection='m3.5c',region=[lonmin,lonmax,latmin,latmax],pen='thick,white')
    # fig.plot(data='/Users/bpk/Documents/AGU_2021/Illapel_Slab_160.txt',projection='m3.5c',region=[lonmin,lonmax,latmin,latmax],pen='thick,white')

    fig.colorbar(frame=['xc' + data_dir + 'Figures/cbar_annots.txt+LQs'],
                 cmap=data_dir + 'Figures/qs.cpt',
                 position='JMR+o0.75c/0c+w7c/0.5c+n"No Data"')
    fig.savefig((data_dir + 'Figures/dep_'+str(-1*dep_round)+'_slice.png'))

    fig2 = pygmt.Figure()
    # fig2.coast(projection='m3.5c',
    #           region=[lonmin,lonmax,latmin,latmax],
    #           water='darkgray')
    fig2.grdimage((data_dir + 'Figures/surfdepgridclip_'+str(dep_round)+'.grd'),
                projection='m3.5c',
                cmap=data_dir + 'Figures/qs_surf.cpt',
                region=[lonmin,lonmax,latmin,latmax],
                interpolation='n')
    fig2.grdcontour(grid=(data_dir + 'Figures/surfdepgridclip_'+str(dep_round)+'.grd'),
                interval=200,
                annotation='400+f5p',
                projection='m3.5c',
                region=[lonmin,lonmax,latmin,latmax])
    fig2.basemap(projection='m3.5c',
                region=[lonmin,lonmax,latmin,latmax],
                frame=['WSNe','a1f0.5'],
                )
    fig2.coast(projection='m3.5c',
              region=[lonmin,lonmax,latmin,latmax],
              borders='1/thick,black',
              shorelines='thick,black',
              )
    # fig2.plot(data='/Users/bpk/Documents/AGU_2021/Illapel_Slab_20.txt',projection='m3.5c',region=[lonmin,lonmax,latmin,latmax],pen='thick,white')
    # fig2.plot(data='/Users/bpk/Documents/AGU_2021/Illapel_Slab_40.txt',projection='m3.5c',region=[lonmin,lonmax,latmin,latmax],pen='thick,white')
    # fig2.plot(data='/Users/bpk/Documents/AGU_2021/Illapel_Slab_60.txt',projection='m3.5c',region=[lonmin,lonmax,latmin,latmax],pen='thick,white')
    # fig2.plot(data='/Users/bpk/Documents/AGU_2021/Illapel_Slab_80.txt',projection='m3.5c',region=[lonmin,lonmax,latmin,latmax],pen='thick,white')
    # fig2.plot(data='/Users/bpk/Documents/AGU_2021/Illapel_Slab_100.txt',projection='m3.5c',region=[lonmin,lonmax,latmin,latmax],pen='thick,white')
    # # fig2.plot(data='/Users/bpk/Documents/AGU_2021/Illapel_Slab_120.txt',projection='m3.5c',region=[lonmin,lonmax,latmin,latmax],pen='thick,white')
    # # fig2.plot(data='/Users/bpk/Documents/AGU_2021/Illapel_Slab_140.txt',projection='m3.5c',region=[lonmin,lonmax,latmin,latmax],pen='thick,white')
    # # fig2.plot(data='/Users/bpk/Documents/AGU_2021/Illapel_Slab_160.txt',projection='m3.5c',region=[lonmin,lonmax,latmin,latmax],pen='thick,white')
    # fig2.plot(data='/Users/bpk/Documents/BPK_Masters_2019/Illapel_Events/main_shock.loc',
    #           projection='m3.5c',
    #           region=[lonmin,lonmax,latmin,latmax],
    #           style='a0.4',
    #           color='yellow',
    #           pen='thin,black',
    #           incols=[1,0]
    #           )
    fig2.plot(data='/Users/bpk/Documents/BPK_Masters_2019/AGU_Fall_Meeting_2019/Illapel_Stns.gmt',
              projection='m3.5c',
              region=[lonmin,lonmax,latmin,latmax],
              style='d0.4',
              color='white',
              pen='thin,black',
              incols=[1,0])
    fig2.plot(data='/Users/bpk/Documents/BPK_Masters_2019/Illapel_Map/volcanos.gmt',
              projection='m3.5c',
              region=[lonmin,lonmax,latmin,latmax],
              style='t0.4',
              color='indianred2',
              pen='thin,black')
    # fig2.plot(data='/Volumes/External/Tomography/Figures/chile_offshore_faults/seafloor_faults/offshore_fault_coords_no_coast.txt',
    #           projection='m3.5c',
    #           region=[lonmin,lonmax,latmin,latmax],
    #           pen='thin,blue')
    fig2.plot(data='/Volumes/External/Tomography/Figures/chile_offshore_faults/trench_coords.txt',
              projection='m3.5c',
              region=[lonmin,lonmax,latmin,latmax],
              pen='1.3p,black',
              style='f1.4c/0.3c+l+t+p',
              color='black')
    fig2.colorbar(frame=['xc' + data_dir + 'Figures/cbar_annots.txt+LQs'],
                 cmap=data_dir + 'Figures/qs.cpt',
                 position='JMR+o0.75c/0c+w7c/0.5c+n"No Data"')
    fig2.savefig((data_dir + 'Figures/dep_'+str(dep_round)+'_slice_surf.png'))

    fig4 = pygmt.Figure()
    pygmt.xyz2grd(x=np.ascontiguousarray(depslice['lon']),
                y=np.ascontiguousarray(depslice['lat']),
                z=1/qs_synth_model[depslice_boxnums.astype(int)],
                outgrid = (data_dir + 'Figures/Q_synth'+str(dep_round)+'.grd'),
                region=[uniqlons[0],uniqlons[-1],uniqlats[0],uniqlats[-1]],
                spacing=(str(lonstep)+'+e/'+str(latstep)+'+e'))
    fig4.grdimage((data_dir + 'Figures/Q_synth'+str(dep_round)+'.grd'),
                cmap=data_dir + 'Figures/qs.cpt',
                projection='m3.5',
                region=[lonmin,lonmax,latmin,latmax],
                interpolation='n')
    fig4.basemap(projection='m3.5',
                region=[lonmin,lonmax,latmin,latmax],
                frame=['WSNe','a1f0.5'],
                )
    fig4.coast(projection='m3.5c',
              region=[lonmin,lonmax,latmin,latmax],
              borders='1/thick,black',
              shorelines='thick,black',
              )
    fig4.colorbar(frame=['xc' + data_dir + 'Figures/cbar_annots.txt+LQs'],
                 cmap=data_dir + 'Figures/qs.cpt',
                 position='JMR+o0.75c/0c+w7c/0.5c+n"No Data"')
    fig4.savefig((data_dir + 'Figures/dep_'+str(dep_round)+'synth_slice.png'))

    # Create ratio plots between recovered Q and synthetic Q structure

    if dep_round > -13.5 or dep_round < -36.0:
        os.system(('gmt grdmath ' + data_dir + 'Figures/surfdepgridclip_'+str(dep_round)+'.grd ' + str(else_qs) + ' DIV = ' + data_dir + 'Figures/depratio_'+str(dep_round)+'.grd'))
        time.sleep(3)
    else:
        os.system(('gmt grdmath ' + data_dir + 'Figures/surfdepgridclip_'+str(dep_round)+'.grd ' + str(bar_qs) + ' DIV = ' + data_dir + 'Figures/depratio_'+str(dep_round)+'.grd'))
        time.sleep(3)

    fig5 = pygmt.Figure()
    fig5.grdimage((data_dir + 'Figures/depratio_'+str(dep_round)+'.grd'),
                cmap=data_dir + 'Figures/qs_ratio.cpt',
                projection='m3.5',
                region=[lonmin,lonmax,latmin,latmax],
                interpolation='n')
    fig5.grdcontour(grid=(data_dir + 'Figures/depratio_'+str(dep_round)+'.grd'),
                interval=data_dir + 'Figures/qs_ratio.cpt',
                projection='m3.5c',
                region=[lonmin,lonmax,latmin,latmax])
    fig5.basemap(projection='m3.5',
                region=[lonmin,lonmax,latmin,latmax],
                frame=['WSNe','a1f0.5'],
                )
    fig5.coast(projection='m3.5c',
              region=[lonmin,lonmax,latmin,latmax],
              borders='1/thick,black',
              shorelines='thick,black',
              )
    fig5.plot(data='/Users/bpk/Documents/BPK_Masters_2019/AGU_Fall_Meeting_2019/Illapel_Stns.gmt',
              projection='m3.5c',
              region=[lonmin,lonmax,latmin,latmax],
              style='d0.4',
              color='white',
              pen='thin,black',
              incols=[1,0])
    fig5.plot(data='/Volumes/External/Tomography/Figures/chile_offshore_faults/trench_coords.txt',
              projection='m3.5c',
              region=[lonmin,lonmax,latmin,latmax],
              pen='1.3p,black',
              style='f1.4c/0.3c+l+t+p',
              color='black')
    fig5.colorbar(frame=['xc' + data_dir + 'Figures/cbar_annots_ratio.txt+L"Qs Ratio"'],
                 cmap=data_dir + 'Figures/qs_ratio.cpt',
                 position='JMR+o0.75c/0c+w7c/0.5c+e+n"No Data"')
    fig5.savefig((data_dir + 'Figures/depratio_'+str(dep_round)+'.png'))
