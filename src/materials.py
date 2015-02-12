""" 
materials.py contains a list of material definitions

Each definition is a dictionary and has
	name 
	type (not used yet...)
	property functions 
		which are defined either as inline (lambda)
		or can be defined externally in this file
		They are a function of one or more state variables
		defined in the OrderedDict 'state'
		Any material can have any set of functions

	Eg. 'rho':lambda state : np.polyval([-0.003416,-0.09298,1001],state['T'])
	is equal to 
	rho =  state['T']*state['T']*-0.003416 + state['T']*-0.09298 + 1001
	where an optional state = 0 is used for materials that are inside fluxes,
	where their constant value ensures we don't explicitly have to know their
	temperature

------------------------------------
function tests are below as run by doctest
python materials.py
------------------------------------
>>> state = {'T': 20}
>>> water['rho'](state)
997.774

>>> glass['k']()
1.05

>>> glass['k'](state)
1.05

"""
import numpy as np
constWater = \
{
	'name':'constWater',
	'type':'liquid',
	'Cp': lambda state = 0 : 4.218
}
constAir = \
{
	'name':'constAir',
	'type':'liquid',
	'Cp': lambda state = 0 : 1.005
}
water = \
{
	'name':'water',
	'type':'liquid',
	'rho':lambda state : np.polyval([-0.003416,-0.09298,1001],state['T']),
	'Cp': lambda state : np.polyval([-4.178e-11,1.384e-08,-1.737e-06, 0.0001115,-0.003429,4.218],state['T']),
	'k':  lambda state : np.polyval([- 0.00001118, 0.002257, 0.5587],state['T'])
}
air = \
{
	'name':'air',
	'type':'gas',
	'rho':lambda state : np.polyval([1.75e-05,-0.00483,1.293],state['T']),
	'Cp': lambda state : np.polyval([1.005],state['T']),
	'k':  lambda state : np.polyval([7e-05,0.0243],state['T']),
	'Pr': lambda state : np.polyval([-4.705e-19,-0.0001,0.715],state['T']),
	'mu': lambda state : np.polyval([7.5e-11,8.88e-08, 1.33e-05],state['T'])
}
silicon_tubing = \
{
	'name':'silicon tubing',
	'type':'solid',
	'k':  lambda state = 0: 0.145
}
silicon_insulation = \
{
	'name':'silicon insulation',
	'type':'solid',
	'k':  lambda state = 0: 0.037
}
glass = \
{
	'name':'glass',
	'type':'solid',
	'k':  lambda state = 0: 1.05
}
argon = \
{
	'name':'argon',
	'type':'gas',
	'k':  lambda state = 0: 0.016
}
# function testing
if __name__ == "__main__":
	import doctest
	doctest.testmod()	