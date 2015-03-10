"""
Document here, for DRIPS model
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

""" Boundary flux blocks """
""" All these blocks remain constant """
# define inlet water with initial state
w0 = b.Block('waterInlet','constWater',T = 50.0, m = 3.2e-6)

# define inlet air with initial state
a0 = b.Block('airInlet','airVapor',T = 28.0, m = 0.5, mvapor = 0.0)



# All these boundary blocks need are temperatures
# define Exterior boundary condition
aExt = b.Block('Exterior','constAir',T = 20.0)
# define Interior boundary condition
aInt = b.Block('Interior','constAir',T = 22.5)

# Here, constant sources are defined using the optional arguments
# to pass in information about the source variable (Temperature)
# and its value



# Initial lists of blocks
water = []
air = []

# add in the inflow block to make it easy to connect blocks
# These blocks are not used in the solve
water.append(w0)
air.append(a0)
L = 0.3
n = 1
#### Initialize the blocks we will solve on
for i in range(1,2*n+1):

	if(i % 2 == 1): # odd regions are "tube" regions
		# Every block is named for its material in this case
		water.append(b.Block('waterTube' + str((i+1)/2),'constWater',T = 15,m = 3.2e-6))
		air.append(b.Block('airTube' + str((i+1)/2),'airVapor',T = 22.5,m = 0.5, mvapor = 0.0))
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
		water.append(b.Block('waterModule' + str(n-i/2),'water',T = 15,m = 3.2e-6))
		air.append(b.Block('airModule' + str(n-i/2),'airVapor',T = 22.5,m = 0.5, mvapor = 0.0))
		water[i].addSource(s.Source('const',T = 0.003))
		water[i].addSource(s.Source('const',m = 1.e-7))
		air[i].addSource(s.Source('const',m = 0.01, mvapor = 0.01))



	# These are the connectivity between regions, each block takes heat
	# from the block "below" it
	air[i].addFlux(f.Flux(air[i-1],'heatConvDripsAirVapor'))
	water[i].addFlux(f.Flux(water[i-1],'heatConvDripsWater'))

	# add in mass fluxes
	air[i].addFlux(f.Flux(air[i-1],'massFlux'))
	water[i].addFlux(f.Flux(water[i-1],'massFlux'))

#### END OF INITIALIZATION

""" Problem Initialization """

# Start the problem with solvable blocks, which
# are all the blocks except the first two
Drips = p.Problem(air[1::]+water[1::])
Drips.solve()
for blk in air[1::]+water[1::]:
	blk.printMe()