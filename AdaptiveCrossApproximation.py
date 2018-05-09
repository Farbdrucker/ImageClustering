#!/usr/bin/python
import numpy as np
from scipy import linalg, dot, sparse
from scipy.sparse.linalg import eigsh

'''
Adaptive Cross Approximation for Images
calculates a rank k approximation of the Graph Laplace
Operator and returns the k eigenvectors as well as
eigenvalues
-> for spectral clustering

c.f
ADAPTIVE CROSS APPROXIMATION FOR ILL-POSED PROBLEMS
T. MACH , L. REICHEL , M. VAN BAREL , AND R. VANDEBRIL

code by Lukas Sanner, 2018
'''
class ACA(object):
    '''
    Initiate parameters
    '''
    def __init__(self, image = None, maxRank = 40,
                    k = 4, tol = 1e-6, sigma = 0.2,
                    seed = None, addDist = False):
        if image is None:
            raise SystemExit('invalid input for ACA')

        self.image = image / float(np.amax(image))
        self.maxRank = maxRank
        self.k = k


        self.__tol = tol
        self.__sigma2 = sigma**2
        self.__seed = seed
        self.__addDist = addDist
        self.width = self.image.shape[0]
        self.height = self.image.shape[1]
        self.m = self.width * self.height

        if len(self.image.shape)>2:
            self.channels = self.image.shape[2]
        else:
            self.channels = 1

    # public
    '''
    public function wich returns the eigenpairs of the approximated
    Grpah Laplacian using the adaptive cross approximation (ACA)
    '''
    def GetEig(self):
        return self.__QR(self.__ACA())

    # private
    '''
    Returns the eigenvalue decomposition of the right side of
    the symmetric Graph Laplacian D^{-1/2} W D^{-1/2} by a QR
    factorization
    '''
    def __QR(self, W):
        W = np.mat(W)
        n = W.shape[1]
        ones = np.mat(np.ones(n))
        d12 = 1./ np.sqrt( W.T * (W* ones.T))
        d12 = np.squeeze(np.asarray(d12))
        d12diag = sparse.diags(d12,
                                offsets = 0,
                                shape = (self.m, self.m))

        A = d12diag * W.T

        Q,R = linalg.qr(A, overwrite_a = True, mode = 'economic')
        print(A.shape, Q.shape, R.shape)
        if W.shape[0]< self.k:
            self.k = W.shape[0]
        eval, evec = eigsh(dot(R,R.T),k = self.k)
        eval = sparse.diags(eval,0)
        evec = np.mat(evec).T * Q.T
        eval = np.eye(self.k) - eval
        return eval, evec

    '''
    Adaptive Cross Approximation, builds a rank k approximation of the matrix
    W = w * w^T
    '''
    def __ACA(self):
        W = np.zeros((self.maxRank, self.m))
        U = np.reshape(self.image, (self.m, self.channels))
        R = np.ones(self.m)

        # start aca with arbitary index
        if self.__seed is not None:
            np.random.randint(self.__seed)
        ind = np.random.randint(self.m)

        for nu in range(self.maxRank):
            W[nu,:] = self.__SimFunction(U, ind)

            # substract rank one approx
            for mu in range(nu-1):
                W[nu,:] -= W[mu,ind] * W[mu,:]

            ind = np.ndarray.argmax(np.abs(W[nu,:]))
            delta = W[nu,ind]

            print('rank {0} \tindex {1} \tdelta {2:.4f}'.format(nu,ind,delta))
            if self.__Convergence(R,delta) == False:
                W[nu,:] *= 1./np.sqrt(delta)
                R -= W[nu,:]**2
                ind = np.argmax(R)
            else:
                print('Rank {} approximation'.format(nu-1))
                return W[:nu-1,:]
        return W[:nu,:]

    '''
    Check for convergence, therefor look at R and delta
    since we devide throught delta it should always be > 0
    '''
    def __Convergence(self, R, delta):
        if np.amax(R) < self.__tol or delta < self.__tol:
            print('adaptive cross approximation converged')
            print('max(R) = {} \tdelta = {}'.format(np.amax(R),delta))
            return True
        else:
            return False

    '''
    Similarity function for the weights of the Graph Laplace Operator
    optional: add a penalty factor for objects with a larger distance
    '''
    def __SimFunction(self, U, ind):
        D = np.zeros(self.m)

        for i in range(self.m):
            D[i] = np.linalg.norm(U[ind] - U[i])**2

            # if add distance is active, add a penalty factor depending of
            # the pixels distances to the exponent
            if self.__addDist == True:
                r = abs(ind - i)
                mod = np.mod(self.m, r)
                D[i] += 0.1* (r**2 - 2*mod + (self.m +1) * mod) / self.m**2

        return np.exp(-D/self.__sigma2)
