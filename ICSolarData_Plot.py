import csv
import sys
import os.path
import time
import matplotlib.pyplot as plt
import matplotlib

from collections import defaultdict
from subprocess import call
from os import chdir
import numpy as np
import math
from scipy.stats import kde

if __name__ == "__main__":
	# for i in range(1,7):
	# basenames = ['Jan28','Jan31','Feb6','Feb11','Feb27','Feb28','Mar06','Mar09']
	basenames = ['Jan28','Jan31']#,'Feb28','Mar06','Mar09']
	# basenames = ['Feb28','Mar06','Mar09']

	# dni = {}
	# Q = {}
	dni = []
	Q = []
	for name in basenames:
		# call('python '+'ICSolarUQ.py data/ICSolar/'+name+'.csv',shell=True)

		exp = open('data/ICSolar/'+name+'.csv','rU')
		data = defaultdict(list)
		f = csv.DictReader(exp)
		for row in f: # read a row as {column1: value1, column2: value2,...}
		  for (k,v) in row.items(): # go over each column name and value 
		  	data[k].append(float(v))
		exp.close()
		# start = 0
		# end = len(data['DNI'])-1
		# while(data['DNI'][start] < 300):
		# 	start = start + 1
		# while(data['DNI'][end] < 300):
		# 	end = end-1

		# end = end - 20
		for i in range(0,len(data['DNI'])):
			if(data['DNI'][i] > 100 and data['exp_heatgen'][i]>0):
				dni.append(data['DNI'][i])
				Q.append(data['exp_heatgen'][i])
	dni = np.array(dni)
	Q = np.array(Q)
	print len(Q)

	norm = plt.Normalize()

	# (p,V)  = np.polyfit(dni,np.log(Q),1,cov=True)
	# print V

	QQ1 = np.poly1d([0.024801*(1.-0.34)*6.0,0.0])
	QQ2 = np.poly1d([1.67600635e-4,-5.45860e-3,-5.0490048])
	QQ3 = np.poly1d([1.11722958e-6,-1.18376465e-3,4.34784474e-1,-3.7253707e1])
	QQe = lambda QQ: np.exp(1.13346325416)*np.exp(0.0045503386885*QQ)
	var = np.sqrt(np.dot(QQ1(dni)-Q,QQ1(dni)-Q)/(len(Q)-1))
	# print var
	plt.scatter(dni,Q,s=0.1)
	plt.ylabel('Q (W)')
	plt.xlabel('DNI (W/m^2)')
	plt.plot(np.sort(dni),QQ1(np.sort(dni)),linewidth=2,label="Linear")
	plt.plot(np.sort(dni),QQ2(np.sort(dni)),linewidth=2,label="Quadratic")
	plt.plot(np.sort(dni),QQ3(np.sort(dni)),linewidth=2,label="Cubic")
	plt.plot(np.sort(dni),QQe(np.sort(dni)),linewidth=2,label="Exponential")
	plt.legend(loc=0)
	axes = plt.gca()
	axes.set_ylim([-50,150])		

	fig = plt.gcf()
	fig.set_size_inches(8,8)
	# plt.title(str(p)+ str(var))
	plt.savefig('images/ICSolar/QvsDNI_fits.png')		
	plt.close()

	# 	# print hb.norm.vmax,hb.norm.vmin
	# hb = plt.hexbin(dni,Q,gridsize=50,cmap=plt.cm.Spectral_r,mincnt=1,norm=norm,edgecolors='black')

	# plt.colorbar()
	# # plt.title('heatgen_m'+str(i))
	# # plt.scatter(dni,Q,s=0.1)
	# plt.ylabel('Q (W)')
	# plt.xlabel('DNI (W/m^2)')

	# fig = plt.gcf()
	# fig.set_size_inches(8,8)
		
	# plt.savefig('images/ICSolar/QvsDNI_hex.png')		
	# plt.close()
