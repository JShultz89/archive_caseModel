import materials 
import numpy as np
from math import pi,log 
class Flux(object):
	"""
	Flux object. Each flux is effectively a boundary condition

	Each flux computes the heat transfer rate between two blocks
	returns a Qdot

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
				self.m.append(materials.createMaterial(G['m'][i]))
	"""
	Flux function

	called by a block
	"""

	def cond(self,b):
		# temperature doesnt matter in the layers, as the k are constant
		Res = 1/(self.A[0]*self.h(self.L)) + \
					np.dot([1/m.k() for m in self.m],[1/A for A in self.A[1:-1]]) + \
					1/(self.A[-1]*self.h(self.R))
		F = (self.R.T-self.L.T)/Res
		if(b == self.R): return F
		else: return -F
	def conv(self,b):
		F = b.mdot*b.m.Cp(b.T)*(self.R.T-self.L.T)
		if(b == self.R): return F
		else: return -F

	
	"""
	returns the convection heat transfer coefficient at a specific temperature

	"""
	def h(self,b):
		
		m = b.m
		h = m.k(b.T)/self.G['cL']

		if(m.name == 'water' and self.G['type'] == 'cyl'):
			# Nu_D for Reynold numbers < 2300 (laminar) 
			# and constant wall temperature. 
			# Could use Nu_D = 4.36 for constant heat transfer.
			h *= 3.66
		elif(m.name == 'air' and self.G['type'] == 'cyl'):
			Re = b.mdot/m.rho(b.T)*self.G['cL']/m.mu(b.T)	
			h *= 0.037*Re**(4.0/5.0)*m.Pr(b.T)**(1.0/3.0)
		elif(m.name == 'air' and self.G['type'] == 'plateLayer'):
			Re = b.mdot/m.rho(b.T)*self.G['cL']/m.mu(b.T)
			h *= 0.0296*Re**(4.0/5.0)*m.Pr(b.T)**(1.0/3.0)
		elif(m.name == 'glass'):
			pass
	
		return h		