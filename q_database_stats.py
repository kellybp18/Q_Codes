import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime

q_database = pd.read_csv('/Volumes/External/Attenuation/q_database.csv')
qs_model = pd.read_csv('/Volumes/External/Tomography/qs_model.csv')

q_database_num_only = q_database.copy()
q_database_num_only.loc[q_database_num_only['judge_result'] == 'GOOD', 'judge_result'] = 1.0
q_database_num_only.loc[q_database_num_only['judge_result'] == 'BAD', 'judge_result'] = 0.0
q_database_num_only.loc[q_database_num_only['outliers_removed'] == 'YES', 'outliers_removed'] = 1.0
q_database_num_only.loc[q_database_num_only['outliers_removed'] == 'NO', 'outliers_removed'] = 0.0
q_database_num_only = q_database_num_only.astype({'judge_result': float, 'outliers_removed': float})
q_database_num_only.drop(['ev_id','stn_id'],axis=1)

num_only_means = q_database_num_only.mean()
num_only_sds = np.sqrt(q_database_num_only.var())
num_only_norm = (q_database_num_only - num_only_means)/num_only_sds

NUM_ONLY_CORR_MATRIX = num_only_norm.corr().round(5)
NUM_ONLY_CORR_MATRIX.style.background_gradient(cmap = 'RdYlGn',vmin=-1,vmax=1).to_excel('/Volumes/External/Attenuation/q_database_corr_matrix.xlsx',engine='openpyxl')

good_rays = q_database[q_database['judge_result'] == 'GOOD']

# Qs vs. Time
events = good_rays['ev_id']
qs = good_rays['stacked_qs']
event_dates = [datetime.datetime.strptime(date[0:-4], '%y%j_%H_%M_%S').date() for date in events]
print(event_dates[0:3])

fig,ax = plt.subplots()
ax.set_axisbelow(True)
fig.set_figwidth(10)
plt.grid(color='black')
plt.scatter(event_dates,qs,c=qs,edgecolor='black',cmap='viridis_r')
plt.xlabel('Date')
plt.ylabel('Ray Path Qs')
plt.colorbar(label='Qs')
plt.savefig('/Volumes/External/Attenuation/Q_Database_Stats/qs_vs_time.png')
plt.clf()
plt.cla()

# Qs in Tomography

qs_model.loc[(qs_model['Qs'] > 0.0) & (qs_model['Qs'] < 75.0),'Qs'] = 75.0
qs_model.loc[(qs_model['Qs'] > 1500.0),'Qs'] = 1500.0

fig,ax = plt.subplots()
ax.set_axisbelow(True)
plt.grid(color='black')
plt.hist(qs_model.loc[(qs_model['Qs'] >= 75.0) & (qs_model['Qs'] <= 1500.0),'Qs'],bins = np.linspace(0,1500,16),edgecolor='black',color='green')
plt.xlabel('Qs')
plt.ylabel('Frequency')
plt.savefig('/Volumes/External/Attenuation/Q_Database_Stats/qs_tomo_hist.png')
plt.clf()
plt.cla()

good_rays.drop(['ev_id','stn_id','judge_result','outliers_removed'],axis=1)

good_rays_means = good_rays.mean()
good_rays_sds = np.sqrt(good_rays.var())
good_rays_norm = (good_rays - good_rays_means)/good_rays_sds

GOOD_RAYS_CORR_MATRIX = good_rays_norm.corr().round(5)
GOOD_RAYS_CORR_MATRIX.style.background_gradient(cmap = 'RdYlGn',vmin=-1,vmax=1).to_excel('/Volumes/External/Attenuation/q_database_good_rays_corr_matrix.xlsx',engine='openpyxl')

# All Rays Stats

fig,ax = plt.subplots()
ax.set_axisbelow(True)
plt.grid(color='black')
plt.hist(q_database.loc[(q_database['stacked_qs'] >= 75.0) & (q_database['stacked_qs'] <= 1500.0),'stacked_qs'],bins = np.linspace(0,1500,16),edgecolor='black',color='red')
plt.xlabel('Stacked Qs')
plt.ylabel('Frequency')
plt.savefig('/Volumes/External/Attenuation/Q_Database_Stats/stacked_qs_hist.png')
plt.clf()
plt.cla()

fig,ax = plt.subplots()
ax.set_axisbelow(True)
plt.grid(color='black')
plt.hist(q_database.loc[(q_database['mean_qs'] >= 75.0) & (q_database['mean_qs'] <= 1500.0),'mean_qs'],bins = np.linspace(0,1500,16),edgecolor='black',color='cyan')
plt.xlabel('Mean Qs')
plt.ylabel('Frequency')
plt.savefig('/Volumes/External/Attenuation/Q_Database_Stats/mean_qs_hist.png')
plt.clf()
plt.cla()

fig,ax = plt.subplots()
ax.set_axisbelow(True)
plt.grid(color='black')
plt.hist(q_database.loc[(q_database['stdev_qs'] >= 0.0) & (q_database['stdev_qs'] <= 300.0),'stdev_qs'],bins = np.linspace(0,300,13),edgecolor='black',color='purple')
plt.xlabel('St. Dev. of Qs')
plt.ylabel('Frequency')
plt.savefig('/Volumes/External/Attenuation/Q_Database_Stats/stdev_qs_hist.png')
plt.clf()
plt.cla()

# Good Rays Only Stats

fig,ax = plt.subplots()
ax.set_axisbelow(True)
plt.grid(color='black')
plt.hist(good_rays['stacked_qs'],bins = np.linspace(0,1500,16),edgecolor='black',color='red')
plt.xlabel('Stacked Qs')
plt.ylabel('Frequency')
plt.savefig('/Volumes/External/Attenuation/Q_Database_Stats/stacked_qs_hist_good.png')
plt.clf()
plt.cla()

fig,ax = plt.subplots()
ax.set_axisbelow(True)
plt.grid(color='black')
plt.hist(good_rays['mean_qs'],bins = np.linspace(0,1500,16),edgecolor='black',color='cyan')
plt.xlabel('Mean Qs')
plt.ylabel('Frequency')
plt.savefig('/Volumes/External/Attenuation/Q_Database_Stats/mean_qs_hist_good.png')
plt.clf()
plt.cla()

fig,ax = plt.subplots()
ax.set_axisbelow(True)
plt.grid(color='black')
plt.hist(good_rays['stdev_qs'],bins = np.linspace(0,300,13),edgecolor='black',color='purple')
plt.xlabel('St. Dev. of Qs')
plt.ylabel('Frequency')
plt.savefig('/Volumes/External/Attenuation/Q_Database_Stats/stdev_qs_hist_good.png')
plt.clf()
plt.cla()