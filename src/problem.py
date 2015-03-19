"""
problem.py contains the Problem Class

Each Problem has:
	(.b) the blocks to solve for in the problem
	(.bc) the blocks used as boundary blocks
	(.mapping) the mapping between the local and global systems


------------------------------------
function tests are run by doctest
python problem.py
------------------------------------
"""

"""
fsolve is used for solving steady state
ode is used for solving transient
"""
from scipy.optimize import fsolve
from scipy.integrate import odeint
import numpy as np
from collections import OrderedDict
import numdifftools as nd

class Problem(object):
	""" 
	Problem Class

	__init__:		Problem Constructor

	input(s):   (blocks) relevant blocks
							(boundaries) blocks on the boundaries
								these are needed for unsteady problems
	output(s):	None
	"""
	def __init__(self,blocks,boundaries = [],**parameters):
		self.b = blocks
		self.bc = boundaries
		self.mapping = [(i, k) for i, b in enumerate(blocks) for k in b.state.keys()]

	"""
	update:			Updates the blocks by unwrapping the new solution

	input(s):   (solution) global array of floats corresponding to mapping
	output(s):	None
	"""

	def update(self,solution):
		for ix, (i,k) in enumerate(self.mapping):
			self.b[i].state[k] = solution[ix]
		for bc in self.bc:
			for s in bc.state:
				bc.state[s] = bc.S[0].S(bc)[s]

	def updateUnst(self,t):
		# update time	
		for b in self.b + self.bc:	
			b.t = t
	def getSolutionVec(self):
		solution = [None]*len(self.mapping)
		for ix, (i,k) in enumerate(self.mapping):
			solution[ix] = self.b[i].state[k]
		return solution

	"""
	r:					Global residual function r(solution) 

	input(s):    (solution) global array of floats corresponding to mapping
	output(s):	R(solution) global array of floats corresponding to residual

	updates solution first, then computes
	should be passed into another function
	"""
	def r(self,solution):
		self.update(solution)
		return [self.b[i].R()[v] for i,v in self.mapping]
	def rVec(self,solution):

		self.update(solution.tolist())
		return np.array([self.b[i].R()[v] for i,v in self.mapping])
	def rUnst(self,solution,t):
		self.updateUnst(t)
		self.update(solution)
		return [self.b[i].R()[v]/self.b[i].T(self.b[i].state)[v] for i,v in self.mapping]

	"""
	solve:			wrapper for chosen (non)linear solver

	input(s):   None
	output(s):	None

	unwraps blocks, passes into solver, finishes by updating blocks one last time
	""",
	def solve(self,t=0):
		self.updateUnst(t)
		solution = fsolve(self.r, self.getSolutionVec())

	def jacobian(self):
		Jfun = nd.Jacobian(self.rVec)
		return Jfun(self.getSolutionVec())
	"""
	solveUnst:	solve the transient problem

	input(s):   (ti) initial time
							(tf) final time
							(n)  number of timesteps
	output(s):	None

	unwraps blocks, passes into solver, finishes by updating blocks one last time
	"""
	def solveUnst(self,t):
		solution = [None]*len(self.mapping)
		# This has the unsteady part
		# Solver, just live and let live	
		for ix, (i,k) in enumerate(self.mapping):
			solution[ix] = self.b[i].state[k]
		soln = odeint(self.rUnst, solution, t,hmax=(t[-1]-t[0])/len(t),rtol = 1e-4, atol = 1e-4)

		# final update
		self.updateUnst(t[-1])
		self.update(soln[-1,:])

		# Lets output all the steps
		allSoln = dict([(b.name + '_'+s,[]) for b in self.b for s in b.state])
		for j in range(0,len(t)):
			for ix, (i,k) in enumerate(self.mapping):
				allSoln[self.b[i].name+'_'+k].append(soln[j,ix])
		allSoln['t'] = t
		return allSoln

if __name__ == "__main__":
    import doctest
    doctest.testmod()

