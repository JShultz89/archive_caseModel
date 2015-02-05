from scipy.optimize import fsolve

"""


"""
class Problem(object):

	def __init__(self,blocks):
		self.b = blocks
		# Store the mapping, to be used later
		self.mapping = [(i, k) for i, b in enumerate(blocks) for k in b.var.keys()]

	# update the variables in each block
	def update(self,solution):
		for ix, (i,k) in enumerate(self.mapping):
			self.b[i].var[k] = solution[ix]

	# define the residual function here as the sum over all non boundary blocks
	def r(self,solution):

		self.update(solution)
		# compute the residual
		return [self.b[i].r()[v] for i,v in self.mapping]

	# for now uses scipy.optimize's fsolve, does not compute
	def solve(self):
		return fsolve(self.r, [b.var[v] for b in self.b for v in b.var])


	# print final solution
	def printSolution(self):
		for b in self.b:
			print b.name, b.var