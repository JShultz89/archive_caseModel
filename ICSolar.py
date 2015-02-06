import src.materials as mat
import src.blocks as b
import numpy as np
import src.flux as f
from scipy.optimize import fsolve
#### Variable list
var = ['T']
################# Geometries
# radius -> [inner, tubing, insulation]
L = 0.3 # Length or height of one volume (looking at facade)
W = 0.3 # Width of 1 volume (looking at facade)
tubeGeom = {'type':'cyl','r':np.cumsum([3.0,1.675,9.525])*1e-3/2.0,'L':L,\
'cL':L,'m':['silicon_tubing','silicon_insulation']}
windowGeom = {'type':'plate','w':W,'L':L,'cL':0.006,'m':['glass']}
IGUGeom = {'type':'plate','w':W,'L':L,'cL':0.006,'m':['glass','argon','glass']}

# define inlet water temperature
w0 = b.Block('water0','water',var)
w0.var['T'] = 13
# define inlet air temperature
a0 = b.Block('air0','air',var)
a0.var['T'] = 20

# define inlet water flowrate
w0.mdot = 8.5e-07*w0.m['rho'](w0.var)
# define inlet air flowrate
a0.mdot = 2.0*a0.m['rho'](a0.var)

# define Exterior boundary condition
aExt = b.Block('Exterior','air',var)
aExt.var['T'] = 25.0
# define Interior boundary condition
aInt = b.Block('Interior','air',var)
aInt.var['T'] = 22.5

################# Sources
qw = 0.008 # Heat flow into water from Module Heat Receiver
qa = 0.003 # Heat flow into air from Heat Loss from the Module
# Define as token function, of a block
def Sa(b):
	return {'T':-qa}
def Sw(b):
	return {'T':-qw}


n = 1
# There are n modules, and n+1 "tube" regions
water = [w0]
air = [a0]

for i in range(1,2*n+2):
	# odd regions are "tube" regions
	water.append(b.Block('waterTube' + str(i),'water',var))
	air.append(b.Block('airTube' + str(i),'air',var))
	if(i % 2 == 1):
		water[i].addFlux(f.Flux(water[i],air[i],'heatcond',tubeGeom))
		air[i].addFlux(f.Flux(water[i],air[i],'heatcond',tubeGeom))
		air[i].addFlux(f.Flux(aInt,air[i],'heatcond',IGUGeom))
		air[i].addFlux(f.Flux(aExt,air[i],'heatcond',windowGeom))
	else:
		# These are "boundary" region
		water[i].addSource(Sw)
		air[i].addSource(Sa)

	air[i].addFlux(f.Flux(air[i-1],air[i],'heatconv'))
	water[i].addFlux(f.Flux(water[i-1],water[i],'heatconv'))
	air[i].var['T'] = 22
	water[i].var['T'] = 15
	air[i].mdot = a0.mdot
	water[i].mdot = w0.mdot

# solvable blocks	
blocks = air[1::]+water[1::]

# define the residual function here as the sum over all non boundary blocks
def residual(vars):
	blocks = air[1::]+water[1::]

	for i in range(0,len(vars)/len(var)):
		for j in range(0,len(var)):
			blocks[i].var[var[j]] = vars[len(var)*i+j]

	return [b.r()[v] for b in blocks for v in var]
# print initial 
# for b in blocks:
# 	print b.name, b.T

# solve it using whatever scipy decides we should use
fsolve(residual, [b.var[v] for b in blocks for v in var])

# print final solution
for b in blocks:
	print b.name, b.var['T']