"""
This defines the ICSolar model proposed by Assad Oberai

where we our problem is similar to this

          |-------|w|---||
          |    5  |w|   ||
          |  |\		|w|   ||
          |  | \	|w|   ||
          |--| 4|-|w|---||
          |  | /	|w|   ||
          |  |/   |w|   ||
          |       |w|   ||
exterior	|		 3 	|w|   ||  interior 
          |       |w|   ||
          |  |\		|w|   ||
          |  | \	|w|   ||
          |--| 2|-|w|---||
          |  | /	|w|   ||
          |  |/   |w|   ||
          |    1  |w|   ||
          |-------|w|---||

with n modules, and 2*n+1 air regions, and 2*n+1 water regions
"""

""" Required Modules """
import src.blocks as b
import src.flux as f
import src.problem as p
import src.source as s
""" Optional Modules """
import csv
import sys
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from subprocess import call
import os.path
from os import chdir
def solve(heatGen,waterTemp,waterFlowRate,airTemp,n,heatGenVar):
	""" Boundary flux blocks """
	""" All these blocks remain constant """
	# define inlet water with initial state
	waterTemp = 25.0;
	airTemp = 20.0;
	w0 = b.Block('waterInlet','constWater',T = waterTemp)
	# define inlet air with initial state
	a0 = b.Block('airInlet','constAir',T = airTemp)

	# We will need mass flow rates for our fluxes, so initialize them here
	# These are added to the class object, and are not part of the
	# default block requirement
	w0.mdot = lambda T = 0 : 1.0#waterFlowRate*1.0e-6*w0.m['rho'](w0.state)
	a0.mdot = lambda T = 0 : 2.0#2.0*a0.m['rho'](a0.state)*0.16

	# All these boundary blocks need are temperatures
	# define Exterior boundary condition
	aExt = b.Block('Exterior','air',T = airTemp)
	# define Interior boundary condition
	aInt = b.Block('Interior','air',T = airTemp)

	# Initial lists of blocks
	water = []
	air = []

	# add in the inflow block to make it easy to connect blocks
	# These blocks are not used in the solve
	water.append(w0)
	air.append(a0)
	L = 1.0
	#### Initialize the blocks we will solve on
	for i in range(1,2*n+1):
		if(i % 2 == 1): # odd regions are "tube" regions
			hh = 1.0
			# Every block is named for its material in this case
			water.append(b.Block('m' + str(n-i/2)+'_in','test',T = waterTemp))
			air.append(b.Block('air' + str(n-i/2)+'_in','test',T = airTemp))
			# Water tube has one flux for heat conduction
			if( i == 1 ): 
				water[i].addFlux(f.Flux(air[i],'heatCondSimple',{'type':'test','m':[],'L':L/2.0,'scale':hh*2.0}))
				# Air has three, corresponding to the windows and the water-tube
				air[i].addFlux(f.Flux(water[i],'heatCondSimple',{'type':'test','m':[],'L':L/2.0,'scale':hh*2.0}))
				# air[i].addFlux(f.Flux(aInt,'heatCondSimple',{'type':'int','m':[],'L':L/2.0}))
				# air[i].addFlux(f.Flux(aExt,'heatCondSimple',{'type':'ext','m':[],'L':L/2.0}))
			else:
				water[i].addFlux(f.Flux(air[i],'heatCondSimple',{'type':'test','m':[],'L':L,'scale':hh}))
				air[i].addFlux(f.Flux(water[i],'heatCondSimple',{'type':'test','m':[],'L':L,'scale':hh}))
				# air[i].addFlux(f.Flux(aInt,'heatCondSimple',{'type':'int','m':[],'L':L}))
				# air[i].addFlux(f.Flux(aExt,'heatCondSimple',{'type':'ext','m':[],'L':L}))
		else: # These are "module" region
			# Every block is named for its material in this case
			water.append(b.Block('m' + str(n-i/2+1)+'_out','test',T = waterTemp))
			air.append(b.Block('air' + str(n-i/2+1)+'_out','test',T = airTemp))
			water[i].addSource(s.Source('const',T = -1.0))#-heatGen[n-i/2]*1e-3))
			air[i].addSource(s.Source('const',T = 0.0))

		# These are the connectivity between regions, each block takes heat
		# from the block "below" it
		air[i].addFlux(f.Flux(air[i-1],'heatConvection'))
		water[i].addFlux(f.Flux(water[i-1],'heatConvection'))

		# These are needed for window calculations
		air[i].mdot = a0.mdot
		water[i].mdot = w0.mdot
	#### END OF INITIALIZATION

	""" Problem Initialization """

	# Start the problem with solvable blocks, which
	# are all the blocks except the first two
	bToSolve = []
	for i in range(0,2*n):				
		bToSolve.append(water[i+1])
		bToSolve.append(air[i+1])
	ICSolar = p.Problem(bToSolve)
	output = ICSolar.solve()
	output = ICSolar.solve()

	J = ICSolar.jacobian()
	print J
	# Sig = np.dot(np.linalg.inv(A),A)
	# print np.transpose(A)
	# print np.count_nonzero(np.abs(A > 1e-20))
	# now we can do a test.


	Temp = {}
	for ww in water[1::]:
		Temp[ww.name] = ww.state['T']
	for aa in air[1::]:
		Temp[aa.name] = aa.state['T']
	print Temp
	# at each point, I'm going to have	
	return Temp
	
