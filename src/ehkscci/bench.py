import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from .core import features, score, reference


def circle(n=16):
    a = np.linspace(0, 2*np.pi, n, endpoint=False)
    return np.c_[np.cos(a), np.sin(a)]


def tau0(z, k=4):
    return float(np.median(np.sort(cdist(z, z), axis=1)[:, k]))


def auc(pos, neg):
    p, q = np.asarray(pos)[:, None], np.asarray(neg)[None, :]
    return float(np.mean(p > q)+.5*np.mean(p == q))


def noise(n=16, repeats=12, seed=2026, factors=(.5,.7,1.,1.4,2.)):
    rng = np.random.default_rng(seed); base = circle(n); t0 = tau0(base)
    refs = {f: features(base, t0*f) for f in factors}; rows = []
    for sigma in (0., .005, .02, .05, .1):
        for rep in range(1 if sigma == 0 else repeats):
            z = base+rng.normal(0, sigma, base.shape)
            for f in factors:
                m = refs[f] if sigma == 0 else features(z, t0*f)
                rows.append(dict(sigma=sigma, repeat=rep, tau_factor=f, **score(m, refs[f])))
    return pd.DataFrame(rows)


def sweep(n=24, seed=2026, factors=(.2,.5,.7,1.,1.4,2.,5.)):
    rng = np.random.default_rng(seed); base = circle(n); t0 = tau0(base)
    benign = base+rng.normal(0, .01, base.shape)
    split = base.copy(); split[split[:,0] > 0,0] += 1.5
    rows = []
    for f in factors:
        ref = features(base, t0*f)
        for name,z in (("nominal",base),("benign",benign),("split",split)):
            rows.append(dict(scenario=name,tau_factor=f, **score(features(z,t0*f),ref)))
    return pd.DataFrame(rows)


def cv(n=16, windows=12, folds=3, seed=7, factors=(.5,.625,.78,1.,1.4,2.)):
    if not 2 <= folds <= windows: raise ValueError("Require 2 <= folds <= windows")
    rng=np.random.default_rng(seed); base=circle(n); t0=tau0(base)
    data={f:[] for f in ("nominal","shift","contaminate","collapse")}
    for _ in range(windows):
        data["nominal"].append(base+rng.normal(0,.02,base.shape))
        z=base.copy(); z[z[:,0]>0,0]+=.35
        data["shift"].append(z+rng.normal(0,.02,base.shape))
        z=base.copy(); ix=rng.choice(n,2,replace=False); z[ix]+=rng.normal(0,.35,(2,2))
        data["contaminate"].append(z+rng.normal(0,.02,base.shape))
        data["collapse"].append(.9*base+rng.normal(0,.02,base.shape))
    ids=np.empty(windows,int); ids[rng.permutation(windows)]=np.arange(windows)%folds
    rows=[]
    for f in factors:
        desc={name:[features(z,t0*f) for z in zs] for name,zs in data.items()}
        for fold in range(folds):
            train=np.flatnonzero(ids!=fold); test=np.flatnonzero(ids==fold)
            ref=reference([desc["nominal"][i] for i in train])
            neg=[score(desc["nominal"][i],ref)["total"] for i in test]
            for fam in ("shift","contaminate","collapse"):
                pos=[score(desc[fam][i],ref)["total"] for i in test]
                rows.append(dict(fold=fold,tau_factor=f,family=fam,auc=auc(pos,neg)))
    return pd.DataFrame(rows)
