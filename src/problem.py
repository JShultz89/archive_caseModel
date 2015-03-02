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

	def update(self,solution,t = 0):
		for ix, (i,k) in enumerate(self.mapping):
			self.b[i].state[k] = solution[ix]
		# update time	
		for b in self.b:	
			b.t = t
		# BC states are updated using a single source function to drive them	
		for bc in self.bc:
			bc.t = t
			for s in bc.state:
				bc.state[s] = bc.S[0].S(bc)[s]
				# print bc.name, bc.state['T'], t

	"""
	r:					Global residual function r(solution) 

	input(s):    (solution) global array of floats corresponding to mapping
	output(s):	R(solution) global array of floats corresponding to residual

	updates solution first, then computes
	should be passed into another function
	"""
	def r(self,solution,t = 0):
		self.update(solution,t)
		return [self.b[i].R()[v]/self.b[i].T(self.b[i].state)[v] for i,v in self.mapping]

	"""
	solve:			wrapper for chosen (non)linear solver

	input(s):   None
	output(s):	None

	unwraps blocks, passes into solver, finishes by updating blocks one last time
	""",
	def solve(self,t = 0):
		solution = [None]*len(self.mapping)
		for ix, (i,k) in enumerate(self.mapping):
			solution[ix] = self.b[i].state[k]
		solution = fsolve(self.r, solution,args=t)
		self.update(solution,t)
	"""
	solveUnst:	solve the transient problem

	input(s):   (ti) initial time
							(tf) final time
							(n)  number of timesteps
	output(s):	None

	unwraps blocks, passes into solver, finishes by updating blocks one last time
	"""
	def solveUnst(self,t):
		solnPoints = {}
		solution = [None]*len(self.mapping)
		# This has the unsteady part
		# Solver, just live and let live	
		for ix, (i,k) in enumerate(self.mapping):
			solution[ix] = self.b[i].state[k]

		soln = odeint(self.r, solution, t)
		# final update
		self.update(soln[-1,:],t[-1])
		# Lets output all the steps
		allSoln = dict([(b.name + '_'+s,[]) for b in self.b for s in b.state])
		for j in range(0,len(t)):
			for ix, (i,k) in enumerate(self.mapping):
				allSoln[self.b[i].name+'_'+k].append(soln[j,ix])
		allSoln['t'] = t
		return allSoln
	"""
	printSolution:		Outputs solution to screen
	"""
	def printSolution(self):
		for b in self.b:
			b.printMe()

if __name__ == "__main__":
    import doctest
    doctest.testmod()

