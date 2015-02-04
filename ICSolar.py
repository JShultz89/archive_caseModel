import src.materials as mat
import src.blocks as b
import numpy as np
import src.flux as f
from scipy.optimize import fsolve

################# Geometries
# radius -> [inner, tubing, insulation]
L = 0.3
tubeGeom = {'type':'cyl','r':np.cumsum([3.0,1.675,9.525])*1e-3/2,'L':L,\
'cL':L,'m':['silicon_tubing','silicon_insulation']}
windowGeom = {'type':'plate','w':0.3,'L':L,'cL':0.006,'m':['glass']}
IGUGeom = {'type':'plate','w':0.3,'L':L,'cL':0.006,'m':['glass','argon','glass']}

# define inlet water
w0 = b.Block('water0','water')
w0.var['T'] = 13
# define inlet air
a0 = b.Block('air0','air')
a0.var['T'] = 20

w0.mdot = 8.5e-07*w0.m['rho'](w0.var)
a0.mdot = 2.0*a0.m['rho'](a0.var)
# define Exterior boundary condition
aExt = b.Block('Exterior','air')
aExt.var['T'] = 25.0
# define Interior boundary condition
aInt = b.Block('Interior','air')
aInt.var['T'] = 22.5

################# Sources
qw = 0.008 # Heat flow into water from Module Heat Receiver
qa = 0.003 # Heat flow into air from Heat Loss from the Module
# Define as token function, of a block
Sa = lambda b: -qa
Sw = lambda b: -qw


n = 5
# There are n modules, and n+1 "tube" regions
water = [w0]
air = [a0]

for i in range(1,2*n+2):
	# odd regions are "tube" regions

	if(i % 2 == 1):
		water.append(b.Block('waterTube' + str(i),'water'))
		air.append(b.Block('airTube' + str(i),'air')) 

		water[i].addFlux(f.Flux(water[i],air[i],'heatcond',tubeGeom))
		air[i].addFlux(f.Flux(water[i],air[i],'heatcond',tubeGeom))
		air[i].addFlux(f.Flux(aInt,air[i],'heatcond',IGUGeom))
		air[i].addFlux(f.Flux(aExt,air[i],'heatcond',windowGeom))
	else:
		# These are "boundary" regions
		water.append(b.Block('waterTube' + str(i),'water'))
		air.append(b.Block('airTube' + str(i),'air'))

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
def residual(var):
	b = air[1::]+water[1::]
	for i in range(0,len(var)):
		b[i].var['T'] = var[i]
	return [block.r() for block in b]

# print initial 
# for b in blocks:
# 	print b.name, b.T

# solve it using whatever scipy decides we should use
fsolve(residual, [b.var['T'] for b in blocks])

# print final solution
for b in blocks:
	print b.name, b.var['T']