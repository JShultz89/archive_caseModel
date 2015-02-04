import materials 
from math import log, pi
import numpy as np

# Interface
class Block(object):
	""" 
	Block Class

	Every component is a Block
	Each Block has:
		A list of materials (.m)
		A list of fluxes (.F)
		A numpy array of variables (.var)
		A list of sources (.S)
	The equation for the block is
	Sum(Fluxes) + Sum(Sources) = 0

	Each boundary condition connects a block
	to another block (or analytic condition)
	"""

	def __init__(self,s,m):
		self.F = []
		self.S = []		
		self.var = {}
		self.name = s
		self.m = materials.__dict__[m]

	def addFlux(self,F):
		self.F.append(F)

	def addSource(self,S):
		self.S.append(S)
	"""
		iterates over sources and boundary conditions 
		returns the sum as a single float variable

	"""
	def r(self):
		res = {}
		for v in self.var:
			res[v] = sum([f.F(self)[v] for f in self.F]) - sum([S(self)[v] for S in self.S])
		return res