from common import *

def simulate(HMM,desc='Truth & Obs'):
  """Generate synthetic truth and observations."""
  f,h,chrono,X0 = HMM.f, HMM.h, HMM.t, HMM.X0

  # Init
  xx    = zeros((chrono.K+1,f.m))
  xx[0] = X0.sample(1)
  yy    = zeros((chrono.KObs+1,h.m))

  # Loop
  for k,kObs,t,dt in progbar(chrono.forecast_range,desc):
    xx[k] = f(xx[k-1],t-dt,dt) + sqrt(dt)*f.noise.sample(1)
    if kObs is not None:
      yy[kObs] = h(xx[k],t) + h.noise.sample(1)

  return xx,yy



def simulate_or_load(script,HMM, sd, more): 
  t = HMM.t

  path = save_dir(rel_path(script)+'/sims/',pre=os.environ.get('SIM_STORAGE',''))

  path += 'HMM={:s} dt={:.3g} T={:.3g} dkObs={:d} {:s} h={:s} sd={:d}'.format(
      os.path.splitext(os.path.basename(HMM.name))[0],
      t.dt, t.T, t.dkObs,
      more,
      socket.gethostname(), sd)

  try:
    msg   = 'loaded from'
    data  = np.load(path+'.npz')
    xx,yy = data['xx'], data['yy']
  except FileNotFoundError:
    msg   = 'saved to'
    xx,yy = simulate(HMM)
    np.savez(path,xx=xx,yy=yy)
  print('Truth and obs',msg,'\n',path)
  return xx,yy
