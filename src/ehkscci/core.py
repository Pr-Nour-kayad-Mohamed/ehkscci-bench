import numpy as np
from scipy.spatial.distance import cdist
from scipy.sparse.csgraph import connected_components, shortest_path
from scipy.optimize import linprog


def wasserstein(a, b, cost):
    a, b, cost = np.asarray(a, float), np.asarray(b, float), np.asarray(cost, float)
    if a.ndim != 1 or b.ndim != 1 or cost.shape != (len(a), len(b)):
        raise ValueError("Invalid transport dimensions")
    if not np.isfinite(cost).all() or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("Nonfinite transport inputs")
    if np.any(a < 0) or np.any(b < 0) or not np.isclose(a.sum(), 1) or not np.isclose(b.sum(), 1):
        raise ValueError("Probability marginals required")
    na, nb = cost.shape
    eq = np.vstack([np.kron(np.eye(na), np.ones((1, nb))),
                    np.kron(np.ones((1, na)), np.eye(nb))])
    opt = linprog(cost.ravel(), A_eq=eq, b_eq=np.r_[a, b], bounds=(0, None), method="highs")
    if not opt.success:
        raise RuntimeError(opt.message)
    return float(opt.fun)


def features(z, tau, k=4, idleness=.5, spectral_time=1., signal=None):
    z = np.asarray(z, float)
    if z.ndim != 2 or not np.isfinite(z).all() or z.shape[1] == 0:
        raise ValueError("Finite n by d coordinates required")
    n = len(z)
    if not isinstance(k, (int, np.integer)) or not 1 <= k < n:
        raise ValueError("Require integer 1 <= k < n")
    if not np.isfinite(tau) or tau <= 0 or not 0 <= idleness < 1:
        raise ValueError("Invalid tau or idleness")
    if not np.isfinite(spectral_time) or spectral_time <= 0:
        raise ValueError("Positive spectral_time required")
    f = z.copy() if signal is None else np.asarray(signal, float)
    if f.ndim == 1: f = f[:, None]
    if f.ndim != 2 or f.shape[0] != n or not np.isfinite(f).all():
        raise ValueError("Invalid signal")
    dist = cdist(z, z)
    if np.min(dist[np.triu_indices(n, 1)]) < 1e-12:
        raise ValueError("Coincident nodes require preprocessing")
    neighbours = np.argsort(dist, axis=1)[:, 1:k+1]
    mask = np.zeros((n, n), bool)
    mask[np.arange(n)[:, None], neighbours] = True
    mask = mask | mask.T
    expo = dist[mask]**2 / (2*tau*tau)
    if not np.isfinite(expo).all() or expo.max() > 700:
        raise ValueError("Affinity underflow risk")
    w = np.zeros((n, n)); w[mask] = np.exp(-expo)
    deg = w.sum(1)
    lap = np.eye(n) - w / np.sqrt(deg[:, None]*deg[None, :])
    lam, u = np.linalg.eigh(lap); lam = np.clip(lam, 0, 2)
    nc = int(connected_components(mask.astype(int), directed=False)[0])
    lengths = np.where(mask, dist, np.inf); np.fill_diagonal(lengths, 0)
    metric = shortest_path(lengths, directed=False)
    mu = (1-idleness)*w/deg[:, None]
    mu[np.arange(n), np.arange(n)] += idleness
    curvature = []
    for i, j in zip(*np.where(np.triu(mask, 1))):
        a = np.flatnonzero(mu[i] > 0); b = np.flatnonzero(mu[j] > 0)
        val = wasserstein(mu[i, a], mu[j, b], metric[np.ix_(a, b)])
        curvature.append(1 - val/metric[i, j])
    residual = f-u[:, :nc]@(u[:, :nc].T@f)
    energy = np.sum(residual**2)
    hf = float(np.sum((-np.expm1(-spectral_time*lam))[:, None]*(u.T@residual)**2)/energy) if energy > 1e-12 else float("nan")
    return dict(q=np.quantile(curvature, np.linspace(.1, .9, 9)),
                gap=float(lam[1]) if nc == 1 else 0., hf=hf,
                components=nc, edges=int(mask.sum()//2))


def reference(items):
    items = list(items)
    if not items: raise ValueError("Empty nominal reference")
    return {key: np.median(np.array([m[key] for m in items]), axis=0) for key in ("q", "gap", "hf")}


def score(observed, nominal, scales=(.1, .05, .1), weights=(1/3, 1/3, 1/3)):
    s, w = np.asarray(scales, float), np.asarray(weights, float)
    if s.shape != (3,) or w.shape != (3,) or not np.isfinite(s).all() or not np.isfinite(w).all() or np.any(s <= 0) or np.any(w < 0) or not np.isclose(w.sum(), 1):
        raise ValueError("Invalid scales or weights")
    if not np.isfinite(observed["hf"]) or not np.isfinite(nominal["hf"]):
        raise ValueError("Stationary signal: HF undefined")
    c = np.array([np.mean(((observed["q"]-nominal["q"])/s[0])**2),
                  (max(0, nominal["gap"]-observed["gap"])/s[1])**2,
                  (max(0, observed["hf"]-nominal["hf"])/s[2])**2])
    return dict(I_curvature=float(c[0]), I_gap=float(c[1]), I_hf=float(c[2]), total=float(w@c))
