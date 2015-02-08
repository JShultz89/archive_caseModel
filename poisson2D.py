"""
Solve u_xx + u_yy = f(x,y) on a uniform grid

with known solution

u = exp(xy) , f = (x^2+y^2)*exp(xy)

python poisson2D n
for the number of cells in each dimension

"""
import math as math
import sys
import src.blocks as b
import src.flux as f
import src.problem as p
import src.source as s

if __name__ == '__main__':
	n = int(sys.argv[1])+2 # add two for the boundaries
	""" 
	lets define a uniform square mesh on [0, 1] x [0, 1]
	and create boundary blocks as we go,
	initializing based on the exact solution, and naming the block by its coordinates
	"""
	d = 1/float(n-2) # spacing, delta X
	B = [b.Block('('+str(i*d-d/2)+','+str(j*d-d/2)+')',None,{'u':math.exp((i*d-d/2)*(j*d-d/2))}) for i in range(0,n) for j in range(0,n)]
	# B = [b.Block('('+str(i*d-d/2)+','+str(j*d-d/2)+')',None,{'u':0}) for i in range(0,n) for j in range(0,n)]

	# interior sources
	# use the name to get the source values
	for block in B:
		(x,y) = eval(block.name)
		block.addSource(s.Source('const',u = -(x*x+y*y)*math.exp(x*y)))
	# Flux geometry	
	G = {'type':'diff','d':d*d,'m':[]}
	intB = []
	for i in range(1,n-1):
		for j in range(1,n-1):
			# Add fluxes, no "normals" so we cheat and define them cleverly
			k = [(i-1)*n+j, i*n+j-1,(i+1)*n+j, i*n+j+1]
			B[i*n+j].addFlux(f.Flux(B[k[0]],B[i*n+j],'difference',G))
			B[i*n+j].addFlux(f.Flux(B[k[1]],B[i*n+j],'difference',G))
			B[i*n+j].addFlux(f.Flux(B[i*n+j],B[k[2]],'difference',G))
			B[i*n+j].addFlux(f.Flux(B[i*n+j],B[k[3]],'difference',G))
			intB.append(B[i*n+j])
	
	# solve the problem on the interior blocks
	P = p.Problem(intB)
	P.solve()

	finalError = math.sqrt(sum([(math.exp(eval(block.name)[0]*eval(block.name)[1])-block.state['u'])**2 for block in intB])/(n-2)/(n-2))

	print finalError
