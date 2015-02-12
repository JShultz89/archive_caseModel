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
w0.mdot = 0.00005 
a0.mdot = 0.005

# All these boundary blocks need are temperatures
# define Exterior boundary condition
aExt = b.Block('Exterior','air',T = 25.0)
# define Interior boundary condition
aInt = b.Block('Interior','air',T = 22.5)

""" Sources used in even numbered blocks """

# Here, constant sources are defined using the optional arguments
# to pass in information about the source variable (Temperature)
# and its value
qa = -0.008 # Heat flow into water from Module Heat Receiver
qw = -0.003 # Heat flow into air from Heat Loss from the Module

Sa = s.Source('const',T = qa)
Sw = s.Source('const',T = qw)

""" Block Initialization """


w1 = b.Block('water1','constWater',T=13)
w2 = b.Block('water2','constWater',T=13)
a1 = b.Block('air1','constAir',T=20)
a2 = b.Block('air2','constAir',T=20)

w1.mdot = w0.mdot
w2.mdot = w1.mdot
a1.mdot = a0.mdot
a2.mdot = a1.mdot

a2.addSource(Sa)
w2.addSource(Sw)

a1.addFlux(f.Flux(aExt,'heatCondEasy',extGeom))
a1.addFlux(f.Flux(aInt,'heatCondEasy',intGeom))
a1.addFlux(f.Flux(w1,'heatCondEasy',tubeGeom))
a1.addFlux(f.Flux(a0,'heatConvection'))
w1.addFlux(f.Flux(a1,'heatCondEasy',tubeGeom))
w1.addFlux(f.Flux(w0,'heatConvection'))

a2.addFlux(f.Flux(a1,'heatConvection'))
w2.addFlux(f.Flux(w1,'heatConvection'))



""" Problem Initialization """

# Start the problem with solvable blocks, which
# are all the blocks except the first two
ICSolar = p.Problem([a1,a2,w1,w2])
ICSolar.solve()
ICSolar.printSolution()
