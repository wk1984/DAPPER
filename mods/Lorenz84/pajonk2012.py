# Settings from
# Pajonk, Oliver, et al. 
#   "A deterministic filter for non-Gaussian Bayesian estimation—applications to dynamical system estimation with noisy measurements."
#   Physica D: Nonlinear Phenomena 241.7 (2012): 775-788.
#
# More interesting settings: mods.Lorenz84.harder

from common import *

from mods.Lorenz84.core import step, dfdx

m = 3
p = m


day = 0.05/6 * 24 # coz dt=0.05 <--> 6h in "model time scale"
t = Chronology(0.05,dkObs=1,T=200*day,BurnIn=10*day)

m = 3
f = {
    'm'    : m,
    'model': lambda x,t,dt: step(x,t,dt),
    'jacob': dfdx,
    'noise': 0
    }

X0  = GaussRV(C=0.01,m=m) # Decreased from Pajonk's C=1.

h = {
    'm'    : p,
    'model': lambda x,t: x,
    'jacob': lambda x,t: eye(p),
    'noise': GaussRV(C=0.1**2,m=p)
    }

other = {'name': os.path.relpath(__file__,'mods/')}

setup = OSSE(f,h,t,X0,**other)

####################
# Suggested tuning
####################
#cfgs.add(ExtKF,infl=2)
#cfgs.add(EnKF,'Sqrt',N=3,infl=1.01)
#cfgs.add(PartFilt, N=100, NER=0.4)
#cfgs.add(PartFilt, N=1000, NER=0.1)
