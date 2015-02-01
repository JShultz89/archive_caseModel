import src.materials as mat
import src.blocks as b
import numpy as np
import src.flux as f
from scipy.optimize import fsolve

################# Geometries
# radius -> [inner, tubing, insulation]
L = 0.3
tubeGeom = {'type':'cyl','r':np.cumsum([3.0,1.675,9.525])*1e-3/2,'L':L,\
'cL':L,'m':['silicon tubing','silicon insulation']}
windowGeom = {'type':'plate','w':0.3,'L':L,'cL':0.006,'m':['glass']}
IGUGeom = {'type':'plate','w':0.3,'L':L,'cL':0.006,'m':['glass','argon','glass']}

# define inlet water
w0 = b.Block('water0','water')
w0.T = 13
# define inlet air
a0 = b.Block('air0','air')
a0.T = 20

w0.mdot = 8.5e-07*w0.m.rho(w0.T)
a0.mdot = 2.0*a0.m.rho(a0.T)
# define Exterior boundary condition
aExt = b.Block('Exterior','air')
aExt.T = 25.0
# define Interior boundary condition
aInt = b.Block('Interior','air')
aInt.T = 22.5

################# Sources
qw = 0.008 # Heat flow into water from Module Heat Receiver
qa = 0.003 # Heat flow into air from Heat Loss from the Module
# Define as token function
Sa = lambda T: qa
Sw = lambda T: qw


n = 1
# There are n modules, and n+1 "tube" regions
water = []
air = []
water.append(w0)
air.append(a0)

for i in range(1,2*n+2):
	# odd regions are "tube" regions

	if(i % 2 == 1):
		water.append(b.Block('waterTube' + str(i),'water'))
		air.append(b.Block('airTube' + str(i),'air')) 

		water[i].addFlux(f.Flux(water[i],air[i],'cond',tubeGeom))
		air[i].addFlux(f.Flux(water[i],air[i],'cond',tubeGeom))
		air[i].addFlux(f.Flux(aInt,air[i],'cond',IGUGeom))
		air[i].addFlux(f.Flux(aExt,air[i],'cond',windowGeom))
	else:
		# These are "boundary" regions
		water.append(b.Block('waterTube' + str(i),'water'))
		air.append(b.Block('airTube' + str(i),'air'))

		water[i].addSource(Sw)
		air[i].addSource(Sa)

	air[i].addFlux(f.Flux(air[i-1],air[i],'conv'))
	water[i].addFlux(f.Flux(water[i-1],water[i],'conv'))
	air[i].T = 22
	water[i].T = 15
	air[i].mdot = a0.mdot
	water[i].mdot = w0.mdot
blocks = air[1::]+water[1::]
T0 = [b.T for b in blocks]

print T0
def residual(T):
	b = air[1::]+water[1::]
	for i in range(0,len(T)):
		b[i].T = T[i]
	return [block.r() for block in b]

for b in blocks:
	print b.name, b.T

	fsolve(residual,T0)

for b in blocks:
	print b.name, b.T