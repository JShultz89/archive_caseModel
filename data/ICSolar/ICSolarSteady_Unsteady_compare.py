import csv
import sys
import os.path
import time
import matplotlib.pyplot as plt
from collections import defaultdict
from subprocess import call
from os import chdir

if __name__ == "__main__":
	basenames = ['Jan28','Jan31','Feb6','Feb11','Feb27','Feb28','Mar06','Mar09']
	for name in basenames:
		expt = open(name+'.csv','rU')
		unsteady = open('model/'+name+'_model_unsteady.csv','rU')
		steady = open('model/'+name+'_model.csv','rU')
		csvfiles = {'exp':expt,'unst':unsteady,'st':steady}
		data = {'exp':defaultdict(list),'unst':defaultdict(list) ,'st':defaultdict(list)}
		for filename in csvfiles:
			f = csv.DictReader(csvfiles[filename])
			for row in f: # read a row as {column1: value1, column2: value2,...}
			  for (k,v) in row.items(): # go over each column name and value 
			  	data[filename][k].append(float(v))
			csvfiles[filename].close()
		# need to align the times
		start = 0
		end = len(data['exp']['Timestamp'])-1
		while(abs(data['exp']['Timestamp'][start] - data['unst']['Timestamp'][0]) > 1e-3):
			start = start+1
		while(abs(data['exp']['Timestamp'][end] - data['unst']['Timestamp'][-1]) > 1e-3):
			end = end-1
		t = range(start,end)
		for j in range(1,7):
			plt.plot(t,data['exp']['exp_inlet'][start:end],linewidth=2.0,label='Inlet')
			plt.plot(t,data['exp']['m'+str(j)+'_out'][start:end],linewidth=2.0,label='Expt')
			plt.plot(t,data['st']['m'+str(j)+'_out'][0:(end-start)],linewidth=2.0,label='Steady')
			plt.plot(t,data['unst']['m'+str(j)+'_out'][0:(end-start)],linewidth=2.0,label='Unsteady')

			plt.legend(loc=0)
			plt.xlabel('Measurement number (~timesteps)')
			plt.ylabel('Temperature (C)')
			plt.title(filename[:-4]+' m'+str(j)+'_out')
			fig = plt.gcf()
			fig.set_size_inches(4,4)

			plt.savefig('../../images/ICSolar/' + name+'_m'+str(j)+'_out_compare.png')		
			plt.close()

			plt.plot(t,data['exp']['exp_inlet'][start:end],linewidth=2.0,label='Inlet')
			plt.plot(t,data['exp']['m'+str(j)+'_in'][start:end],linewidth=2.0,label='Expt')
			plt.plot(t,data['st']['m'+str(j)+'_in'][0:(end-start)],linewidth=2.0,label='Steady')
			plt.plot(t,data['unst']['m'+str(j)+'_in'][0:(end-start)],linewidth=2.0,label='Unsteady')
			plt.legend(loc=0)
			plt.xlabel('Measurement number (~timesteps)')
			plt.ylabel('Temperature (C)')
			plt.title(filename[:-4]+' m'+str(j)+'_in')
			fig = plt.gcf()
			fig.set_size_inches(4,4)
			plt.savefig('../../images/ICSolar/' + name+'_m'+str(j)+'_in_compare.png')
			plt.close()

			# lets do this manually
		os.chdir('../../_posts/')
		mdfilename = time.strftime("%Y-%m-%d")+'-Comparison_'+name+'.md'
		mdfile = open(mdfilename,'w')
		header = ['---','layout: post','title: Comparison of data on '+name,
			'---', 'h2. {{ page.title }}']

		for item in header:
			mdfile.write(item+'\n')
		mdfile.write('\n')
		for i in range(6,0,-1):
			mdfile.write('![Results]({{ site.baseurl }}/images/ICSolar/' + name+'_m'+str(i)+'_in_compare.png)\n\n')
			mdfile.write('![Results]({{ site.baseurl }}/images/ICSolar/' + name+'_m'+str(i)+'_out_compare.png)\n\n')

		mdfile.close()
		os.chdir('../data/ICSolar')