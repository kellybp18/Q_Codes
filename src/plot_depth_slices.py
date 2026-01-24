import numpy as np
import pygmt
import pandas as pd
import os
import time

from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
data_dir = base_dir / "data"
fig_dir = base_dir / "figures"

map_coords = np.array([-73.0,-68.0,-34.0,-29.0])
num_boxes = 90160 # Edit for number of boxes in your tomography

latmin = -33.0
latmax = -29.5
lonmin = -73.0
lonmax = -69.0
depmin = 10
depmax = -72

q_database = pd.read_csv(data_dir / 'q_database.csv')
qs_model = pd.read_csv(data_dir / 'qs_model.csv')
qs_initial_model = (1/450)*np.ones(num_boxes)

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

dist = np.loadtxt(data_dir  / 'dist.txt')

for j in range(len(dist[:,0])):
   blockdist = dist[j,:]
   nonzerodists = blockdist[np.nonzero(blockdist)]
   hitcount = len(nonzerodists)
   totaldist = np.sum(nonzerodists)
   hitcounts = hitcounts.append({'boxnum':j+1,'hitcount':hitcount,'total_ray_dist':totaldist},ignore_index=True)

hitcounts.to_csv(data_dir / 'hitcounts.csv',index=False)
#hitcounts = pd.read_csv(data_dir / 'hitcounts.csv')

