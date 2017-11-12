from mpi4py import MPI
import numpy

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()
stat = MPI.Status()


COLS = 6
ROWS = 16
if size > ROWS:
	print("Not enough ROWS")
	exit()
subROWS=ROWS//size+2

# Set up initial grid on rank 0
Grid=None
if rank == 0:
#	M=numpy.array(range(COLS*(ROWS+2))).reshape((ROWS+2, COLS)).astype('float')
#	M=numpy.empty((ROWS+2, COLS)).astype('float')
	Grid=numpy.zeros((ROWS+2, COLS))
	Grid[0,:] = 1.
	Grid[:,0] = 1.
	initGrid = Grid

#distribute initial grid to other ranks
Grid=comm.bcast(Grid,root=0)

for i in xrange(100):
	#parse out subgrids for each rank and sweep thru
	subGrid = Grid[(ROWS/size)*rank:(ROWS/size)*rank+subROWS,:]
	for subROW in xrange(1,subROWS-1):
		for elem in xrange(1,COLS-1):
			subGrid[subROW,elem] = (subGrid[subROW,elem-1]
						+subGrid[subROW,elem+1]
						+subGrid[subROW-1,elem]
						+subGrid[subROW+1,elem])/4.
	Grid[2*rank:2*rank+subROWS,:]=subGrid 
	#exhange edges for next interation
	if rank == 0:
		comm.send(Grid[ROWS*(rank+1)/size,:],dest=rank+1)
		Grid[ROWS*(rank+1)/size+1,:]=comm.recv(source=rank+1)
	elif rank == size-1:
		comm.send(Grid[ROWS*rank/size+1,:],dest=rank-1)
		Grid[ROWS*(rank)/size,:]=comm.recv(source=rank-1)
	else: 
		comm.send(Grid[ROWS*rank/size+1,:],dest=rank-1)
		comm.send(Grid[ROWS*(rank+1)/size,:],dest=rank+1)
		Grid[ROWS*(rank)/size,:]=comm.recv(source=rank-1)
		Grid[ROWS*(rank+1)/size+1,:]=comm.recv(source=rank+1)


subGrid = Grid[(ROWS/size)*rank+1:(ROWS/size)*rank+subROWS-1,:]
newGrid=comm.gather(subGrid,root=0)
if rank == 0:
	result= numpy.vstack(newGrid)
	print numpy.vstack(initGrid)
	print result
