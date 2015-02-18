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
from numpy import cumsum # this is used once in tube geometry

""" Geometries used for fluxes """
# radius -> [inner, tubing, insulation]
L = 0.3

# this is the water tube geometry dictionary, consisting of two materials
# and corresponding radii. 
# tubeGeom = {'type':'cyl','r':cumsum([3.0,1.675,9.525])*1e-3/2,'L':L,\
# 'cL':L,'m':['silicon_tubing','silicon_insulation']}

# # this is the outer window, which is a single layer of glass
# windowGeom = {'type':'plate','w':0.3,'L':L,'cL':0.006,'m':['glass']}

# # this is the double layer window, glass, then argon, then glass
# IGUGeom = {'type':'plate','w':0.3,'L':L,'cL':0.006,'m':['glass','argon','glass']}

tubeGeom = {'type':'wa','m':[]}
intGeom = {'type':'int','m':[]}
extGeom = {'type':'ext','m':[]}
""" Boundary flux blocks """
""" All these blocks remain constant """
# define inlet water with initial state
w0 = b.Block('water0','water',T = 13)

# define inlet air with initial state
a0 = b.Block('air0','air',T = 20)

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
qw = -0.008 # Heat flow into water from Module Heat Receiver
qa = -0.003 # Heat flow into air from Heat Loss from the Module

Sa = s.Source('const',T = qa)
Sw = s.Source('const',T = qw)

""" Block Initialization """

# Number of modules
n = 2
# Initial lists of blocks
water = []
air = []

# add in the inflow block to make it easy to connect blocks
# These blocks are not used in the solve
water.append(w0)
air.append(a0)

#### Initialize the blocks we will solve on
for i in range(1,2*n):
	# Every block is named for its material in this case
	water.append(b.Block('water' + str(i),'water',T = 15))
	air.append(b.Block('air' + str(i),'air',T = 22))

	if(i % 2 == 1): # odd regions are "tube" regions
		# Water tube has one flux for heat conduction
		water[i].addFlux(f.Flux(air[i],'heatCondEasy',tubeGeom))
		# Air has three, corresponding to the windows and the water-tube
		air[i].addFlux(f.Flux(water[i],'heatCondEasy',tubeGeom))
		air[i].addFlux(f.Flux(aInt,'heatCondEasy',intGeom))
		air[i].addFlux(f.Flux(aExt,'heatCondEasy',extGeom))
	else: # These are "module" region
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
air[0].printMe()
water[0].printMe()

ICSolar.printSolution()
