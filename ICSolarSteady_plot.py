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
	basenames = ['Jan28','Jan31','Feb6','Feb11','Feb27','Feb28','Mar06','Mar09']
	# basenames = ['Jan28']
	# hlist = [2.0]
	# h = float(2.0)
	ext = ''
	# for name in basenames:
	# 	# for h in hlist:
	# 		# print name, h
	# 	call('python '+'ICSolar.py data/ICSolar/'+name+'.csv >/dev/null',shell=True)

	os.chdir('data/ICSolar')
	# normfile = open('Steady_norms.txt','w')

	for name in basenames:
		# normfile.write(name+'\n')
		# for h in hlist:
		# h = float(h)
		expt = open(name+'.csv','rU')
		steady = open('model/'+name+'_model_'+'.csv','rU')
		csvfiles = {'exp':expt,'st':steady}
		data = {'exp':defaultdict(list),'st':defaultdict(list)}
		for filename in csvfiles:
			f = csv.DictReader(csvfiles[filename])
			for row in f: # read a row as {column1: value1, column2: value2,...}
			  for (k,v) in row.items(): # go over each column name and value 
			  	data[filename][k].append(float(v))
			csvfiles[filename].close()
		# need to align the times
		numPoints = len(data['exp']['Timestamp'])
		t = np.arange(0,numPoints)*10.0
		for key in data['exp'].keys():
			if ('dni' in key.lower()):
				dni = key
		print len(data['exp'][dni]), name, dni
		q = np.array(data['exp']['exp_heatgen']);
		plt.plot(t,data['exp'][dni],linewidth=2.0,label='dni')
		plt.plot(t,q*10.0,linewidth=2.0,label='Q')
		plt.legend(loc=0)

		plt.xlabel('Time (seconds)')
		plt.ylabel('DNI (W/m^2),Q')
		fig = plt.gcf()
		fig.set_size_inches(5,5)
		axes = plt.gca()
		plt.savefig('../../images/ICSolar/' + name+'_DNI.png')		
		plt.close()
		# for j in range(6,0,-1):

		plt.plot(t,data['exp']['exp_heatgen'],linewidth=2.0)
		plt.xlabel('Time (seconds)')
		plt.ylabel('Q_i')
		# plt.legend(loc=0)

		fig = plt.gcf()
		fig.set_size_inches(5,5)
		plt.savefig('../../images/ICSolar/' + name+'_Q.png')		
		plt.close()

	# 	for j in range(6,0,-1):
	# 		plt.plot(t,data['exp']['m'+str(j)+'_in'],linewidth=2.0,label='Expt')
	# 		plt.plot(t,data['st']['m'+str(j)+'_in'],linewidth=2.0,label='Model')
	# 		plt.plot(t,data['exp']['exp_inlet'],linewidth=2.0,label='Inlet')

	# 		plt.legend(loc=0)
	# 		plt.xlabel('Time (seconds)')
	# 		plt.ylabel('Temperature (C)')
	# 		plt.title('m'+str(j)+'_in ')
	# 		fig = plt.gcf()
	# 		fig.set_size_inches(5,5)
	# 		axes = plt.gca()
	# 		axes.set_ylim([20,100])
	# 		plt.savefig('../../images/ICSolar/' + name+'_m'+str(j)+'_in_steady_'+ext+'.png')		
	# 		plt.close()

	# 		plt.plot(t,data['exp']['m'+str(j)+'_out'],linewidth=2.0,label='Expt')
	# 		plt.plot(t,data['st']['m'+str(j)+'_out'],linewidth=2.0,label='Model')
	# 		plt.plot(t,data['exp']['exp_inlet'],linewidth=2.0,label='Inlet')
	# 		if(j == 1):
	# 			L2 = sum([(data['exp']['m'+str(j)+'_out'][i]-data['st']['m'+str(j)+'_out'][i])*(data['exp']['m'+str(j)+'_out'][i]-data['st']['m'+str(j)+'_out'][i])
	# 			 for i in range(0,numPoints)])
	# 			L2 = math.sqrt(L2/numPoints)
	# 			Linf = max([abs(data['exp']['m'+str(j)+'_out'][i]-data['st']['m'+str(j)+'_out'][i]) for i in range(0,numPoints)])
	# 			normfile.write(str(j) + " L2 "+ str(L2)+" Linf "+str(Linf)+'\n')
	# 		plt.legend(loc=0)
	# 		plt.xlabel('Time (seconds)')
	# 		plt.ylabel('Temperature (C)')
	# 		plt.title('m'+str(j)+'_out ')
	# 		fig = plt.gcf()
	# 		fig.set_size_inches(5,5)
	# 		axes = plt.gca()
	# 		axes.set_ylim([20,100])
	# 		plt.savefig('../../images/ICSolar/' + name+'_m'+str(j)+'_out_steady_'+ext+'.png')
	# 		plt.close()


	# 		# AIR TIME
	# 		# plt.plot(t,data['exp']['air'+str(j)+'_in'],linewidth=2.0,label='Expt')
	# 		plt.plot(t,data['st']['air'+str(j)+'_in'],linewidth=2.0,label='Model')
	# 		plt.plot(t,data['exp']['Tamb'],linewidth=2.0,label='Ambient')

	# 		plt.legend(loc=0)
	# 		plt.xlabel('Time (seconds)')
	# 		plt.ylabel('Temperature (C)')
	# 		plt.title('air'+str(j)+'_in ')
	# 		fig = plt.gcf()
	# 		fig.set_size_inches(5,5)
	# 		axes = plt.gca()
	# 		axes.set_ylim([20,30])
	# 		plt.savefig('../../images/ICSolar/' + name+'_air'+str(j)+'_in_steady_'+ext+'.png')		
	# 		plt.close()

	# 		# plt.plot(t,data['exp']['air'+str(j)+'_out'],linewidth=2.0,label='Expt')
	# 		plt.plot(t,data['st']['air'+str(j)+'_out'],linewidth=2.0,label='Model')
	# 		plt.plot(t,data['exp']['Tamb'],linewidth=2.0,label='Ambient')

	# 		plt.legend(loc=0)
	# 		plt.xlabel('Time (seconds)')
	# 		plt.ylabel('Temperature (C)')
	# 		plt.title('m'+str(j)+'_out ')
	# 		fig = plt.gcf()
	# 		fig.set_size_inches(5,5)
	# 		axes = plt.gca()
	# 		axes.set_ylim([20,30])
	# 		plt.savefig('../../images/ICSolar/' + name+'_air'+str(j)+'_out_steady_'+ext+'.png')
	# 		plt.close()

	# 		# lets do this manually
	# 	os.chdir('../../_posts/')
	# 	mdfilename = time.strftime("%Y-%m-%d")+'-Steady_'+name+'_'+ext+'.md'
	# 	mdfile = open(mdfilename,'w')
	# 	header = ['---','layout: post','title: Air and Water Results on '+name,
	# 		'---', '{{ page.title }}','-----------------']

	# 	for item in header:
	# 		mdfile.write(item+'\n')
	# 	mdfile.write('\n')
	# 	mdfile.write('![Results]({{ site.baseurl }}/images/ICSolar/' + \
	# 			name+'_flowrate.png) ')
	# 	mdfile.write('![Results]({{ site.baseurl }}/images/ICSolar/' + \
	# 			name+'_Q.png)\n\n')
	# 	for i in range(6,0,-1):
	# 		mdfile.write('![Results]({{ site.baseurl }}/images/ICSolar/' + \
	# 			name+'_m'+str(i)+'_in_steady_'+ext+'.png) ')
	# 		mdfile.write('![Results]({{ site.baseurl }}/images/ICSolar/' + \
	# 			name+'_m'+str(i)+'_out_steady_'+ext+'.png)\n\n')
	# 		mdfile.write('![Results]({{ site.baseurl }}/images/ICSolar/' + \
	# 			name+'_air'+str(i)+'_in_steady_'+ext+'.png) ')
	# 		mdfile.write('![Results]({{ site.baseurl }}/images/ICSolar/' + \
	# 			name+'_air'+str(i)+'_out_steady_'+ext+'.png)\n\n')

	# 	mdfile.close()
	# 	os.chdir('../data/ICSolar')
	# normfile.close()