import plotly.graph_objects as go
import pandas as pd
import numpy as np
from skimage import io
from plotly.validators.scatter.marker import SymbolValidator

chosen_lat = -32.0

qs_model = pd.read_csv('/Volumes/External/Tomography/qs_model.csv')
slab = pd.read_table('/Users/bpk/Documents/AGU_2021/Illapel_Slab2_Surface.xyz',sep='\t',dtype=float,names=['lon','lat','dep'])
elev_data = pd.read_table('/Users/bpk/Documents/AGU_2021/Illapel_topo15.xyz',sep='\t',dtype=float,names=['lon','lat','elev'])
stn_data = pd.read_table('/Users/bpk/Documents/BPK_Masters_2019/AGU_Fall_Meeting_2019/Illapel_Stns.gmt',sep=' ',dtype=float,usecols=[0,1,2],names=['lat','lon','elev'])

x_data = np.array(qs_model['lon'])
y_data = np.array(qs_model['lat'])
z_data = np.array(qs_model['dep'])
q_data = np.array(qs_model['Qs'])
max_q = np.max(q_data)
min_q = np.min(q_data[q_data != 0])

print(len(q_data))
print(len(q_data[q_data >= 1000]))

for i in range(len(slab['lon'])):
    if slab['lon'][i] == -68.0:
        if i == 50:
            slab_x = np.array([slab['lon'][(i-50):(i+1)]])
            slab_y = np.array([slab['lat'][(i-50):(i+1)]])
            slab_z = np.array([slab['dep'][(i-50):(i+1)]])
        else:
            slab_x = np.append(slab_x,np.reshape([slab['lon'][(i-50):(i+1)]],(1,51)),axis=0)
            slab_y = np.append(slab_y,np.reshape([slab['lat'][(i-50):(i+1)]],(1,51)),axis=0)
            slab_z = np.append(slab_z,np.reshape([slab['dep'][(i-50):(i+1)]],(1,51)),axis=0)

fix_slab = np.where(slab_y >= -31.8)
for lat_idx in range(len(fix_slab[0])):
    if slab_z[fix_slab[0][lat_idx]][fix_slab[1][lat_idx]] <= -100.0:
        slab_z[fix_slab[0][lat_idx]][fix_slab[1][lat_idx]] = -100.0

# Pick latitude x-section
slab_line_lat = np.where(slab_y == chosen_lat)
slab_line_x = slab_x[slab_line_lat[0]][slab_line_lat[1]]
slab_line_y = slab_y[slab_line_lat[0]][slab_line_lat[1]]
slab_line_z = slab_z[slab_line_lat[0]][slab_line_lat[1]]

# Set up image on bottom of figure
map_lon = np.linspace(-73,-68,1201)
map_lat = np.linspace(-29,-34,1201)
map_x,map_y = np.meshgrid(map_lon,map_lat)
map_z = np.ones_like(map_x)*(-180)
cvals = np.reshape([elev_data['elev']],(1201,-1))+8000

# Get topographic profile
topo_lat_idxs = np.where(elev_data['lat']==chosen_lat)[0]
topo_x = np.array(elev_data['lon'][topo_lat_idxs])
topo_y = np.ones_like(topo_x)*(chosen_lat)
topo_z = np.array(elev_data['elev'][topo_lat_idxs]/1000)
print(topo_lat_idxs)
print(topo_x)
print(np.shape(topo_x),np.shape(topo_y))
print(topo_z)

# Get station data
stn_lat_idxs = stn_data[stn_data['lat'] >= (chosen_lat-0.5)]
stn_lats = stn_lat_idxs[stn_lat_idxs['lat'] <= (chosen_lat+0.5)]
stn_x = np.array(stn_lats['lon'])
stn_y = np.ones_like(stn_x)*chosen_lat
stn_z = np.array(stn_lats['elev'])

fig = go.Figure()

fig.add_trace(go.Volume(
    x=x_data, #.flatten(),
    y=y_data, #.flatten(),
    z=z_data, #.flatten(),
    value=q_data,#.flatten(),
    #isomin=0,
    #isomax=1,
    #opacity=0.1,
    #cmin=0,
    #cmax=max_q,
    caps=dict(z=dict(show=False)),
    surface=dict(count=20,show=False),
    slices=dict(y=dict(fill=1,locations=[chosen_lat],show=True)),
    flatshading=True,
    lightposition=dict(x=0,y=-4,z=0),
    colorscale=[[0,'rgb(180,180,180)'],[(min_q/max_q),'rgb(180,180,180)'],
                [min_q/max_q,'rgb(255,0,0)'],[(200/max_q),'rgb(255,165,0)'],
                [(200/max_q),'rgb(255,165,0)'],[(400/max_q),'rgb(255,255,0)'],
                [(400/max_q),'rgb(255,255,0)'],[(600/max_q),'rgb(0,255,0)'],
                [(600/max_q),'rgb(0,255,0)'],[(800/max_q),'rgb(0,255,255)'],
                [(800/max_q),'rgb(0,255,255)'],[(1000/max_q),'rgb(0,0,255)'],
                [(1000/max_q),'rgb(0,0,255)'],[1,'rgb(0,0,255)']],
    colorbar=dict(x=0.7,title=dict(text='Qs',font=dict(size=21),side='top'),len=0.5,tickfont=dict(size=14)),
    opacityscale=[[0,0],[(min_q/max_q),0],[(min_q/max_q),1],[1,1]],
    ))

