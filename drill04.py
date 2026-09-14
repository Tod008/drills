import numpy as np
from scipy import stats
from scipy.optimize import brentq
import matplotlib.pyplot as plt

def t_stat(x, y):
    """Compute two sample t-statistic for x and y. Returns (100,) array of t-statistics."""

    n1 = x.shape[0]

    n2 = y.shape[0]

    var1 = x.var(axis=0, ddof=1)

    var2 = y.var(axis=0, ddof=1)

    s = np.sqrt(((n1-1) * var1 + (n2-1) * var2)/(n1+n2-2))

    res = (x.mean(axis=0) - y.mean(axis=0)) / (s * np.sqrt(1/n1 + 1/n2))

    return res

def permute(x, y, rng, n1=10):
    """This function shuffles the combined (20,100) array, so every column gets the same row permutation."""

    combined = np.concatenate([x, y], axis = 0)

    rng.shuffle(combined)

    shuffled_x = combined[:n1]

    shuffled_y = combined[n1:]

    return shuffled_x, shuffled_y

def benjamini_hochberg(pvals, alpha=0.05):
    """Step-up BH. pvals (n_rep, m) -> boolean reject mask, same shape. m is taken from pvals.shape[1], so BH corrects across all columns regardless of which are null."""

    sort = np.argsort(pvals, axis = 1)

    sorted_list = np.take_along_axis(pvals, sort, axis = 1)

    threshold = np.arange(1, pvals.shape[1] + 1) * (alpha / pvals.shape[1])

    max_index = np.max(np.where(sorted_list <= threshold, np.arange(pvals.shape[1]), -1), axis = 1)

    rejected = np.arange(pvals.shape[1]) <= max_index[:, None]

    res = np.zeros_like(pvals, dtype=bool)

    np.put_along_axis(res, sort, rejected, axis = 1)

    return np.squeeze(res)

def run(delta, rng, B=1000):

    results = np.zeros((B, 100))

    x = rng.standard_normal((10, 100))

    y = rng.standard_normal((10, 100))

    x[:, :10] += delta

    observed = t_stat(x, y)

    for i in range(B):

        perm_x, perm_y = permute(x, y, rng)

        ttest = t_stat(perm_x, perm_y)

        results[i, :] = ttest

    c = np.linspace(0, np.abs(observed).max(), 100)

    fdr_hat = np.zeros(len(c))
    fdp = np.zeros(len(c))

    for j, k in enumerate(c):

        R = (np.abs(observed) >= k).sum()

        V_hat = (np.abs(results) >= k).sum() / B

        fdr_hat[j] = V_hat / np.maximum(R, 1) 

        fdp[j] = (np.abs(observed[10:]) >= k).sum() / max(R, 1)

    pvals = np.zeros(100)

    # p-values pool all permuted statistics into one null reference results.size, so the 10 true effect columns contribute to the reference distribution.
    for i in range(100):

        pvals[i] = (np.abs(results) >= np.abs(observed[i])).sum() / results.size

    return c, fdr_hat, fdp, pvals

rng = np.random.default_rng(69)

n1, n2 = 10, 10

def power(d):

    crit = stats.t.ppf(1 - 0.05/2, df=18)
    ncp = d / (np.sqrt((1/n1) + (1/n2)))
    p = stats.nct.sf(crit, df=18, nc=ncp) + stats.nct.cdf(-crit, df=18, nc=ncp)

    return p

root = brentq(lambda d: power(d) - 0.8, 0.01, 2.0)

print(power(root))

c, fdr_hat, fdp, pvals = run(0.8, rng)

q_grid = np.linspace(0.01, 0.5, 50)

n_sim = 200

all_fdp = np.zeros((n_sim, len(q_grid)))

for s in range(n_sim):

    _, _, _, pvals = run(0.8, rng)

    for i, q in enumerate(q_grid):

        bh = benjamini_hochberg(pvals[None, :], alpha=q)
        R = bh.sum()
        all_fdp[s, i] = bh[10:].sum() / max(R, 1)

bh_fdr = all_fdp.mean(axis=0)



fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(c, fdr_hat, label='Estimated FDR')
ax.plot(c, fdp, label='Realised FDP')
ax.legend()
ax.set_xlabel('c'); ax.set_ylabel('FDR/FDP')
fig.savefig('drill04_fdr_hat.png', dpi=150, bbox_inches='tight')

fig2, ax2 = plt.subplots(figsize=(7,5))
ax2.plot(q_grid, bh_fdr, label='Realised FDR')
ax2.plot(q_grid, q_grid, '--', label='q (claimed)')
ax2.legend()
ax2.set_xlabel('q'); ax2.set_ylabel('FDR')
fig2.savefig('drill04_bh_q.png', dpi=150, bbox_inches='tight')