if __name__ == "__main__":
	filename = sys.argv[1]
	if (len(sys.argv) > 2):
		hwa = float(sys.argv[2])
	else:
		hwa = 2.0
	csvfile = open(filename,'rU')
	csvwrite = open(os.path.dirname(filename)+'/model/' + os.path.basename(filename)[:-4]+ \
		'_model_'+'.csv','w')
	cr = csv.DictReader(csvfile)
	# read in all the data
	data = defaultdict(list) 
	for row in cr: # read a row as {column1: value1, column2: value2,...}
	  for (k,v) in row.items(): # go over each column name and value 
	  	data[k].append(float(v))

	numModules = 2
	csvHeader = ['Timestamp','exp_inlet'] 
	for i in range(numModules,0,-1):
		csvHeader.append('m'+str(i)+'_in')
		csvHeader.append('m'+str(i)+'_out')
		csvHeader.append('air'+str(i)+'_in')
		csvHeader.append('air'+str(i)+'_out')
		data['m'+str(i)+'_in_mod'] = [];
		data['m'+str(i)+'_out_mod'] = [];
		data['air'+str(i)+'_in_mod'] = [];
		data['air'+str(i)+'_out_mod'] = [];
	cw = csv.DictWriter(csvwrite,csvHeader)
	cw.writeheader()
	# for each line, run the data
	numDataPoints = len(data['Timestamp'])
	for i in range(0,numModules):
		airTemp = 22.5
		if('Tamb' in data.keys()): 
			airTemp = data['Tamb'][i]
		heatGen = [data['heatgen_m'+str(j)][i] for j in range(1,7)]
		waterTemp = data['exp_inlet'][i]
		waterFlowRate = data['exp_flowrate'][i]
		results = solve(heatGen,waterTemp,waterFlowRate,airTemp,numModules,hwa)
		results['Timestamp'] = data['Timestamp'][i]
		results['exp_inlet'] = data['exp_inlet'][i]

		for j in range(1,numModules):
			data['m'+str(j)+'_in_mod'].append(results['m'+str(j)+'_in'])
			data['m'+str(j)+'_out_mod'].append(results['m'+str(j)+'_out'])
			data['air'+str(j)+'_in_mod'].append(results['air'+str(j)+'_in'])
			data['air'+str(j)+'_out_mod'].append(results['air'+str(j)+'_out'])
		cw.writerow(results)
	csvfile.close()
	csvwrite.close()


	# i = range(0,numDataPoints)
	# for j in range(1,7):
	# 	plt.plot(i,data['exp_inlet'],linewidth=2.0,label='Inlet')
	# 	if('m'+str(j)+'_out' in data.keys()): 
	# 		plt.plot(i,data['m'+str(j)+'_out'],linewidth=2.0,label='Expt')
	# 	plt.plot(i,data['m'+str(j)+'_out_mod'],linewidth=2.0,label='Model')
	# 	plt.legend(loc=0)
	# 	plt.xlabel('Measurement number (~time)')
	# 	plt.ylabel('Temperature (C)')
	# 	plt.title(filename[:-4]+' m'+str(j)+'_out')
	# 	fig = plt.gcf()
	# 	fig.set_size_inches(4,4)

	# 	plt.savefig(os.path.dirname(filename)+'/images/' + os.path.basename(filename)[:-4]+'_m'+str(j)+'_out.pdf')		
	# 	plt.close()

	# 	plt.plot(i,data['exp_inlet'],linewidth=2.0,label='Inlet')
	# 	if('m'+str(j)+'_in' in data.keys()): 
	# 		plt.plot(i,data['m'+str(j)+'_in'],linewidth=2.0,label='Expt')
	# 	plt.plot(i,data['m'+str(j)+'_in_mod'],linewidth=2.0,label='Model')

	# 	plt.legend(loc=0)
	# 	plt.xlabel('Measurement number (~time)')
	# 	plt.ylabel('Temperature (C)')
	# 	plt.title(filename[:-4]+' m'+str(j)+'_in')
	# 	fig = plt.gcf()
	# 	fig.set_size_inches(4,4)
	# 	plt.savefig(os.path.dirname(filename)+'/images/' + os.path.basename(filename)[:-4]+'_m'+str(j)+'_in.pdf')
	# 	plt.close()

	# 	# lets do this manually
	# chdir('doc/ICSolar')
	# texfilename = 'Steady_'+os.path.basename(filename)[:-4]+'.tex'
	# texfile = open(texfilename,'w')
	# header = ['\documentclass{article}',
	# '\\usepackage[top=50pt, bottom=50pt, left=60pt, right=60pt]{geometry}',
	# '\\usepackage{graphicx}', 
	# '\\usepackage[bottom]{footmisc}',
	# '\\usepackage{enumerate,verbatim}',
	# '\\usepackage{amssymb,amsmath,ulem,amsthm}',
	# '\\usepackage{transparent,float}']

	# for item in header:
	# 	texfile.write(item+'\n')
	# texfile.write('\\begin{document}\n')
	# for i in range(6,0,-1):
	# 	texfile.write('\\begin{figure}[!ht]\n')
	# 	texfile.write('\\centering\n')
	# 	texfile.write('\\includegraphics[width=0.4\\textwidth]{../../'+\
	# 		os.path.dirname(filename)+'/'+'images/' + os.path.basename(filename)[:-4]+'_m'+str(i)+\
	# 		'_in.pdf}\hspace{0.05\\textwidth}\n')
	# 	texfile.write('\\includegraphics[width=0.4\\textwidth]{../../'+\
	# 		os.path.dirname(filename)+'/'+'images/' + os.path.basename(filename)[:-4]+'_m'+str(i)+\
	# 		'_out.pdf}\hspace{0.05\\textwidth}\\\\\n')
	# 	texfile.write('\\caption{'+'Results for Module '+str(i)+'.}')	              
	# 	texfile.write('\\end{figure}\n')
	# 	if(i == 5 or i == 3):
	# 		texfile.write('\\clearpage\n')    
	# texfile.write('\end{document}\n')
	# texfile.close()
	# call('pdflatex '+texfilename+'>/dev/null',shell=True)
