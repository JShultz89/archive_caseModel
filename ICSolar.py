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

# this is the water tube
tubeGeom = {'type':'cyl','r':cumsum([3.0,1.675,9.525])*1e-3/2,'L':L,\
'cL':L,'m':['silicon_tubing','silicon_insulation']}

# this is the outer window, which is a single layer of glass
windowGeom = {'type':'plate','w':0.3,'L':L,'cL':0.006,'m':['glass']}

# this is the double layer window
IGUGeom = {'type':'plate','w':0.3,'L':L,'cL':0.006,'m':['glass','argon','glass']}


""" Boundary flux blocks """
# define inlet water
w0 = b.Block('water0','water')
w0.state['T'] = 13
# define inlet air
a0 = b.Block('air0','air')
a0.state['T'] = 20

w0.mdot = 8.5e-07*w0.m['rho'](w0.state)
a0.mdot = 2.0*a0.m['rho'](a0.state)

# define Exterior boundary condition
aExt = b.Block('Exterior','air')
aExt.state['T'] = 25.0
# define Interior boundary condition
aInt = b.Block('Interior','air')
aInt.state['T'] = 22.5

""" Sources used in even numbered blocks """
qw = 0.008 # Heat flow into water from Module Heat Receiver
qa = 0.003 # Heat flow into air from Heat Loss from the Module

Sa = s.Source('const',**{'T':qa})
Sw = s.Source('const',**{'T':qw})

""" Block Initialization """

# Number of modules
n = 3
# Initial list of blocks
water = [w0]
air = [a0]

# Initial block construction
for i in range(1,2*n+2):
	# Every block is named for its material in this case
	water.append(b.Block('water' + str(i),'water'))
	air.append(b.Block('air' + str(i),'air'))

	if(i % 2 == 1): # odd regions are "tube" regions
		water[i].addFlux(f.Flux(water[i],air[i],'heatConduction',tubeGeom))
		air[i].addFlux(f.Flux(water[i],air[i],'heatConduction',tubeGeom))
		air[i].addFlux(f.Flux(aInt,air[i],'heatConduction',IGUGeom))
		air[i].addFlux(f.Flux(aExt,air[i],'heatConduction',windowGeom))
	else: # These are "module" region
		water[i].addSource(Sw)
		air[i].addSource(Sa)

	# Common fluxes for all blocks
	air[i].addFlux(f.Flux(air[i-1],air[i],'heatConvection'))
	water[i].addFlux(f.Flux(water[i-1],water[i],'heatConvection'))

	# Initialize the state of every block to be the same for now
	air[i].state['T'] = 22
	water[i].state['T'] = 15

	# These are needed for window calculations
	air[i].mdot = a0.mdot
	water[i].mdot = w0.mdot

""" Problem Initialization """

# Start the problem with solvable blocks
ICSolar = p.Problem(air[1::]+water[1::])
ICSolar.solve()
ICSolar.printSolution()