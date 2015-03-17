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
from scipy.interpolate import interp1d
from collections import defaultdict
from subprocess import call
import os.path
from os import chdir
from time import clock
def solve(data,n,start,end):

	timesteps = data['Timestamp']

	""" Boundary flux blocks """
	""" All these blocks remain constant """

	w0 = b.Block('waterInlet','constWater',T = data['exp_inlet'][start])

	# define inlet air with initial state
	if('Tamb' not in data.keys() or 'm1_out' not in data.keys()):
		print "Not enough data in the file"
		sys.exit(0)
	Tamb = data['Tamb'][start]
	# else:
	# 	Tamb = 22.5
	# 	data['Tamb'] = [22.5]*len(data['Timestamp'])

	a0 = b.Block('airInlet','constAir',T = Tamb)
	# We will need mass flow rates for our fluxes, so initialize them here
	# These are added to the class object, and are not part of the
	# default block requirement

	## Define an unsteady boundary block for inlet and outlet by adding a source
	# Tentatively solve from 0 to 1, drive it with 
	w0.addSource(s.Source('time', T = lambda t: interp1d(timesteps,data['exp_inlet'])(t),kind='linear'))
	a0.addSource(s.Source('time', T = lambda t: interp1d(timesteps,data['Tamb'])(t),kind='linear'))

	w0.mdot = lambda w0 : interp1d(timesteps,data['exp_flowrate'],kind='linear')(w0.t)*1.0e-6*w0.m['rho'](w0.state)
	a0.mdot = lambda a0 : 2.0*a0.m['rho'](a0.state)*0.16

	# All these boundary blocks need are temperatures
	# define Exterior boundary condition
	aExt = b.Block('Exterior','air',T = Tamb)
	aExt.addSource(s.Source('time', T = lambda t: interp1d(timesteps,data['Tamb'])(t),kind='linear'))

	# define Interior boundary condition
	aInt = b.Block('Interior','air',T = Tamb)
	aInt.addSource(s.Source('time', T = lambda t: interp1d(timesteps,data['Tamb'])(t),kind='linear')) 

	""" Sources used in even numbered blocks """


	""" Block Initialization """

	# Initial lists of blocks
	water = []
	air = []

	# add in the inflow block to make it easy to connect blocks
	# These blocks are not used in the solve
	water.append(w0)
	air.append(a0)
	L = 0.15
	LMod = 0.3-L

	#### Initialize the blocks we will solve on
	for i in range(1,2*n+1):

		if(i % 2 == 1): # odd regions are "tube" regions
			# Every block is named for its material in this case
			water.append(b.Block('m' + str(n-i/2)+'_in','constWater',T = data['m' + str(n-i/2)+'_in'][start]))
			air.append(b.Block('airTube' + str((i+1)/2),'constAir',T = Tamb))
			# Water tube has one flux for heat conduction
			if( i == 1 ): 
				water[i].addFlux(f.Flux(air[i],'heatCondSimple',{'type':'wa','m':[],'L':L/2}))
				# Air has three, corresponding to the windows and the water-tube
				air[i].addFlux(f.Flux(water[i],'heatCondSimple',{'type':'wa','m':[],'L':L/2}))
				air[i].addFlux(f.Flux(aInt,'heatCondSimple',{'type':'int','m':[],'L':L/2}))
				air[i].addFlux(f.Flux(aExt,'heatCondSimple',{'type':'ext','m':[],'L':L/2}))
					# need to set up timesteps dependent functions
				air[i].T = lambda state : {'T': -1.2*0.048*L/0.3*1.005/2.0}
				water[i].T = lambda state : {'T': -998.0*2.12e-6*L/0.3*4.218/2.0}
			else:
				water[i].addFlux(f.Flux(air[i],'heatCondSimple',{'type':'wa','m':[],'L':L}))
				air[i].addFlux(f.Flux(water[i],'heatCondSimple',{'type':'wa','m':[],'L':L}))
				air[i].addFlux(f.Flux(aInt,'heatCondSimple',{'type':'int','m':[],'L':L}))
				air[i].addFlux(f.Flux(aExt,'heatCondSimple',{'type':'ext','m':[],'L':L}))
					# need to set up timesteps dependent functions
				air[i].T = lambda state : {'T': -1.2*0.048*L/0.3*1.005}
				water[i].T = lambda state : {'T': -998.0*2.12e-6*L/0.3*4.218}
		else: # These are "module" region
			# Every block is named for its material in this case
			water.append(b.Block('m' + str(n-i/2+1)+'_out','water',T = data['m' + str(n-i/2+1)+'_out'][start]))
			air.append(b.Block('airModule' + str(n-i/2+1),'air',T = Tamb))

			water[i].addSource(s.Source('time', T = lambda t: -0.001*interp1d(timesteps,data['heatgen_m'+str(n-i/2+1)])(t),kind='linear'))
			air[i].addSource(s.Source('const',T = 0))

			water[i].addFlux(f.Flux(air[i],'heatCondSimple',{'type':'wa','m':[],'L':LMod}))
			air[i].addFlux(f.Flux(water[i],'heatCondSimple',{'type':'wa','m':[],'L':LMod}))
			air[i].addFlux(f.Flux(aInt,'heatCondSimple',{'type':'int','m':[],'L':LMod}))
			air[i].addFlux(f.Flux(aExt,'heatCondSimple',{'type':'ext','m':[],'L':LMod}))
			# lets assume a small mass, and see what happens
			air[i].T = lambda state : {'T': -1.2*0.048*LMod/0.3*1.005}
			water[i].T = lambda state : {'T': -998.0*2.12e-6*LMod/0.3*4.218}

		# These are the connectivity between regions, each block takes heat
		# from the block "below" it
		air[i].addFlux(f.Flux(air[i-1],'heatConvection'))
		water[i].addFlux(f.Flux(water[i-1],'heatConvection'))

		# These are needed for window calculations
		water[i].mdot = lambda w0 : interp1d(timesteps,data['exp_flowrate'],kind='linear')(w0.t)*1.0e-6*w0.m['rho'](w0.state)
		air[i].mdot = lambda a0 : 2.0*a0.m['rho'](a0.state)*0.16

	#### END OF INITIALIZATION

	""" Problem Initialization """
	# Start the problem with solvable blocks, which
	# are all the blocks except the first two
	ICSolar = p.Problem(air[1::]+water[1::],[a0,w0,aExt,aInt])
	starttime = clock()
	# ICSolar.solve(timesteps[start])
	soln = ICSolar.solveUnst(timesteps[start:end])
	print (clock() - starttime)/len(timesteps[start:end]), " seconds per timestep"
	return soln
