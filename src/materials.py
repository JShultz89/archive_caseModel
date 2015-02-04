import numpy as np
""" 
This file contains a list of material definitions

Each definition contains a name, a type (not used yet),
and a list of property functions, which are inputs of the variable
'var' with indices defined numerically, depending on the problem type

"""

water = \
{
	'name':'water',
	'type':'liquid',
	'rho':lambda var : np.polyval([-0.003416,-0.09298,1001],var['T']),
	'Cp': lambda var : np.polyval([-4.178e-11,1.384e-08,-1.737e-06, 0.0001115,-0.003429,4.218],var['T']),
	'k':  lambda var : np.polyval([- 0.00001118, 0.002257, 0.5587],var['T'])
}
air = \
{
	'name':'air',
	'type':'gas',
	'rho':lambda var : np.polyval([1.75e-05,-0.00483,1.293],var['T']),
	'Cp': lambda var : np.polyval([1.005],var['T']),
	'k':  lambda var : np.polyval([7e-05,0.0243],var['T']),
	'Pr': lambda var : np.polyval([-4.705e-19,-0.0001,0.715],var['T']),
	'mu': lambda var : np.polyval([7.5e-11,8.88e-08, 1.33e-05],var['T'])
}
silicon_tubing = \
{
	'name':'silicon tubing',
	'type':'solid',
	'k':  lambda var = 0: 0.145
}
silicon_insulation = \
{
	'name':'silicon insulation',
	'type':'solid',
	'k':  lambda var = 0: 0.037
}
glass = \
{
	'name':'glass',
	'type':'solid',
	'k':  lambda var = 0: 1.05
}
argon = \
{
	'name':'argon',
	'type':'gas',
	'k':  lambda var = 0: 0.016
}

# class Material(object):
# 	""" 
# 	Base Class - Material

# 	"""
# 	def __init__(self,s='none'):
# 		self.name = s
# 	""" Thermal Conductivity in (W/m K) """
# 	def k(self,T=0):
# 		return np.polyval(self.kC,T)
	
# 	"""Density in kg/m^3 """
# 	def rho(self,T=0):
# 		return np.polyval(self.rhoC,T)

# 	"""Specific heat in kJ/(kg K) """
# 	def Cp(self,T=0):
# 		return np.polyval(self.CpC,T)


# class Solid(Material):
# 	""" 
# 	Solid Class

# 	"""
# 	def __init__(self,s):
# 		super(Solid,self).__init__(s)
# 		self.setkC(s)
# 		self.rhoC = 0
# 		self.CpC = 0

# 	""" list of solids """	
# 	def setkC(self,s):
# 		if(s == 'silicon tubing'): self.kC = [0.145]
# 		elif(s == 'silicon insulation'): self.kC = [0.037]
# 		elif(s == 'glass'): self.kC = [1.05]
		
# class Gas(Material):
# 	""" 
# 	Gas Class 


# 	"""
# 	def __init__(self,s):
# 		super(Gas,self).__init__()
# 		self.name = s
# 		""" list of gases """
# 		if(s == 'air'):
# 			self.rhoC = [1.75e-05,-0.00483,1.293]
# 			self.CpC = [1.005]
# 			self.kC = [7e-05,0.0243]

# 			# gas specific
# 			self.PrC = [-4.705e-19,-0.0001,0.715]
# 			self.muC = [ 7.5e-11,8.88e-08, 1.33e-05]
# 		elif(s == 'argon'): 
# 			# other properties don't matter for now	
# 			self.kC = [0.016]

# 	# Prandtl
# 	def Pr(self,T=0):
# 		return np.polyval(self.PrC,T)

# 	def mu(self,T=0):
# 		return np.polyval(self.muC,T)

# class Liquid(Material):
# 	""" 
# 	Liquid Class 


# 	"""
# 	def __init__(self,s):
# 		super(Liquid,self).__init__()
# 		self.name = s

# 		""" list of liquids """
# 		if(s == 'water'):
# 			self.rhoC = [-0.003416,-0.09298,1001]
# 			self.CpC = [-4.178e-11,1.384e-08,-1.737e-06, \
# 				0.0001115,-0.003429,4.218]
# 			self.kC = 