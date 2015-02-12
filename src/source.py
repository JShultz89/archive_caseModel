"""
source.py contains the Source class

All sources are S = source(block) 

------------------------------------
function tests are run by doctest
python blocks.py
------------------------------------
>>> b = blocks.Block('test','water')
>>> b.state['T'] = 20.0
>>> Sa = Source('const',**{'T':0.5})
>>> Sa.S(b)['T']
0.5
>>> b.state['T'] = 10.0
>>> Sa.S(b)['T']
0.5

"""
class Source(object):
	""" 
	Source Class

	input(s):   (s) string corresponding to function name
							(kwargs) optional dictionary with arguments for the source functions
	output(s):	None
	"""
	def __init__(self,s,**kwargs):
		self.S = eval('self.'+s)
		self.kwargs = kwargs
	"""
	input(s):   (b) Block
	output(s):	dict corresponding to b.state variables

	This is the constant source
	"""
	def const(self,b):
		return dict([(state,self.kwargs[state]) for state in b.state])

if __name__ == "__main__":
	import doctest
	import blocks
	doctest.testmod()

