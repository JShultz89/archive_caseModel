"""
This defines the ICSolar model proposed by Assad Oberai

where we our problem is similar to this

<<<<<<< HEAD
					|-------|w|---||
					|    5  |w|   ||
					|  |\	|w|   ||
					|  | \	|w|   ||
					|--| 4|-|w|---||
					|  | /	|w|   ||
					|  |/   |w|   ||
					|       |w|   ||
		exterior	|	 3 	|w|   ||  interior 
					|       |w|   ||
					|  |\	|w|   ||
					|  | \	|w|   ||
					|--| 2|-|w|---||
					|  | /	|w|   ||
					|  |/   |w|   ||
					|    1  |w|   ||
					|-------|w|---||
=======
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
>>>>>>> a2438d6dd5dfcf8bbdf6bdadafc2a99bab80476f

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

def solve(heatGen,waterTemp,n):
	""" Boundary flux blocks """
	""" All these blocks remain constant """
	# define inlet water with initial state
	w0 = b.Block('waterInlet','water',T = waterTemp)

	# define inlet air with initial state
	a0 = b.Block('airInlet','air',T = 20)

	# We will need mass flow rates for our fluxes, so initialize them here
	# These are added to the class object, and are not part of the
	# default block requirement
	w0.mdot = 8.5e-07*w0.m['rho'](w0.state)
	a0.mdot = 2.0*a0.m['rho'](a0.state)

	# All these boundary blocks need are temperatures
	# define Exterior boundary condition
	aExt = b.Block('Exterior','air',T = 25.0)
	# define Interior boundary condition
	aInt = b.Block('Interior','air',T = 22.5)

	""" Sources used in even numbered blocks """

	# Here, constant sources are defined using the optional arguments
	# to pass in information about the source variable (Temperature)
	# and its value
	qw = -heatGen # Heat flow into water from Module Heat Receiver
	qa = -0.003 # Heat flow into air from Heat Loss from the Module

	Sa = s.Source('const',T = qa)
	Sw = s.Source('const',T = qw)

	""" Block Initialization """

	# Initial lists of blocks
	water = []
	air = []

	# add in the inflow block to make it easy to connect blocks
	# These blocks are not used in the solve
	water.append(w0)
	air.append(a0)

	#### Initialize the blocks we will solve on
	for i in range(1,2*n+1):


		if(i % 2 == 1): # odd regions are "tube" regions
			# Every block is named for its material in this case
			water.append(b.Block('waterTube' + str((i+1)/2),'water',T = 15))
			air.append(b.Block('airTube' + str((i+1)/2),'air',T = 22))
			# Water tube has one flux for heat conduction
			if( i == 1 ): 
				water[i].addFlux(f.Flux(air[i],'heatCondSimple',{'type':'wa','m':[],'L':0.15}))
				# Air has three, corresponding to the windows and the water-tube
				air[i].addFlux(f.Flux(water[i],'heatCondSimple',{'type':'wa','m':[],'L':0.15}))
				air[i].addFlux(f.Flux(aInt,'heatCondSimple',{'type':'int','m':[],'L':0.15}))
				air[i].addFlux(f.Flux(aExt,'heatCondSimple',{'type':'ext','m':[],'L':0.15}))
			else:
				water[i].addFlux(f.Flux(air[i],'heatCondSimple',{'type':'wa','m':[],'L':0.3}))
				air[i].addFlux(f.Flux(water[i],'heatCondSimple',{'type':'wa','m':[],'L':0.3}))
				air[i].addFlux(f.Flux(aInt,'heatCondSimple',{'type':'int','m':[],'L':0.3}))
				air[i].addFlux(f.Flux(aExt,'heatCondSimple',{'type':'ext','m':[],'L':0.3}))
		else: # These are "module" region
			# Every block is named for its material in this case
			water.append(b.Block('waterModule' + str(i/2),'water',T = 15))
			air.append(b.Block('airModule' + str(i/2),'air',T = 22))
			water[i].addSource(Sw)
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

	return water[-1].state['T']

if __name__ == "__main__":
	if len(sys.argv) < 4:
		csvfile = open('nov25.csv','rU')
		csvwrite = open('simulation.csv','w')
		cr = csv.DictReader(csvfile)
		cw = csv.DictWriter(csvwrite,['Timestamp','exp_inlet','sim_outlet','exp_outlet','exp_heatgen'])
		cw.writeheader()
		for row in cr:
			heatGen = float(row['exp_heatgen'])
			waterTemp = float(row['exp_inlet'])
			Tf = solve(heatGen*1e-3,waterTemp,12)
			cw.writerow({'Timestamp':row['Timestamp'],'exp_inlet':row['exp_inlet'], \
				'exp_outlet':row['exp_outlet'],'sim_outlet':round(Tf,8),'exp_heatgen':row['exp_heatgen']})
		csvfile.close()
		csvwrite.close()
	else:
		print solve(float(sys.argv[1]),float(sys.argv[2]),int(sys.argv[3]))