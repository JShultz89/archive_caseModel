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

csvcol = defaultdict(list) 
csvfile = open('Feb11.csv','rU')
cr = csv.DictReader(csvfile)
for row in cr: # read a row as {column1: value1, column2: value2,...}
  for (k,v) in row.items(): # go over each column name and value 
  	csvcol[k].append(float(v))

time = csvcol['Timestamp'];

""" Boundary flux blocks """
""" All these blocks remain constant """
# define inlet water with initial state
waterTemp = 20
w0 = b.Block('waterInlet','constWater',T = csvcol['exp_inlet'][50])

# define inlet air with initial state
a0 = b.Block('airInlet','constAir',T = 22)

# We will need mass flow rates for our fluxes, so initialize them here
# These are added to the class object, and are not part of the
# default block requirement

## Define an unsteady boundary block for inlet and outlet by adding a source
# Tentatively solve from 0 to 1, drive it with 
w0.addSource(s.Source('time', T = lambda t: interp1d(time,csvcol['exp_inlet'])(t),kind='quadratic' ))
a0.addSource(s.Source('time', T = lambda t: 22 ))


w0.mdot = 8.5e-07*w0.m['rho'](w0.state)
a0.mdot = 2.0*a0.m['rho'](a0.state)*0.16

# All these boundary blocks need are temperatures
# define Exterior boundary condition
aExt = b.Block('Exterior','air',T = 25.0)
# define Interior boundary condition
aInt = b.Block('Interior','air',T = 22.5)

""" Sources used in even numbered blocks """


""" Block Initialization """

# Initial lists of blocks
water = []
air = []

# add in the inflow block to make it easy to connect blocks
# These blocks are not used in the solve
water.append(w0)
air.append(a0)
L = 0.29
LMod = 0.01
n = 6
#### Initialize the blocks we will solve on
for i in range(1,2*n+1):

	if(i % 2 == 1): # odd regions are "tube" regions
		# Every block is named for its material in this case
		water.append(b.Block('waterTube' + str((i+1)/2),'constWater',T = csvcol['exp_outlet'][50]))
		air.append(b.Block('airTube' + str((i+1)/2),'constAir',T = 22))
		# Water tube has one flux for heat conduction
		if( i == 1 ): 
			water[i].addFlux(f.Flux(air[i],'heatCondSimple',{'type':'wa','m':[],'L':L/2}))
			# Air has three, corresponding to the windows and the water-tube
			air[i].addFlux(f.Flux(water[i],'heatCondSimple',{'type':'wa','m':[],'L':L/2}))
			air[i].addFlux(f.Flux(aInt,'heatCondSimple',{'type':'int','m':[],'L':L/2}))
			air[i].addFlux(f.Flux(aExt,'heatCondSimple',{'type':'ext','m':[],'L':L/2}))
				# need to set up time dependent functions
			air[i].T = lambda state : {'T': -1.2*0.048*1.005/2.0}
			water[i].T = lambda state : {'T': -998.0*2.12e-6*4.218/2.0}
		else:
			water[i].addFlux(f.Flux(air[i],'heatCondSimple',{'type':'wa','m':[],'L':L}))
			air[i].addFlux(f.Flux(water[i],'heatCondSimple',{'type':'wa','m':[],'L':L}))
			air[i].addFlux(f.Flux(aInt,'heatCondSimple',{'type':'int','m':[],'L':L}))
			air[i].addFlux(f.Flux(aExt,'heatCondSimple',{'type':'ext','m':[],'L':L}))
				# need to set up time dependent functions
			air[i].T = lambda state : {'T': -1.2*0.048*1.005}
			water[i].T = lambda state : {'T': -998.0*2.12e-6*4.218}
	else: # These are "module" region
		# Every block is named for its material in this case
		water.append(b.Block('waterModule' + str(i/2),'water',T =  csvcol['exp_outlet'][50]))
		air.append(b.Block('airModule' + str(i/2),'air',T = 22))
		water[i].addSource(s.Source('time', T = lambda t: -0.001*0.65*interp1d(time,csvcol['heatgen_m'+str(i/2)])(t),kind='quadratic'))
		# air[i].addSource(s.Source('const',T = 0))

		water[i].addFlux(f.Flux(air[i],'heatCondSimple',{'type':'wa','m':[],'L':LMod}))
		air[i].addFlux(f.Flux(water[i],'heatCondSimple',{'type':'wa','m':[],'L':LMod}))
		air[i].addFlux(f.Flux(aInt,'heatCondSimple',{'type':'int','m':[],'L':LMod}))
		air[i].addFlux(f.Flux(aExt,'heatCondSimple',{'type':'ext','m':[],'L':LMod}))
		# lets assume a small mass, and see what happens
		air[i].T = lambda state : {'T': -1.2*0.048*LMod/L*1.005}
		water[i].T = lambda state : {'T': -998.0*2.12e-6*LMod/L*4.218}



	# These are the connectivity between regions, each block takes heat
	# from the block "below" it
	air[i].addFlux(f.Flux(air[i-1],'heatConvection'))
	water[i].addFlux(f.Flux(water[i-1],'heatConvection'))

	# These are needed for window calculations
	air[i].mdot = a0.mdot
	water[i].mdot = w0.mdot
#### END OF INITIALIZATION

end = -50
""" Problem Initialization """
# Start the problem with solvable blocks, which
# are all the blocks except the first two
ICSolar = p.Problem(air[1::]+water[1::],[a0,w0])
ICSolar.solve(time[50]);
soln = ICSolar.solveUnst(time[50:end])
t0 = time[0];
# for i in range(1,7):
print [(s,soln[s][-1]) for s in soln]
plt.plot(np.array(soln['t'])-t0, np.array(soln['waterModule6_T']),linewidth=2.0,label='Model');
plt.plot(np.array(time[50:end])-t0, np.array(csvcol['exp_outlet'][50:end]),linewidth=2.0,label='Expt');
plt.plot(np.array(time[50:end])-t0, np.array(csvcol['exp_inlet'][50:end]),linewidth=2.0,label='Inlet');

plt.xlabel('Time (s)')
plt.ylabel('Temperature (C)')
plt.legend(loc=0)

plt.savefig('Feb11_unst_10.png')
# plt.show()
plt.close()