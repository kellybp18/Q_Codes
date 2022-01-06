import plotly.graph_objects as go
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def make_vert_slice(lat_slice):
    """"""
    qs_model = pd.read_csv('/Volumes/External/Tomography/qs_model.csv')
    slab = pd.read_table('/Users/bpk/Documents/BPK_Masters_2019/Illapel_Map/Illapel_Slab2_Contours.txt',sep=' ',dtype=float,names=['lon','lat','dep'])
    lon = qs_model['lon']
    lat = qs_model['lat']
    dep = qs_model['dep']
    qs = qs_model['Qs']
    round_lats = np.round(np.array(lat),decimals=1)
    lat_idxs = np.where(round_lats == np.round(lat_slice,1))[0]

    x_slice = lon[lat_idxs]
    z_slice = dep[lat_idxs]
    q_slice = (qs[lat_idxs]).reset_index(drop=True)

    #print(q_slice)

    x_grid = np.linspace(-72.89130435,-68.10869565,23)
    z_grid = np.linspace(-4.5,-175.5,20)
    q_mesh = np.zeros((23,20))

    count = 0
    for k in range(len(z_grid)):
        for i in range(len(x_grid)):
            q_mesh[i,k] = q_slice[count]
            count = count + 1

    x_mesh,z_mesh = np.meshgrid(x_grid,z_grid)

    round_lats_slab = np.array(slab['lat'])
    lat_idxs_slab = np.where(round_lats_slab == lat_slice)[0]
    slabline_x = slab['lon'][lat_idxs_slab]
    slabline_y = slab['dep'][lat_idxs_slab]

    plt.pcolormesh(x_mesh,z_mesh,q_mesh.T,shading='nearest')
    plt.colorbar()

    plt.plot(slabline_x,slabline_y,color='black',linewidth=3)
    plt.show()

make_vert_slice(-31.5000)
make_vert_slice(-31.3000)