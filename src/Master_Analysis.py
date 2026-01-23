import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

q_database = pd.read_csv('/Volumes/External/Attenuation/q_database.csv')
good_data = q_database[q_database['judge_result'] == "GOOD"]
bad_data = q_database[q_database['judge_result'] == "BAD"]
print('Number of good rays: ',len(good_data['judge_result']))
print('Number of bad rays: ',len(bad_data['judge_result']))
print('Percent Good: ',(float(len(good_data['judge_result']))/(float(len(bad_data['judge_result'])) + float(len(good_data['judge_result']))))*100)
print('Number of rays that had outliers removed: ',len(q_database[q_database['outliers_removed'] == 'YES']))
print('Average of Stacked Qs: ',np.mean(good_data['stacked_qs']))
print('Average of Mean Qs: ',np.mean(good_data['mean_qs']))
print('Average of Standard Deviations of Qs: ',np.mean(good_data['stdev_qs']))

# Qs vs. Magnitude
plt.figure('fig1')
plt.scatter(good_data['mag'],good_data['mean_qs'])
plt.xlabel('Magnitude (M$_W$)')
plt.ylabel('Mean Q$_S$')
plt.title('Ray Path Q$_S$ vs. Source Magnitude')
plt.savefig('/Volumes/External/Attenuation/Figures/Qs_vs_Mag.png')
plt.show()

# Proportion of good and bad data per station
stations = ['IL01','IL02','IL03','IL04','IL05','IL06','IL07','IL08', \
            'IL09','IL11','IL12','IL13','IL14','IL15','IL16','IL17', \
            'IL18','IL19','IL20','IL21','IL22','IL23']

good_count = np.zeros(22)
bad_count = np.zeros(22)

for count,stn in enumerate(stations):
    good_count[count] = len(good_data[good_data['stn_id'] == stn])
    bad_count[count] = len(bad_data[bad_data['stn_id'] == stn])


plt.figure('fig2')
plt.bar(stations,good_count,color='blue',label='Good Data')
plt.bar(stations,bad_count,color='red',bottom=good_count,label='Bad Data')
plt.legend()
plt.xlabel('Station')
plt.ylabel('Number of Events')
plt.title('Proportion of Good and Bad Data Per Station')
plt.savefig('/Volumes/External/Attenuation/Figures/Stn_Good_Bad_Rays.png')
plt.show()

# Qs vs. Depth
plt.figure('fig3')
plt.scatter(good_data['ev_dep'],good_data['mean_qs'])
plt.xlabel('Earthquake Depth (km)')
plt.ylabel('Mean Q$_S$')
plt.title('Ray Path Q$_S$ vs. Source Depth')
plt.savefig('/Volumes/External/Attenuation/Figures/Qs_vs_Depth.png')
plt.show()

# Qs vs. Distance
# csn Chile (csn.uchile.cl) (IRIS network code C)
# t7 and t8 histogram overall and with station
plt.figure('fig4',figsize=(30,9))
binBoundaries = np.linspace(0,20,21)

plt.subplot(1,2,1)
plt.hist(good_data['t7'],bins=binBoundaries,range = (0,20),color='orange',edgecolor='black')
plt.xlabel('Frequency Band Start Point (Hz)')
plt.ylabel('Number of Events')
plt.title('Histogram of T7 Picks')

plt.subplot(1,2,2)
plt.hist(good_data['t8'],bins=binBoundaries,range = (0,20),color='cyan',edgecolor='black')
plt.xlabel('Frequency Band End Point (Hz)')
plt.ylabel('Number of Events')
plt.title('Histogram of T8 Picks')
plt.savefig('/Volumes/External/Attenuation/Figures/t7_t8_histograms.png')
plt.show()

# Event 3D Map
fig = go.Figure(data=[go.Scatter3d(x=q_database["ev_lon"], y=q_database["ev_lat"], z=q_database["ev_dep"],
                                   marker=dict(size=6,
                                               color=q_database["mag"],  # set color to an array/list of desired values
                                               colorscale='Viridis'      # choose a colorscale
                                              ),
                                   mode='markers',name='Magnitude (Mw)')])
fig.update_layout(xaxis_title="Longitude (deg)",
    yaxis_title="Latitude (deg)",
    font=dict(
        family="Courier New, monospace",
        size=18,
        color="black"
    )
)
fig.update_scenes(zaxis_autorange="reversed")
fig.show()

# Histogram of stdev
plt.figure('fig5')
stdev_bins = np.linspace(0,7500,151)
plt.hist(q_database['stdev_qs'],bins=stdev_bins,color='cyan',edgecolor='black')
plt.xlabel('Standard Deviation of Qs')
plt.ylabel('Number of Rays')
plt.title('Histogram of Standard Deviation of Qs')
plt.savefig('/Volumes/External/Attenuation/Figures/stdev_histogram.png')
plt.show()

plt.figure('fig6')
mean_qs_bins = np.linspace(75,1500,15)
plt.hist(good_data['mean_qs'],bins=mean_qs_bins,color='cyan',edgecolor='black')
plt.xlabel('Mean Qs')
plt.ylabel('Number of Rays')
plt.title('Histogram of Mean Qs')
plt.savefig('/Volumes/External/Attenuation/Figures/Mean_Qs_histogram.png')
plt.show()

plt.figure('fig7')
mean_qs_bins = np.linspace(75,1500,15)
plt.hist(good_data['stacked_qs'],bins=mean_qs_bins,color='cyan',edgecolor='black')
plt.xlabel('Stacked Qs')
plt.ylabel('Number of Rays')
plt.title('Histogram of Stacked Qs')
plt.savefig('/Volumes/External/Attenuation/Figures/Stacked_Qs_histogram.png')
plt.show()

plt.figure('fig8')
linefit_coeffs = np.polyfit(good_data['mean_qs'],good_data['stdev_qs'],1)
print('Linear regression line is y =',linefit_coeffs[0],'* x +',linefit_coeffs[1])
linefit_y_hats = np.polyval(linefit_coeffs,good_data['mean_qs'])
plt.scatter(good_data['mean_qs'],good_data['stdev_qs'],label='Stdev per mean Qs')
plt.plot(good_data['mean_qs'],linefit_y_hats,c='r',label='Linear Fit')
plt.xlabel('Mean Qs')
plt.ylabel('Standard Deviation of Qs')
plt.title('Standard Deviation of Qs vs. Mean Qs')
plt.legend()
plt.savefig('/Volumes/External/Attenuation/Figures/Mean_Qs_vs_stdev.png')
plt.show()
