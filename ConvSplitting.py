from numpy.linalg import norm
import numpy as np
from numpy import multiply as mul
'''
Stoll / Buenger 2016
Input:
u_0:      Image with predifend points the supervised part
lambda:   eigenvalues of the Graph Laplacian
phi:      eigenvectors of the Graph Laplacian
Output:
u:        segmented image
'''
def ConvSplittingFunc(u0, lamb, phi ,
                    omega0 = 1, eps = None ,
                    dt = 0.01, c = None,
                    maxIter = 500, tol = 1e-8):

        if eps is None:
            eps = 1./np.sqrt(u0.shape[0])
        if c is None:
            c = 3./eps + omega0

        # lambda should be a vector of the k eigenvalues
        k = lamb.shape[0]
        if len(lamb.shape)>1:
            lamb = lamb.diagonal()
            if lamb.shape[0]<lamb.shape[1]:
                lamb = lamb.T


        u0 = np.mat(u0)
        phi = np.mat(phi).T

        n = u0.shape[0]
        omega = np.mat(np.zeros((n,1)))
        for i in range(n):
            if u0[i]>0:
                omega[i] = omega0

        uzero = phi.T * u0
        a = uzero
        b = phi.T * np.power(u0,3)
        kOnes = np.mat(np.ones((k,1)))
        u = np.mat(np.zeros((n,1)))
        d = np.mat(np.zeros((k,1)))
        D = kOnes + dt *(eps * lamb + c *kOnes)
        #print phi.shape, lamb.shape, u.shape, u0.shape, omega.shape, b.shape
        for i in range(maxIter):
            print('iter {}'.format(i))
            left = (1+dt/eps +c*dt)*a
            right = dt/eps *b - dt * d
            a = mul(1./D, left - right)

            uNew = phi * a
            if i >1:
                normU = norm(uNew - u)/norm(u)
                if normU < tol:
                    return u,uzero
            u = phi * a
            b = phi.T * np.power(u,3)
            d = phi.T * mul((u -u0) , omega)


        return u,uzero
