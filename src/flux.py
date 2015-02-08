""" 
flux.py contains a list of flux functions 

This is meant to serve as a platform
for all flux functions

Each flux computes the heat transfer rate between two blocks
Each flux contains:
	The left state (.L)
	The right state (.R)
	The type (.f)
	The list of materials between the left and right state (.m)
	The geometry between the left and right state (.G) 
		with the areas .A precomputed

Should we have a state dependent material inside a flux,
ie if glass properties depended on temperature
then glass should be a block itself

------------------------------------
function tests are run by doctest
python flux.py
------------------------------------

"""

import materials 
import numpy as np
from math import pi,log 
class Flux(object):
	"""
	Flux object. Each flux is effectively a boundary condition

	__init__:		Flux Constructor

	input(s):   (L) Left block
							(R) Right block
							(f) Flux function name
							(G) Geometry (optional)
								For now, geometry is not required, 
								as some fluxes don't need it
	output(s):	None
	"""
	def __init__(self,L,R,f,G=None):
		self.L = L
		self.R = R
		self.F = eval('self.'+f) # set up the function
		self.m = []
		
		if G is not None:
			self.G = G
			n = len(G['m'])+2 # number of layers + both sides
			if(G['type'] == 'cyl'):
				self.A = np.zeros(n)
				self.A[0] = 2*pi*G['r'][0]*G['L']
				for i in range(1,n-1): # b.Technically not an area
					self.A[i] = (2*pi*G['L'])/log(G['r'][i]/G['r'][i-1])
				self.A[n-1] = 2*pi*G['r'][n-2]*G['L']
			elif(G['type'] == 'plate'):
				self.A = np.ones(n)*G['w']*G['L']
			for i in range(0,n-2):
				self.m.append(eval('materials.'+G['m'][i]))

	"""
	The following are all flux function choices defined with

	input(s):   (b) (must be left or right block)
	output(s):	dict with entries for the flux for each state contributed to

	Fluxes can have blocks with different physical states
	provided the flux function passes contributions to some of the states

	For example, L.state could have 'T','rho' and R.state could have just 'T'
	as long as the flux between them only affects 'T'


	The bulk of the hard-coding and material calls are in here
	"""

	def heatConduction(self,b):

		"""
		returns the convection heat transfer coefficient at a specific temperature

		"""
		def h(b):
			
			m = b.m
			h = m['k'](b.state)/self.G['cL']
			if(m['name'] == 'water' and self.G['type'] == 'cyl'):
				# Nu_D for Reynold numbers < 2300 (laminar) 
				# and constant wall temperature. 
				# Could use Nu_D = 4.36 for constant heat transfer.
				h *= 3.66
			elif(m['name'] == 'air' and self.G['type'] == 'cyl'):
				Re = b.mdot/m['rho'](b.state)*self.G['cL']/m['mu'](b.state)	
				h *= 0.037*Re**(4.0/5.0)*m['Pr'](b.state)**(1.0/3.0)
			elif(m['name'] == 'air' and self.G['type'] == 'plateLayer'):
				Re = b.mdot/m['rho'](b.state)*self.G['cL']/m['mu'](b.state)
				h *= 0.0296*Re**(4.0/5.0)*m['Pr'](b.state)**(1.0/3.0)
			elif(m['name'] == 'glass'):
				pass
		
			return h		
		# temperature doesnt matter in the layers, as the k are constant
		Res = 1/(self.A[0]*h(self.L)) + \
					np.dot([1/m['k']() for m in self.m],[1/A for A in self.A[1:-1]]) + \
					1/(self.A[-1]*h(self.R))
		F = (self.R.state['T']-self.L.state['T'])/Res
		if(b == self.R): return {'T':F}
		else: return {'T':-F}

	def heatConvection(self,b):
		F = b.mdot*b.m['Cp'](b.state)*(self.R.state['T']-self.L.state['T'])
		if(b == self.R): return {'T':F}
		else: return {'T':-F}

	def difference(self,b):

		if(b == self.L): 
			return dict((s,(self.R.state[s]-self.L.state[s])/self.G['d']) for s in b.state)
		else: return dict((s,(self.L.state[s]-self.R.state[s])/self.G['d']) for s in b.state)


if __name__ == "__main__":
	import doctest
	doctest.testmod()

