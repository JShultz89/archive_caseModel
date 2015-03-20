import csv
import sys
import os.path
import time
import matplotlib.pyplot as plt
from collections import defaultdict
from subprocess import call
from os import chdir
import numpy as np
import math
if __name__ == "__main__":
	# basenames = ['Jan28','Jan31','Feb6','Feb11','Feb27','Feb28','Mar06','Mar09']
	basenames = ['test']

	ext = '_UQ'
	for name in basenames:
		call('python '+'ICSolarUQ.py data/ICSolar/'+name+'.csv >/dev/null',shell=True)

	os.chdir('data/ICSolar')

	for name in basenames:

		steady = open('model/'+name+'_model_'+'.csv','rU')
		data = defaultdict(list)
		f = csv.DictReader(steady)
		for row in f: # read a row as {column1: value1, column2: value2,...}
		  for (k,v) in row.items(): # go over each column name and value 
		  	data[k].append(float(v))
		steady.close()
		# need to align the times
		numPoints = len(data['Timestamp'])
		t = np.arange(0,numPoints)*10.0
		dni = np.array(data['DNI'])*0.024801*(1.0-0.34)
		q = np.array(data['heatgen_mod'])
		qSTD = np.array(data['heatgen_mod_var'])
		lb = q-qSTD
		ub = q+qSTD
		plt.plot(t,dni,linewidth=2.0,label='heat From DNI')
		plt.plot(t,np.array(data['exp_heatgen'])/6.0,linewidth=2.0,label='Exp Heat')
		plt.plot(t,q,linewidth=2.0,label='Model Heat')
		plt.fill_between(t, lb, ub, facecolor='yellow', alpha=0.5)
		plt.legend(loc=0)
		for j in range(6,0,-1):
			plt.plot(t,data['heatgen_m'+str(j)],linewidth=2.0,label=str(j),ls='--')
		plt.xlabel('Time (seconds)')
		plt.ylabel('Average Energy (W) per module')
		fig = plt.gcf()
		fig.set_size_inches(5,5)
		axes = plt.gca()
		plt.savefig('../../images/ICSolar/' + name+'_DNI.png')		
		plt.close()

		plt.plot(t,dni,linewidth=2.0,label='heat From DNI')
		plt.plot(t,q,linewidth=2.0,label='Model Heat')
		plt.fill_between(t, lb, ub, facecolor='yellow', alpha=0.5)
		plt.legend(loc=0)

		plt.xlabel('Time (seconds)')
		plt.ylabel('Average Energy (W) per module')
		fig = plt.gcf()
		fig.set_size_inches(5,5)
		axes = plt.gca()
		plt.savefig('../../images/ICSolar/' + name+'_DNI_var.png')		
		plt.close()
		# figs = [['m','_in'],['m','_out'],['air','_in'],['air','_out']]
		figs = [['m','_in'],['m','_out']]

		for j in range(6,0,-1):
			for d in figs:
				if (d[0] == 'air'):
					plt.plot(t,data['Tamb'],linewidth=2.0,label='Expt')
				else:
					plt.plot(t,data[d[0]+str(j)+d[1]],linewidth=2.0,label='Expt')

				plt.plot(t,data[d[0]+str(j)+d[1]+'_mod'],linewidth=2.0,label='Model')
				lb = np.array(data[d[0]+str(j)+d[1]+'_mod'])-np.sqrt(np.array(data[d[0]+str(j)+d[1]+'_mod_var']))
				ub = np.array(data[d[0]+str(j)+d[1]+'_mod'])+np.sqrt(np.array(data[d[0]+str(j)+d[1]+'_mod_var']))
				plt.fill_between(t, lb, ub, facecolor='yellow', alpha=0.5)
				plt.legend(loc=0)
				plt.xlabel('Time (seconds)')
				plt.ylabel('Temperature (C)')
				plt.title(d[0]+str(j)+d[1])
				fig = plt.gcf()
				fig.set_size_inches(5,5)
				axes = plt.gca()
				axes.set_ylim([20,100])
				plt.savefig('../../images/ICSolar/' + name+'_'+d[0]+str(j)+d[1]+ext+'.png')		
				plt.close()
