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
		A list temperature (.T)
		A list of sources (.S)
	The equation for the block is
	Sum(BCs) + Sum(Sources) = 0

	Each boundary condition connects a block
	to another block (or analytic condition)
	"""

	def __init__(self,s,m):
		self.F = []
		self.T = 0
		self.S = []
		self.name = s
		self.m = materials.createMaterial(m)
		self.mdot = []


	def addFlux(self,F):
		self.F.append(F)

	def addSource(self,S):
		self.S.append(S)
	"""
		iterates over sources and boundary conditions 
		returns the sum as a single float variable

	"""
	def r(self):
		return sum([f.F(self) for f in self.F]) - sum([S(self.T) for S in self.S])
		