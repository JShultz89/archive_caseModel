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
	hlist = [0.01,0.1,0.5,0.75,1.0,1.25,1.5,1.75,2.0,5.0,10.0,100.0]

	for name in basenames:
		for h in hlist:
			print name, h
			call('python '+'ICSolar.py data/ICSolar/'+name+'.csv '+ str(h)+'>/dev/null',shell=True)

	os.chdir('data/ICSolar')
	for name in basenames:

		for h in hlist:
			h = float(h)
			expt = open(name+'.csv','rU')
			steady = open('model/'+name+'_model_'+str(int(round(h*100)))+'.csv','rU')
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
			t = range(0,numPoints)*10.0
	
			plt.plot(t,data['exp']['exp_flowrate'],linewidth=2.0)
			plt.xlabel('Time (seconds)')
			plt.ylabel('Volumetric Flow Rate (mm^3/s)')
			fig = plt.gcf()
			fig.set_size_inches(4,4)
			axes = plt.gca()
			plt.savefig('../../images/ICSolar/' + name+'_'+str(int(round(hwa*100)))+'_flowrate.png')		
			plt.close()
			for j in range(6,0,-1):
				plt.plot(t,data['exp']['heatgen_m'+str(j)],linewidth=2.0,label=str(j))
			plt.xlabel('Time (seconds)')
			plt.ylabel('Q_i')
			fig = plt.gcf()
			fig.set_size_inches(4,4)
			plt.savefig('../../images/ICSolar/' + name+'_'+str(int(round(hwa*100)))+'_Q.png')		
			plt.close()

			for j in range(6,0,-1):
				plt.plot(t,data['exp']['m'+str(j)+'_in'],linewidth=2.0,label='Expt')
				plt.plot(t,data['st']['m'+str(j)+'_in'],linewidth=2.0,label='Model')
				plt.plot(t,data['exp']['exp_inlet'],linewidth=2.0,label='Inlet')

				L2 = sum([(data['exp']['m'+str(j)+'_in'][i]-data['st']['m'+str(j)+'_in'][i])*(data['exp']['m'+str(j)+'_in'][i]-data['st']['m'+str(j)+'_in'][i])
				 for i in range(0,numPoints)])
				L2 = sqrt(L2/numPoints)
				Linf = max([abs(data['exp']['m'+str(j)+'_in'][i]-data['st']['m'+str(j)+'_in'][i]) for i in range(0,numPoints)])

				plt.legend(loc=0)
				plt.xlabel('Time (seconds)')
				plt.ylabel('Temperature (C)')
				plt.title('m'+str(j)+'_in '+'L2:'+str(int(round(L2*100000)/100000))+' Linf:'+str(int(round(Linf*100000)/100000)))
				fig = plt.gcf()
				fig.set_size_inches(4,4)
				axes = plt.gca()
				axes.set_ylim([20,100])
				plt.savefig('../../images/ICSolar/' + name+'_m'+str(j)+'_out_steady_'+str(int(round(hwa*100)))+'.png')		
				plt.close()

				plt.plot(t,data['exp']['m'+str(j)+'_out'],linewidth=2.0,label='Expt')
				plt.plot(t,data['st']['m'+str(j)+'_out'],linewidth=2.0,label='Model')
				plt.plot(t,data['exp']['exp_inlet'],linewidth=2.0,label='Inlet')
				L2 = sum([(data['exp']['m'+str(j)+'_out'][i]-data['st']['m'+str(j)+'_out'][i])*(data['exp']['m'+str(j)+'_out'][i]-data['st']['m'+str(j)+'_out'][i])
				 for i in range(0,numPoints)])
				L2 = sqrt(L2/numPoints)
				Linf = max([abs(data['exp']['m'+str(j)+'_out'][i]-data['st']['m'+str(j)+'_out'][i]) for i in range(0,numPoints)])

				plt.legend(loc=0)
				plt.xlabel('Time (seconds)')
				plt.ylabel('Temperature (C)')
				plt.title('m'+str(j)+'_out '+'L2:'+str(int(round(L2*100000)/100000))+' Linf:'+str(int(round(Linf*100000)/100000)))
				fig = plt.gcf()
				fig.set_size_inches(4,4)
				axes = plt.gca()
				axes.set_ylim([20,100])
				plt.savefig('../../images/ICSolar/' + name+'_m'+str(j)+'_out_steady_'+str(int(round(hwa*100)))+'.png')
				plt.close()

				# lets do this manually
			os.chdir('../../_posts/')
			mdfilename = time.strftime("%Y-%m-%d")+'-Steady_'+name+str(int(round(hwa*100)))+'.md'
			mdfile = open(mdfilename,'w')
			header = ['---','layout: post','title: Comparison of data on '+name,
				'---', '{{ page.title }}','-----------------', 'With h_{wa} = '+str(h*0.16*0.3)]

			for item in header:
				mdfile.write(item+'\n')
			mdfile.write('\n')
			mdfile.write('![Results]({{ site.baseurl }}/images/ICSolar/' + \
					name+'_'+str(int(round(hwa*100)))+'_flowrate.png ')
			mdfile.write('![Results]({{ site.baseurl }}/images/ICSolar/' + \
					name+'_'+str(int(round(hwa*100)))+'_Q.png\n\n')
			for i in range(6,0,-1):
				mdfile.write('![Results]({{ site.baseurl }}/images/ICSolar/' + \
					name+'_m'+str(j)+'_in_steady_'+str(int(round(hwa*100)))+'.png ')
				mdfile.write('![Results]({{ site.baseurl }}/images/ICSolar/' + \
					name+'_m'+str(j)+'_out_steady_'+str(int(round(hwa*100)))+'.png\n\n')

			mdfile.close()
			os.chdir('../data/ICSolar')