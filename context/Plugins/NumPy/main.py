from numpy import *

matrixSize = %(value)d

A = matrix(random.rand(matrixSize,matrixSize))
B = A.I
C = A*B
d = B.sum()

print "I am %(name)s with an id = %(id)d of a total of %(sweepSize)d." 
print str(matrixSize)+";"+str(d)

