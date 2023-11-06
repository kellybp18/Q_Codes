import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

q_database = pd.read_csv('/Volumes/External/Attenuation/q_database.csv')
good_data = q_database[q_database['judge_result'] == "GOOD"]
max_amp = np.array(good_data['max_amp'])
freq_of_maxamp = np.array(good_data['t7'])
stacked_qs = np.array(good_data['stacked_qs'])

three_d_array = np.vstack((np.round(freq_of_maxamp,5),np.round(max_amp,5),np.round(stacked_qs,5)))
np.savetxt('/Volumes/External/three_d.txt',three_d_array.T,fmt='%.5f')

new_array = pd.read_table('/Volumes/External/three_d_new.txt',sep='\t',dtype=float,names=['freq','amp','qs'])
new_array = new_array.sort_values(by=['amp','freq'],ascending=[True,True],na_position='first')
print(new_array['freq'])
print(new_array['amp'])
print(new_array['qs'][0:110])
print(new_array['freq'][1000000],new_array['amp'][1000000],new_array['qs'][1000000])
x = np.arange(0.0,15.01,0.01)
y = np.arange(4.0,16.01,0.01)
z = np.reshape(np.array(new_array['qs']),(1501,1201))
# x_range = np.arange(0.0,15.001,0.001)
# y_range = np.arange(0.0,16.001,0.001)
# X,Y = np.meshgrid(x_range,y_range)
# Z = np.zeros_like(X)

# for i,Qs in enumerate(stacked_qs):
#     print(i)
#     idx = np.where((X == np.round(freq_of_maxamp[i],3)) & (Y == np.round(max_amp[i],3)))
#     Z[idx] = Qs

# np.savetxt('/Volumes/External/z_mesh.txt',Z)

f1 = plt.figure(1)
plt.scatter(freq_of_maxamp,max_amp,c='blue')
plt.xlabel('Frequency of Max Stacked Amplitude (Hz)')
plt.ylabel('Log of Max Stacked Amplitude')
plt.show()
plt.savefig('/Volumes/External/Figure_1_WQ.png')

mag = np.array(good_data['mag'])
f2 = plt.figure(2)
plt.scatter(mag,max_amp,c='green')
plt.xlabel('Earthquake Magnitude')
plt.ylabel('Log of Max Stacked Amplitude')
plt.show()
plt.savefig('/Volumes/External/amp_vs_mag.png')
# # fig2, ax2 = plt.subplots(subplot_kw={"projection": "3d"})

# # # Make data.
# # X = np.arange(-5, 5, 0.25)
# # Y = np.arange(-5, 5, 0.25)
# # X, Y = np.meshgrid(X, Y)
# # R = np.sqrt(X**2 + Y**2)
# # Z = np.sin(R)

# # # Plot the surface.
# # surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,
# #                        linewidth=0, antialiased=False)

# # # Customize the z axis.
# # ax.set_zlim(-1.01, 1.01)
# # ax.zaxis.set_major_locator(LinearLocator(10))
# # # A StrMethodFormatter is used automatically
# # ax.zaxis.set_major_formatter('{x:.02f}')

# # # Add a color bar which maps values to colors.
# # fig.colorbar(surf, shrink=0.5, aspect=5)

# # plt.show()

fig2 = go.Figure(data=[go.Surface(x = x,
                                  y = y,
                                  z = z,
                                  colorscale = 'viridis',
                                  colorbar_title = 'Stacked Qs')])
fig2.update_layout(scene_xaxis_title="Frequency of Max Stacked Amplitude (Hz)",
    scene_yaxis_title="Log of Max Stacked Amplitude",
    scene_zaxis_title="Stacked Qs",
    font=dict(
        family="Courier New, monospace",
        size=18,
        color="black"
    )
)
fig2.show()