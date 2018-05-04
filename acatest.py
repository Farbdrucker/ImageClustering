import numpy as np
from AdaptiveCrossApproximation import ACA
from ConvSplitting import ConvSplittingFunc
if __name__ == '__main__':
    n = 100
    m = 64
    nm = n*m
    seed = 100
    np.random.seed(seed)
    Im = np.random.random((n,m))
    print Im
    D,V =  ACA(image = Im, seed = seed, maxRank = 5, k = 3).GetEig()
    Mask = np.zeros((nm,1))
    Mask[30:40] = 1
    u0 = ConvSplittingFunc(u0=Mask,lamb = D, phi = V)
    print u0
