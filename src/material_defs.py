""" 
This file contains material definitions 

Each definition contains a name, a type (not used yet),
and a list of property functions, which are inputs of the variable

"""
water = \
{
	'name':'water',
	'type':'liquid',
	'rho':lambda var : np.polyval([-0.003416,-0.09298,1001],var[T]),
	'Cp': lambda var : np.polyval([-4.178e-11,1.384e-08,-1.737e-06, 0.0001115,-0.003429,4.218],var[T]),
	'k':  lambda var : np.polyval([- 0.00001118, 0.002257, 0.5587],var[T])
}
air = \
{
	'name':'air',
	'type':'gas',
	'rho':lambda var : np.polyval([1.75e-05,-0.00483,1.293],var[T]),
	'Cp': lambda var : np.polyval([1.005],var[T]),
	'k':  lambda var : np.polyval([7e-05,0.0243],var[T]),
	'Pr': lambda var : np.polyval([-4.705e-19,-0.0001,0.715],var[T]),
	'mu': lambda var : np.polyval([7.5e-11,8.88e-08, 1.33e-05],var[T])
}
siliconTubing = \
{
	'name':'silicon tubing',
	'type':'solid',
	'k':  lambda var = 0: 0.145
}
siliconInsulation = \
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
