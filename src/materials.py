import numpy as np
""" 
a factory for materials

s is a string, depicting the material name
returns the material itself
"""
def createMaterial(s):
	if(s == 'water'): return Liquid(s)
	elif(s == 'air'): return Gas(s)
	else: return Solid(s)

class Material(object):
	""" 
	Base Class - Material

	"""
	def __init__(self,s='none'):
		self.name = s

	def k(self,T=0):
		return np.polyval(self.kC,T)
	
	'Density in kg/m^3 '
	def rho(self,T=0):
		return np.polyval(self.rhoC,T)
	# Specific heat
	def Cp(self,T=0):
		return np.polyval(self.CpC,T)


class Solid(Material):
	""" 
	Solid Class

	"""
	def __init__(self,s):
		super(Solid,self).__init__(s)
		self.setkC(s)
		# Temporary Values, never called
		self.rhoC = 0
		self.CpC = 0
	def setkC(self,s):
		if(s == 'silicon tubing'): self.kC = [0.145]
		elif(s == 'silicon insulation'): self.kC = [0.037]
		elif(s == 'argon'): self.kC = [0.016]
		elif(s == 'glass'): self.kC = [0.037]
		
class Gas(Material):
	""" 
	Gas Class 


	"""
	def __init__(self,s):
		super(Gas,self).__init__()
		self.name = s
		# gas general
		if(self.name == 'air'):
			self.rhoC = [1.75e-05,-0.00483,1.293]
			self.CpC = [1.005]
			self.kC = [7e-05,0.0243]

			# gas specific
			self.PrC = [-4.705e-19,-0.0001,0.715]
			self.muC = [ 7.5e-11,8.88e-08, 1.33e-05]

	# Prandtl
	def Pr(self,T=0):
		return np.polyval(self.PrC,T)

	def mu(self,T=0):
		return np.polyval(self.muC,T)

class Liquid(Material):
	""" 
	Liquid Class 


	"""
	def __init__(self,name):
		super(Liquid,self).__init__()
		self.name = name
		if(self.name == 'water'):
			self.rhoC = [-0.003416,-0.09298,1001]
			self.CpC = [-4.178e-11,1.384e-08,-1.737e-06, \
				0.0001115,-0.003429,4.218]
			self.kC = [- 0.00001118, 0.002257, 0.5587]