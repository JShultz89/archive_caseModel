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
def solve(heatGen,waterTemp,waterFlowRate,airTemp,n,stddev):
	""" Boundary flux blocks """
	""" All these blocks remain constant """
	# define inlet water with initial state
	w0 = b.Block('waterInlet','constWater',T = waterTemp)
	# define inlet air with initial state
	a0 = b.Block('airInlet','constAir',T = airTemp)

	# We will need mass flow rates for our fluxes, so initialize them here
	# These are added to the class object, and are not part of the
	# default block requirement
	w0.mdot = lambda T = 0 : waterFlowRate*1.0e-6*w0.m['rho'](w0.state)
	a0.mdot = lambda T = 0 : 2.0*a0.m['rho'](a0.state)*0.16

	# print heatGen,waterTemp,waterFlowRate,airTemp,n,stddev
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
	L = 0.3
	#### Initialize the blocks we will solve on
	for i in range(1,2*n+1):
		if(i % 2 == 1): # odd regions are "tube" regions
			hh = 2.0
			# Every block is named for its material in this case
			water.append(b.Block('m' + str(n-i/2)+'_in','constWater',T = waterTemp))
			air.append(b.Block('air' + str(n-i/2)+'_in','constAir',T = airTemp))
			# Water tube has one flux for heat conduction
			if( i == 1 ): 
				water[i].addFlux(f.Flux(air[i],'heatCondSimple',{'type':'wa','m':[],'L':L/2.0,'scale':hh}))
				# Air has three, corresponding to the windows and the water-tube
				air[i].addFlux(f.Flux(water[i],'heatCondSimple',{'type':'wa','m':[],'L':L/2.0,'scale':hh}))
				air[i].addFlux(f.Flux(aInt,'heatCondSimple',{'type':'int','m':[],'L':L/2.0}))
				air[i].addFlux(f.Flux(aExt,'heatCondSimple',{'type':'ext','m':[],'L':L/2.0}))
			else:
				water[i].addFlux(f.Flux(air[i],'heatCondSimple',{'type':'wa','m':[],'L':L,'scale':hh}))
				air[i].addFlux(f.Flux(water[i],'heatCondSimple',{'type':'wa','m':[],'L':L,'scale':hh}))
				air[i].addFlux(f.Flux(aInt,'heatCondSimple',{'type':'int','m':[],'L':L}))
				air[i].addFlux(f.Flux(aExt,'heatCondSimple',{'type':'ext','m':[],'L':L}))
		else: # These are "module" region
			# Every block is named for its material in this case
			water.append(b.Block('m' + str(n-i/2+1)+'_out','constWater',T = waterTemp))
			air.append(b.Block('air' + str(n-i/2+1)+'_out','constAir',T = airTemp))
			water[i].addSource(s.Source('const',T = -heatGen))
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
	ICSolar.solve()


	J = ICSolar.jacobian()
	invJ = np.linalg.inv(J)
	numBlocks = len(bToSolve)

	cov = np.zeros(numBlocks)

	Temp = {}
	
	for ix, (i,k) in enumerate(ICSolar.mapping):
		if('m' in ICSolar.b[i].name and 'out' in ICSolar.b[i].name):
			cov[ix] = stddev
			# cov[ix] = 1.0

	sig = np.outer(np.dot(invJ,cov),np.transpose(np.dot(invJ,cov)))
	# sig = np.dot(np.dot(invJ,np.outer(cov,cov)),np.transpose(invJ))

	# names = ['']*24
	for ix, (i,k) in enumerate(ICSolar.mapping):
		# names[ix] = ICSolar.b[i].name
		Temp[ICSolar.b[i].name+'_mod'] = ICSolar.b[i].state['T']
		Temp[ICSolar.b[i].name+'_mod_var'] = np.sqrt(sig[ix][ix])
	# plt.pcolor(sig,cmap='RdBu')
	# plt.colorbar()
	# ax = plt.gca()
	# ax.invert_yaxis()
	# ax.xaxis.tick_top()
	# plt.yticks(np.arange(0.5,24.5),names)
	# plt.xticks(np.arange(0.5,24.5),names,rotation='vertical')
	# plt.grid()
	# plt.show()
	
	# for ww in water[1::]:
	# 	Temp[ww.name] = ww.state['T']
	# for aa in air[1::]:
	# 	Temp[aa.name] = aa.state['T']
	# at each point, I'm going to have	
	return Temp
	
if __name__ == "__main__":
	print sys.argv[1]
	filename = sys.argv[1]
	csvfile = open(filename,'rU')
	csvwrite = open(os.path.dirname(filename)+'/model/' + os.path.basename(filename)[:-4]+ \
		'_model_UQ3'+'.csv','w')
	cr = csv.DictReader(csvfile)
	# read in all the data
	data = defaultdict(list) 
	for row in cr: # read a row as {column1: value1, column2: value2,...}
	  for (k,v) in row.items(): # go over each column name and value 
	  	data[k].append(float(v))

	numModules = 6

	csvHeader = data.keys()
	for i in range(numModules,0,-1):
		csvHeader.append('m'+str(i)+'_in_mod')
		csvHeader.append('m'+str(i)+'_in_mod_var')
		csvHeader.append('m'+str(i)+'_out_mod')
		csvHeader.append('m'+str(i)+'_out_mod_var')

		csvHeader.append('air'+str(i)+'_in_mod')
		csvHeader.append('air'+str(i)+'_in_mod_var')
		csvHeader.append('air'+str(i)+'_out_mod')
		csvHeader.append('air'+str(i)+'_out_mod_var')
	csvHeader.append('heatgen_mod')
	csvHeader.append('heatgen_mod_var')

	cw = csv.DictWriter(csvwrite,csvHeader)
	cw.writeheader()

	start = 0
	end = len(data['DNI'])-1
	while(data['DNI'][start] < 100):
		start = start + 1
	while(data['DNI'][end] < 100):
		end = end-1

	end = end - 20

	sampleSize = 30 # 5 minutes
	# for i in range(start+sampleSize,end):
	for i in range(start,end):

		if (i % 100 == 0):
			print i
		airTemp = data['Tamb'][i]
		# heatGenData = np.array()
		

		# heatGenMean = np.mean(heatGenData)
		# heatGenSTD = np.std(heatGenData)
		pol = [1.11722958e-6,-1.18376465e-3,4.34784474e-1,-3.7253707e1]

		heatGenMean = np.polyval(pol,data['DNI'][i])*1e-3/6.0
		heatGenSTD = 7.225627*1e-3/6.0
		# print i, heatGenMean, heatGenSTD
		waterTemp = data['exp_inlet'][i]
		waterFlowRate = data['exp_flowrate'][i]
		
		results = solve(heatGenMean,waterTemp,waterFlowRate,airTemp,numModules,heatGenSTD)
		for k in data.keys():
			results[k] = data[k][i]
		results['heatgen_mod'] = heatGenMean
		results['heatgen_mod_var'] = heatGenSTD

		cw.writerow(results)
	csvfile.close()
	csvwrite.close()
	# 	