os.system('cd ' + str(fig_dir))

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
    mask_data.to_csv(data_dir / ('maskdepgrid_'+str(dep_round)+'.xyz'),header=None,index=None,sep=' ',mode='w')

    os.system(('gmt blockmean ' + str(data_dir) + '/maskdepgrid_'+str(dep_round)+'.xyz -R-73/-68/-34/-29 -I'+str(surflonstep)+'/'+str(surflatstep)+' > ' + str(data_dir) + '/maskdepgridmed_'+str(dep_round)+'.xyz'))
    time.sleep(3)
    os.system(('gmt surface ' + str(data_dir) + '/maskdepgridmed_'+str(dep_round)+'.xyz -G' + str(data_dir) + '/maskdepgridmed_'+str(dep_round)+'.grd -I'+str(surflonstep)+'/'+str(surflatstep)+' -Lu1500.0 -R-73/-68/-34/-29 -Tb1i0'))
    time.sleep(5)
    os.system(('gmt grdclip ' + str(data_dir) + '/maskdepgridmed_'+str(dep_round)+'.grd -G' + str(data_dir) + '/maskdepgridclip_'+str(dep_round)+'.grd -Sb75.0/NaN'))
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

    # Get data for station plotting

    surf_data = pd.DataFrame(depslice.loc[:,['lon','lat','Qs']])
    surf_data.to_csv(data_dir / ('surfdepgrid_'+str(dep_round)+'.xyz'),header=None,index=None,sep=' ',mode='w')

    os.system(('gmt blockmean ' + str(data_dir) + '/surfdepgrid_'+str(dep_round)+'.xyz -R-73/-68/-34/-29 -I'+str(surflonstep)+'/'+str(surflatstep)+' > ' + str(data_dir) + '/surfdepgridmed_'+str(dep_round)+'.xyz'))
    time.sleep(3)
    os.system(('gmt surface ' + str(data_dir) + '/surfdepgridmed_'+str(dep_round)+'.xyz -G' + str(data_dir) + '/surfdepgridmed_'+str(dep_round)+'.grd -I'+str(surflonstep)+'/'+str(surflatstep)+' -Lu1500.0 -R-73/-68/-34/-29 -Tb1i0'))
    time.sleep(5)
    os.system(('gmt grdmath ' + str(data_dir) + '/surfdepgridmed_'+str(dep_round)+'.grd ' + str(data_dir) + '/maskdepgridclip_'+str(dep_round)+'.grd OR = ' + str(data_dir) + '/surfmaskdepgridmed_'+str(dep_round)+'.grd'))
    time.sleep(3)
    print("Okay")

    slab = pd.read_table(data_dir / 'Illapel_Slab2_Contours.txt',sep=' ',dtype=float,names=['lon','lat','dep'])

    fig = pygmt.Figure()
    pygmt.xyz2grd(x=np.ascontiguousarray(depslice_nozero['lon']),
                y=np.ascontiguousarray(depslice_nozero['lat']),
                z=np.ascontiguousarray(depslice_nozero['Qs']),
                outgrid = (str(data_dir) + '/Qdep_'+str(dep_round)+'.grd'),
                region=[uniqlons[0],uniqlons[-1],uniqlats[0],uniqlats[-1]],
                spacing=(str(lonstep)+'+e/'+str(latstep)+'+e'))
    pygmt.grdclip((str(data_dir) + '/surfmaskdepgridmed_'+str(dep_round)+'.grd'),
                outgrid=(str(data_dir) + '/surfdepgridclip_'+str(dep_round)+'.grd'),
                below=[75,75.0])
    #pygmt.config(COLOR_NAN='white')
    #pygmt.makecpt(cmap='seis',
    #            series=[q_min,q_max,q_inc],
    #            continuous=True,
    #            background='o')
    fig.grdimage((str(data_dir) + '/Qdep_'+str(dep_round)+'.grd'),
                cmap=data_dir / 'qs.cpt',
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
    fig.colorbar(frame=['xc' + str(data_dir) + '/cbar_annots.txt+LQs'],
                 cmap=data_dir / 'qs.cpt',
                 position='JMR+o0.75c/0c+w7c/0.5c+n"No Data"')
    fig.savefig((str(fig_dir) + '/dep_'+str(-1*dep_round)+'_slice.png'))

    lonmin = -73.5

    fig2 = pygmt.Figure()
    fig2.coast(projection='m3.5c',
              region=[lonmin,lonmax,latmin,latmax],
              water='darkgray')
    fig2.grdimage((str(data_dir) + '/surfdepgridclip_'+str(dep_round)+'.grd'),
                projection='m3.5c',
                cmap=data_dir / 'qs_surf.cpt',
                region=[lonmin,lonmax,latmin,latmax],
                interpolation='n')
    fig2.grdcontour(grid=(str(data_dir) + '/surfdepgridclip_'+str(dep_round)+'.grd'),
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
    fig2.plot(data=data_dir / 'main_shock.loc',
              projection='m3.5c',
              region=[lonmin,lonmax,latmin,latmax],
              style='a0.4',
              color='yellow',
              pen='thin,black',
              incols=[1,0]
              )
    fig2.plot(data=data_dir / 'Illapel_Stns.gmt',
              projection='m3.5c',
              region=[lonmin,lonmax,latmin,latmax],
              style='d0.4',
              color='white',
              pen='thin,black',
              incols=[1,0])
    fig2.plot(data=data_dir / 'volcanos.gmt',
              projection='m3.5c',
              region=[lonmin,lonmax,latmin,latmax],
              style='t0.4',
              color='indianred2',
              pen='thin,black')
    fig2.plot(data=data_dir / 'offshore_fault_coords_no_coast.txt',
              projection='m3.5c',
              region=[lonmin,lonmax,latmin,latmax],
              pen='thin,blue')
    fig2.plot(data=data_dir / 'trench_coords.txt',
              projection='m3.5c',
              region=[lonmin,lonmax,latmin,latmax],
              pen='1.3p,black',
              style='f1.4c/0.3c+l+t+p',
              color='black')
    fig2.colorbar(frame=['xc' + str(data_dir) + '/cbar_annots.txt+LQs'],
                 cmap=data_dir / 'qs.cpt',
                 position='JMR+o0.75c/0c+w7c/0.5c+n"No Data"')
    fig2.savefig((str(fig_dir) + '/dep_'+str(dep_round)+'_slice_surf.png'))

    lonmin = -73.0

    fig3 = pygmt.Figure()
    pygmt.xyz2grd(x=np.array(hitcount_data['lon']),
                y=np.array(hitcount_data['lat']),
                z=np.array(hitcount_data['total_ray_dist']),
                outgrid = (str(data_dir) + '/hitcounts_dep_'+str(dep_round)+'.grd'),
                region=[uniqlons[0],uniqlons[-1],uniqlats[0],uniqlats[-1]],
                spacing=(str(lonstep)+'+e/'+str(latstep)+'+e'))
    pygmt.makecpt(cmap=data_dir / 'YlOrRd.cpt',
                series=(str(mindist)+'/'+str(maxdist)+'/'+str((maxdist-mindist)/30)),
                continuous=True,
                reverse=True,
                background='o')
    fig3.grdimage((str(data_dir) + '/hitcounts_dep_'+str(dep_round)+'.grd'),
                projection='m3.5c',
                region=[lonmin,lonmax,latmin,latmax],
                interpolation='n')    
    fig3.basemap(projection='m3.5c',
                region=[lonmin,lonmax,latmin,latmax],
                frame=['WSNe','a1f0.5'],
                )
    fig3.coast(projection='m3.5c',
              region=[lonmin,lonmax,latmin,latmax],
              borders='1/thick,black',
              shorelines='thick,black',
              )
    fig3.plot(data=data_dir / 'trench_coords.txt',
              projection='m3.5c',
              region=[lonmin,lonmax,latmin,latmax],
              pen='1.3p,black',
              style='f1.4c/0.3c+l+t+p',
              color='black')
    fig3.text(x=np.array(hitcount_data['lon']),
              y=np.array(hitcount_data['lat']),
              text=np.array(np.array(hitcount_data['hitcount'],dtype=int),dtype=str),
              font="7p,Helvetica,black",
              projection='m3.5c',
              region=[lonmin,lonmax,latmin,latmax])
    fig3.colorbar(frame=['x+l"Sum of Ray Distances in Box"','y+lkm'],
                 position='JMR+o0.75c/0c+w7c/0.5c')
    fig3.savefig((str(fig_dir) + '/dep_'+str(dep_round)+'_hitcounts_.png'))
