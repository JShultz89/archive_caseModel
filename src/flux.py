""" 
flux.py contains a list of flux functions 

This is meant to serve as a platform
for all flux functions

Each flux computes the heat transfer rate between two blocks
Each flux contains:
	The block it belongs to (.B)
	The block its connected to (.N)
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

	input(s):   (N) Neighboring block
							(f) Flux function name
							(G) Geometry (optional)
								For now, geometry is not required, 
								as some fluxes don't need it
	output(s):	None
	"""
	def __init__(self,N,f,G=None):
		self.B = None # this will be set when its added to the block
		self.N = N
		self.F = eval('self.'+f) # set up the function
		self.m = []
		
		if G is not None:
			self.G = G
			n = len(G['m'])+2 # number of layers + both sides
			for i in range(0,n-2):
				self.m.append(materials.__dict__.get(G['m'][i],0))

	"""
	The following are all flux function choices defined with

	input(s):   none
	output(s):	dict with entries for the flux for each state contributed to

	Fluxes can have blocks with different physical states
	provided the flux function passes contributions to some of the states

	For example, L.state could have 'T','rho' and R.state could have just 'T'
	as long as the flux between them only affects 'T'


	The bulk of the hard-coding and material calls are in here
	"""

	def heatCondSimple(self):
	
		# All per meter
		if(self.G['type'] == 'ext'):
			h = 1.5583718700478653
		elif(self.G['type'] == 'int'):
			h = 0.5240370865137535
		elif(self.G['type'] == 'wa'):
			h = 0.16079175187974612
		else:
			h = 0
		h /= self.G['L']
		return {'T':(self.N.state['T']-self.B.state['T'])*h}

	def heatConduction(self):

		"""
		returns the convection heat transfer coefficient at a specific temperature

		"""
		def h(b):
			
			m = self.B.m
			h = m['k'](self.B.state)/self.G['cL']
			if(m['name'] == 'water' and self.G['type'] == 'cyl'):
				# Nu_D for Reynold numbers < 2300 (laminar) 
				# and constant wall temperature. 
				# Could use Nu_D = 4.36 for constant heat transfer.
				h *= 3.66
			elif(m['name'] == 'air' and self.G['type'] == 'cyl'):
				Re = self.B.mdot/m['rho'](self.B.state)*self.G['cL']/m['mu'](self.B.state)	
				h *= 0.037*Re**(4.0/5.0)*m['Pr'](self.B.state)**(1.0/3.0)
			elif(m['name'] == 'air' and self.G['type'] == 'plateLayer'):
				Re = self.B.mdot/m['rho'](self.B.state)*self.G['cL']/m['mu'](self.B.state)
				h *= 0.0296*Re**(4.0/5.0)*m['Pr'](self.B.state)**(1.0/3.0)
			elif(m['name'] == 'glass'):
				pass
		
			return h		
		# temperature doesnt matter in the layers, as the k are constant

		Res = 1/(self.A[0]*h(self.B)) + \
					np.dot([1/m['k']() for m in self.m],[1/A for A in self.A[1:-1]]) + \
					1/(self.A[-1]*h(self.N))
		# print np.array([A for A in self.A[1:-1]])
		return {'T':(self.N.state['T']-self.B.state['T'])/Res}

	def heatConvection(self):
		return {'T':self.B.mdot*self.B.m['Cp'](self.B.state)*(self.B.state['T']-self.N.state['T'])}

	def difference(self):
		return dict((s,(self.N.state[s]-self.B.state[s])/self.G['d']) for s in self.B.state)



if __name__ == "__main__":
	import doctest
	doctest.testmod()