fig.add_trace(go.Surface(x=slab_x,y=slab_y,z=slab_z,opacity=1,connectgaps=True,colorscale=[[0,'rgb(0,0,0)'],[1,'rgb(0,0,0)']],showscale=False,visible=False))

fig.add_trace(go.Surface(x=map_x,y=map_y,z=map_z,surfacecolor=cvals,cmin=0,cmax=16000,showscale=False,
                         colorscale=[[0,'rgb(0,2,12)'],[1/16,'rgb(0,2,12)'],
                                     [1/16,'rgb(0,7,37)'],[2/16,'rgb(0,7,37)'],
                                     [2/16,'rgb(0,45,88)'],[3/16,'rgb(0,45,88)'],
                                     [3/16,'rgb(0,115,163)'],[4/16,'rgb(0,115,163)'],
                                     [4/16,'rgb(43,174,192)'],[5/16,'rgb(43,174,192)'],
                                     [5/16,'rgb(129,221,176)'],[6/16,'rgb(129,221,176)'],
                                     [6/16,'rgb(192,247,190)'],[7/16,'rgb(192,247,190)'],
                                     [7/16,'rgb(231,252,233)'],[8/16,'rgb(231,252,233)'],
                                     [8/16,'rgb(95,110,50)'],[8.5/16,'rgb(95,110,50)'],
                                     [8.5/16,'rgb(133,113,55)'],[9/16,'rgb(133,113,55)'],
                                     [9/16,'rgb(172,152,70)'],[10/16,'rgb(172,152,70)'],
                                     [10/16,'rgb(224,204,90)'],[11/16,'rgb(224,204,90)'],
                                     [11/16,'rgb(250,232,113)'],[12/16,'rgb(250,232,113)'],
                                     [12/16,'rgb(251,236,139)'],[13/16,'rgb(251,236,139)'],
                                     [13/16,'rgb(252,240,164)'],[14/16,'rgb(252,240,164)'],
                                     [14/16,'rgb(252,246,197)'],[15/16,'rgb(252,246,197)'],
                                     [15/16,'rgb(254,252,236)'],[1,'rgb(254,252,236)']]
                        )
             )

fig.add_trace(go.Scatter3d(x=slab_line_x[0], y=slab_line_y[0], z=slab_line_z[0],name='Slab Profile',
    marker=dict(
        size=0.1
    ),
    line=dict(
        color='black',
        width=10
    ),
    showlegend=False
))

fig.add_trace(go.Scatter3d(x=[-73,-68], y=[chosen_lat,chosen_lat], z=[-180,-180],name='Cross-Section Line',
    marker=dict(
        size=0.1
    ),
    line=dict(
        color='red',
        width=10
    ),
    showlegend=False
))

fig.add_trace(go.Scatter3d(x=topo_x, y=topo_y, z=topo_z,name='Topographic Profile',
    marker=dict(
        size=0.1
    ),
    line=dict(
        color='burlywood',
        width=10
    ),
    showlegend=False
))

fig.add_trace(go.Scatter3d(x=stn_x, y=stn_y, z=stn_z,
    marker=dict(
        size=10,
        color='rgb(155,48,255)',
        line_color='black',
        line_width=8,
        symbol='diamond'
    ),
    line=dict(
        width=0
    ),
    showlegend=False
))

fig.update_layout(title=dict(text=('Qs Tomography Cross Section at '+str(chosen_lat)+'° Latitude'),
                  x=0.5,y=0.85,font=dict(size=26)),
                  scene = dict(xaxis_title='Longitude (°)',
                               yaxis_title='Latitude (°)',
                               zaxis_title='Depth (km)',
                               xaxis = dict(backgroundcolor="white",
                                            gridcolor="black",
                                            showbackground=True,
                                            zerolinecolor="white",
                                            range=[-73,-68]),
                               yaxis = dict(backgroundcolor="white",
                                            gridcolor="black",
                                            showbackground=True,
                                            zerolinecolor="white",
                                            range=[-34,-29]),
                               zaxis = dict(backgroundcolor="white",
                                            gridcolor="black",
                                            showbackground=True,
                                            range=[-180,np.max(topo_z)])
                              ),
                               scene_camera = dict(eye=dict(x=0., y=-2, z=0.46)),
                 )
#fig.update_scenes(zaxis_autorange="reversed")

fig.show()

#fig.write_image('~/Documents/AGU_2021/Tomo_Slice_'+str(chosen_lat)[1:])