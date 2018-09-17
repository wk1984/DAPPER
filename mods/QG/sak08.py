# Reproduce results from Sakov and Oke "DEnKF" paper from 2008.

from common import *

from mods.QG.core import step, dt, shape, order, sample_filename
from mods.QG.liveplotting import liveplotter
from tools.localization import partial_direct_obs_nd_loc_setup as loc_setup

############################
# Time series, model, initial condition
############################

# As specified in core.py: dt = 4*1.25 = 5.0.
# Decreasing BurnIn below 250 will increase the average rmse!
# Sakov also used 10 repetitions.
t = Chronology(dt=dt,dkObs=1,T=1500,BurnIn=250)
# In my opinion the burn in should be 400.

# Considering that I have 8GB mem on the Mac, and the estimate:
# ≈ (8 bytes/float)*(129² float/stat)*(7 stat/k) * K,
# it should be possible to run experiments of length (K) < 8000.

f = {
    'm'    : np.prod(shape),
    'model': step,
    'noise': 0,
    }

X0 = RV(m=f['m'],file=sample_filename)


############################
# Observation settings
############################

# This will look like satelite tracks when plotted in 2D
p  = 300
jj = equi_spaced_integers(f['m'],p)
jj = jj-jj[0]

# Want: random_offset(t1)==random_offset(t2) if t1==t2.
# Solutions: (1) use caching (ensure maxsize=inf) or (2) stream seeding.
# Either way, use a local random stream to avoid interfering with global stream
# (and e.g. ensure equal outcomes for 1st and 2nd run of the python session).
rstream = np.random.RandomState()
max_offset = jj[1]-jj[0]
def random_offset(t):
  rstream.seed(int(t/dt*100))
  u = rstream.rand()
  return int(floor(max_offset * u))

def obs_inds(t):
  return jj + random_offset(t)

@ens_compatible
def hmod(E,t):
  return E[obs_inds(t)]

# Localization.
batch_shape = [3, 3] # width (in grid points) of each state batch.
# Increasing the width
#  => quicker analysis (but less relative speed-up by parallelization, depending on NPROC)
#  => worse (increased) rmse (but width 4 is only slightly worse than 1);
#     if inflation is applied locally, then rmse might actually improve.
localizer = loc_setup(shape[::-1], batch_shape[::-1], obs_inds, periodic=False)

h = {
    'm'    : p,
    'model': hmod,
    'noise': GaussRV(C=4*eye(p)),
    'localizer': localizer,
    }

# Moving localization mask for smoothers:
h['loc_shift'] = lambda ii, dt: ii # no movement (suboptimal, but easy)

# Jacobian left unspecified coz it's (usually) employed by methods that
# compute full cov, which in this case is too big.


############################
# Other
############################
LP = functools.partial(liveplotter,obs_inds=obs_inds)

setup = TwinSetup(f,h,t,X0,LP=LP)
setup.name = os.path.relpath(__file__,'mods/')



####################
# Suggested tuning
####################
# Reproducing Fig 7 from Sakov and Oke "DEnKF" paper from 2008.

# Notes:
# - As may be inferred from Fig 3 of Counillon et al 2009 ("...hybrid EnKF-OI...")
#   (even though setup is slightly different): Must have N >= 25.
# - Our experiments differ from Sakov's in the following minor details:
#    - We have not had the need to increase the dissipation parameter for the EnKF.
#    - We use a batch width (unsure what Sakov uses)

#from mods.QG.sak08 import setup                                # Expected RMSE_a:
# N = 25
# cfgs += LETKF(mp=True, N=N,infl=1.04       ,loc_rad=10)       # 0.64
# cfgs += LETKF(mp=True, N=N,infl='-N',xN=2.0,loc_rad=10)       # 0.66
# cfgs += SL_EAKF(       N=N,infl=1.04       ,loc_rad=10)       # 0.62
# cfgs += SL_EAKF(       N=N,infl=1.03       ,loc_rad=10)       # 0.58
#
# Iterative:
# Yet to try: '-N' inflation, larger N, different loc_rad, and
# smaller Lag (testing lag>3 was worse [with this loc_shift])
# cfgs += iLEnKS('Sqrt',N=25,infl=1.03,loc_rad=12,iMax=3,Lag=2) # 0.59
#
# N = 45
# cfgs += LETKF(mp=True, N=N,infl=1.02       ,loc_rad=10)       # 0.52
# cfgs += LETKF(mp=True, N=N,infl='-N',xN=1.5,loc_rad=10)       # 0.51