if __name__ == "__main__":
	filename = sys.argv[1]
	csvfile = open(filename,'rU')
	csvwrite = open(os.path.dirname(filename)+'/model/' + os.path.basename(filename)[:-4]+ \
		'_model_unsteady.csv','w')
	cr = csv.DictReader(csvfile)
	# read in all the data
	data = defaultdict(list) 
	for row in cr: # read a row as {column1: value1, column2: value2,...}
	  for (k,v) in row.items(): # go over each column name and value 
	  	data[k].append(float(v))

	numModules = 6

	csvHeader = ['Timestamp','exp_inlet'] 
	for i in range(6,0,-1):
		csvHeader.append('m'+str(i)+'_in')
		csvHeader.append('m'+str(i)+'_out')
		data['m'+str(i)+'_in_mod'] = [];
		data['m'+str(i)+'_out_mod'] = [];
	cw = csv.DictWriter(csvwrite,csvHeader)
	cw.writeheader()
	# for each line, run the data
	start = 20
	end = len(data['Timestamp'])-20
	soln = solve(data,numModules,start,end)
	for i in range(0,end-start):
		results = {}
		results['Timestamp'] = data['Timestamp'][i+start]
		results['exp_inlet'] = data['exp_inlet'][i+start]
		for j in range(1,7):
			data['m'+str(j)+'_in_mod'].append(soln['m'+str(j)+'_in_T'][i])
			data['m'+str(j)+'_out_mod'].append(soln['m'+str(j)+'_out_T'][i])
			results['m'+str(j)+'_in'] = soln['m'+str(j)+'_in_T'][i]
			results['m'+str(j)+'_out'] = soln['m'+str(j)+'_out_T'][i]
		cw.writerow(results)
	csvfile.close()
	csvwrite.close()


	
	for j in range(1,7):
		plt.plot(soln['t'],data['exp_inlet'][start:end],linewidth=2.0,label='Inlet')
		plt.plot(soln['t'],data['m'+str(j)+'_out'][start:end],linewidth=2.0,label='Expt')
		plt.plot(soln['t'],data['m'+str(j)+'_out_mod'][0:(end-start)],linewidth=2.0,label='Model')
		plt.legend(loc=0)
		plt.xlabel('Measurement number (~timesteps)')
		plt.ylabel('Temperature (C)')
		plt.title(filename[:-4]+' m'+str(j)+'_out')
		fig = plt.gcf()
		fig.set_size_inches(4,4)

		plt.savefig(os.path.dirname(filename)+'/images/' + os.path.basename(filename)[:-4]+'_m'+str(j)+'_out_unsteady.pdf')		
		plt.close()

		plt.plot(soln['t'],data['exp_inlet'][start:end],linewidth=2.0,label='Inlet')
		plt.plot(soln['t'],data['m'+str(j)+'_in'][start:end],linewidth=2.0,label='Expt')
		plt.plot(soln['t'],data['m'+str(j)+'_in_mod'][0:(end-start)],linewidth=2.0,label='Model')

		plt.legend(loc=0)
		plt.xlabel('Measurement number (~timesteps)')
		plt.ylabel('Temperature (C)')
		plt.title(filename[:-4]+' m'+str(j)+'_in')
		fig = plt.gcf()
		fig.set_size_inches(4,4)
		plt.savefig(os.path.dirname(filename)+'/images/' + os.path.basename(filename)[:-4]+'_m'+str(j)+'_in_unsteady.pdf')
		plt.close()

		# lets do this manually
	chdir('doc/ICSolar')
	texfilename = 'Unsteady_'+os.path.basename(filename)[:-4]+'.tex'
	texfile = open(texfilename,'w')
	header = ['\documentclass{article}',
	'\\usepackage[top=50pt, bottom=50pt, left=60pt, right=60pt]{geometry}',
	'\\usepackage{graphicx}', 
	'\\usepackage[bottom]{footmisc}',
	'\\usepackage{enumerate,verbatim}',
	'\\usepackage{amssymb,amsmath,ulem,amsthm}',
	'\\usepackage{transparent,float}']

	for item in header:
		texfile.write(item+'\n')
	texfile.write('\\begin{document}\n')
	for i in range(6,0,-1):
		texfile.write('\\begin{figure}[!ht]\n')
		texfile.write('\\centering\n')
		texfile.write('\\includegraphics[width=0.4\\textwidth]{../../'+\
			os.path.dirname(filename)+'/'+'images/' + os.path.basename(filename)[:-4]+'_m'+str(i)+\
			'_in_unsteady.pdf}\hspace{0.05\\textwidth}\n')
		texfile.write('\\includegraphics[width=0.4\\textwidth]{../../'+\
			os.path.dirname(filename)+'/'+'images/' + os.path.basename(filename)[:-4]+'_m'+str(i)+\
			'_out_unsteady.pdf}\hspace{0.05\\textwidth}\\\\\n')
		texfile.write('\\caption{'+'Results for Module '+str(i)+'.}')	              
		texfile.write('\\end{figure}\n')
		if(i == 5 or i == 3):
			texfile.write('\\clearpage\n')    
	texfile.write('\end{document}\n')
	texfile.close()
	call('pdflatex '+texfilename+'>/dev/null',shell=True)
