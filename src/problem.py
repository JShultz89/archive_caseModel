from scipy.optimize import fsolve

"""


"""
class Problem(object):

	def __init__(self,blocks):
		self.b = blocks

	# update the variables in each block
	def update(self,solution):
		k = 0;
		for b in self.b:
			for v in b.var:
				b.var[v] = solution[k]
				k+=1	

	# define the residual function here as the sum over all non boundary blocks
	def r(self,solution):
		self.update(solution)
		# compute the residual
		return [b.r()[v] for b in self.b for v in b.var]

	# for now uses scipy.optimize's fsolve, does not compute
	def solve(self):
		return fsolve(self.r, [b.var[v] for b in self.b for v in b.var])


	# print final solution
	def printSolution(self):
		for b in self.b:
			print b.name, b.var