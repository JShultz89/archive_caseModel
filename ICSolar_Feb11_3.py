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
def solve(heatGen,waterTemp,n):
	""" Boundary flux blocks """
	""" All these blocks remain constant """
	# define inlet water with initial state
	w0 = b.Block('waterInlet','constWater',T = waterTemp)

	# define inlet air with initial state
	a0 = b.Block('airInlet','constAir',T = 28)

	# We will need mass flow rates for our fluxes, so initialize them here
	# These are added to the class object, and are not part of the
	# default block requirement
	w0.mdot = 1.61e-6*w0.m['rho'](w0.state)
	a0.mdot = 2.0*a0.m['rho'](a0.state)*0.16

	# All these boundary blocks need are temperatures
	# define Exterior boundary condition
	aExt = b.Block('Exterior','air',T = 20.0)
	# define Interior boundary condition
	aInt = b.Block('Interior','air',T = 22.5)

	""" Sources used in even numbered blocks """

	# Here, constant sources are defined using the optional arguments
	# to pass in information about the source variable (Temperature)
	# and its value
	qa = 0 # Heat flow into air from Heat Loss from the Module

	Sa = s.Source('const',T = qa)
	

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
			# Every block is named for its material in this case
			water.append(b.Block('waterTube' + str((i+1)/2),'constWater',T = 15))
			air.append(b.Block('airTube' + str((i+1)/2),'constAir',T = 22.5))
			# Water tube has one flux for heat conduction
			if( i == 1 ): 
				water[i].addFlux(f.Flux(air[i],'heatCondSimple',{'type':'wa','m':[],'L':L/2.0}))
				# Air has three, corresponding to the windows and the water-tube
				air[i].addFlux(f.Flux(water[i],'heatCondSimple',{'type':'wa','m':[],'L':L/2.0}))
				air[i].addFlux(f.Flux(aInt,'heatCondSimple',{'type':'int','m':[],'L':L/2.0}))
				air[i].addFlux(f.Flux(aExt,'heatCondSimple',{'type':'ext','m':[],'L':L/2.0}))
			else:
				water[i].addFlux(f.Flux(air[i],'heatCondSimple',{'type':'wa','m':[],'L':L}))
				air[i].addFlux(f.Flux(water[i],'heatCondSimple',{'type':'wa','m':[],'L':L}))
				air[i].addFlux(f.Flux(aInt,'heatCondSimple',{'type':'int','m':[],'L':L}))
				air[i].addFlux(f.Flux(aExt,'heatCondSimple',{'type':'ext','m':[],'L':L}))
		else: # These are "module" region
			# Every block is named for its material in this case
			water.append(b.Block('waterModule' + str(n-i/2),'water',T = 15))
			air.append(b.Block('airModule' + str(n-i/2),'air',T = 22.5))
			water[i].addSource(s.Source('const',T = -heatGen[n-i/2]*1e-3))
			air[i].addSource(Sa)

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
	ICSolar = p.Problem(air[1::]+water[1::])
	ICSolar.solve()
	# ICSolar.printSolution()
	# air[0].printMe()
	# water[0].printMe()
	# print a0.mdot
	# print w0.mdot
	mTemp = []
	for ww in water:
		# if 'Module' in ww.name:
		mTemp.append(float(ww.state['T']))
	return mTemp
	
if __name__ == "__main__":
	if len(sys.argv) < 4:
		csvfile = open('Feb11.csv','rU')
		csvwrite = open('Feb11_sim.csv','w')
		cr = csv.DictReader(csvfile)
		cw = csv.DictWriter(csvwrite,['Timestamp','exp_inlet','exp_outlet','sim_outlet'])
		cw.writeheader()
		Tin = []
		Tout = []
		# TsimA = []
		numMod = 6
		TsimW = []
		AllW =[]

		for row in cr:
			heatGen = [float(row['heatgen_m'+str(i)]) for i in range(1,7)]
			waterTemp = float(row['exp_inlet'])
			Wt = solve(heatGen,waterTemp,numMod)
			WtEnd = Wt[-1]
			cw.writerow({'Timestamp':row['Timestamp'],'exp_inlet':row['exp_inlet'], \
				'exp_outlet':row['exp_outlet'],'sim_outlet':round(WtEnd,8)})
			TsimW.append(WtEnd)
			AllW.append(Wt)
			# TsimA.append(Ta)
			Tout.append(row['exp_outlet'])
			Tin.append(waterTemp)
		csvfile.close()
		csvwrite.close()
		i = range(0,len(Tin))
		plt.plot(i,Tin,linewidth=2.0,label='Inlet')
		plt.plot(i,Tout,linewidth=2.0,label='Expt - Water')
		plt.plot(i,TsimW,linewidth=2.0,label='Model - Water')
		# plt.plot(i,TsimA,linewidth=2.0,label='Model-Air')

		plt.legend(loc=0)
		plt.xlabel('Measurement number (~time)')
		plt.ylabel('Temperature (C)')
		plt.title('Comparison with Expt for ' + str(numMod) + ' Modules')
		# plt.ylim([float(min(TsimW))-10,float(max(Tout))+20])
		# plt.show()
		plt.savefig('feb11.png')
		plt.close()
		for j in range(0,len(Wt)):
			Wj = [w[j] for w in AllW]
			# if (j > 0 and j % 2 == 0):
			# 	name = 'Module '+str(j/2)
			# elif ( j == 0 ):
			# 	name = 'Inlet'
			# else:
			name = 'Region '+str(j)
			plt.plot(i,Wj,linewidth=2.0,label=name)
		# plt.legend(loc=0)
		plt.xlabel('Measurement number (~time)')
		plt.ylabel('Temperature (C)')
		plt.title('Individual Region Temperatures')		
		plt.savefig('feb11modules.png')
		plt.close()


	else:
		print solve(float(sys.argv[1]),float(sys.argv[2]),int(sys.argv[3]))