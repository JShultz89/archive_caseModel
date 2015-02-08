"""
Solve u_xx + u_yy = f(x,y) on a uniform grid
and v_xx + v_yy = f(x,y) on a uniform grid

with known solution

u = exp(xy) 	 				f['u'] = (x^2+y^2)*exp(xy)
v = exp((x^2+y^2))  f['v'] = (4*(x^2+y^2+1))*exp((x^2+y^2)) 

python poisson2D n
for the number of cells in each dimension

"""
import math as math
import sys
import src.blocks as b
import src.flux as f
import src.problem as p
import src.source as s

def poisson2D(N):
	n = N+2 # add two for the boundaries
	""" 
	lets define a uniform square mesh on [-1, 1] x [1, 1]
	and create boundary blocks as we go,
	initializing based on the exact solution, and naming the block by its coordinates
	"""
	d = 2./float(n-2) # spacing, delta X
	B = [b.Block('('+str(i*d-d/2-1)+','+str(j*d-d/2-1)+')',None,{'u':math.exp((i*d-d/2-1)*(j*d-d/2-1)),
		'v':math.exp((i*d-d/2-1)**2+(j*d-d/2-1)**2)}) for i in range(0,n) for j in range(0,n)]

	# interior sources
	# use the name to get the source values
	for block in B:
		(x,y) = eval(block.name)
		block.addSource(s.Source('const',u = -(x*x+y*y)*math.exp(x*y),v = -4.0*(x*x+y*y+1.0)*math.exp(x*x+y*y)))
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
			B[i*n+j].state['u'] = 0.
			B[i*n+j].state['v'] = 0.

			intB.append(B[i*n+j])
	
	# solve the problem on the interior blocks
	P = p.Problem(intB)
	P.solve()
	Eu = math.sqrt(sum([(math.exp(eval(block.name)[0]*eval(block.name)[1])-block.state['u'])**2 for block in intB])/(n-2)/(n-2))
	Ev = math.sqrt(sum([(math.exp(eval(block.name)[0]**2+eval(block.name)[1]**2)-block.state['v'])**2 for block in intB])/(n-2)/(n-2))
	return (Eu,Ev)

if __name__ == "__main__":
	n = int(sys.argv[1])
	# print poisson2D(2)
	Error = [poisson2D(n),poisson2D(n*2)]
	print Error
	Rate = [(math.log(Error[1][0])-math.log(Error[0][0]))/(math.log(2./(2*n))-math.log(2./(n))),
	(math.log(Error[1][1])-math.log(Error[0][1]))/(math.log(2./(2*n))-math.log(2./(n)))]
	print Rate