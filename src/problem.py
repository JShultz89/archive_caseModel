"""
problem.py contains the Problem Class

Each Problem has:
	(.b) the blocks to solve for in the problem
	(.mapping) the mapping between the local and global systems


------------------------------------
function tests are run by doctest
python problem.py
------------------------------------
"""
from scipy.optimize import fsolve
import csv

class Problem(object):
	""" 
	Problem Class

	__init__:		Problem Constructor

	input(s):   (blocks) relevant blocks
	output(s):	None
	"""
	def __init__(self,blocks):
		self.b = blocks
		self.mapping = [(i, k) for i, b in enumerate(blocks) for k in b.state.keys()]

	"""
	update:			Updates the blocks by unwrapping the new solution

	input(s):   (solution) global array of floats corresponding to mapping
	output(s):	None
	"""

	def update(self,solution):
		for ix, (i,k) in enumerate(self.mapping):
			self.b[i].state[k] = solution[ix]

	"""
	r:					Global residual function r(solution) 

	input(s):   (solution) global array of floats corresponding to mapping
	output(s):	R(solution) global array of floats corresponding to residual

	updates solution first, then computes
	should be passed into another function
	"""
	def r(self,solution):
		self.update(solution)
		return [self.b[i].R()[v] for i,v in self.mapping]

	"""
	solve:			wrapper for chosen (non)linear solver

	input(s):   None
	output(s):	None

	unwraps blocks, passes into solver, finishes by updating blocks one last time
	"""
	def solve(self):
		solution = [None]*len(self.mapping)
		for ix, (i,k) in enumerate(self.mapping):
			solution[ix] = self.b[i].state[k]
		solution = fsolve(self.r, solution)
		self.update(solution)

	"""
	printSolution:		Outputs solution to screen
	"""
	def printSolution(self):
		for b in self.b:
		    print b.name, [s + '=' + str(b.state[s]) for s in b.state]

        
        def writeSolution(self):
           	csvfilename = 'output_nov25.csv'
           	csvfile = open(csvfilename, 'wb')
           	python_data = csv.writer(csvfile)
           	for b in self.b:
           	    python_data.writerow([b.name, [s + '=' + str(b.state[s]) for s in b.state]])

if __name__ == "__main__":
    import doctest
    doctest.testmod()

