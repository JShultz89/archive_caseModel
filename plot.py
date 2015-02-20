'''
File to plot the output quick
'''

import matplotlib.pyplot as plt 
import csv
import datetime as dt
import dateutil.parser as dparser

csvfile = open('simulation.csv','rU')
cr = csv.DictReader(csvfile)

Exp_Tw = []
Sim_Tw = []
Time = []

for row in cr:
    Time_tmp = str(row['Timestamp'])
    Time_tmp=dt.datetime.strptime(Time_tmp,'%H:%M %p')
    Time.append(Time_tmp)
    Exp_Tw.append(float(row['exp_outlet']))
    Sim_Tw.append(float(row['sim_outlet']))

plt.plot(Time,Exp_Tw)
plt.plot([1,2,5], [2,4,10])