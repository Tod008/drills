import numpy as np
from scipy import stats
import pandas as pd
import matplotlib.pyplot as plt

def metrics(reject): #(n_rep, 100) boolean

    power = reject[:,:10].mean(axis=0).mean()

    fwer = np.any(reject[:,10:], axis=1).mean()

    # A replicate with no rejections contributes 0, is not an excluded value.
    # Assumes columns 0-9 are true effects. At delta = 0, that's false --
    # every column is null, so a rejection in 0-9 is counted as a true discovery.
    # Understates the FDR at delta = 0 only (0.90 vs 0.99 actual).
    fdp =  (np.sum(reject[:,10:], axis=1) / np.maximum(reject.sum(axis=1), 1))

    return power, fwer, fdp.mean(), fdp.std(ddof=1) / np.sqrt(len(fdp))

def benjamini_hochberg(pvals, alpha=0.05):
    """Step-up BH. pvals (n_rep, m) -> boolean reject mask, same shape. m is taken from pvals.shape[1], so BH corrects across all columns regardless of which are null."""

    sort = np.argsort(pvals, axis=1)

    sorted_list = np.take_along_axis(pvals, sort, axis=1)

    threshold = np.arange(1, pvals.shape[1]+1) * (alpha / pvals.shape[1])

    # When nothing is passes threshold, -1 is returned.
    max_index = np.max(np.where(sorted_list <= threshold, np.arange(pvals.shape[1]), -1), axis = 1)

    rejected = np.arange(pvals.shape[1]) <= max_index[:,None]

    res = np.zeros_like(pvals, dtype=bool)

    np.put_along_axis(res, sort, rejected, axis=1)

    return res

def run(delta, rng, n_rep=2000, alpha=0.05):

    rng = np.random.default_rng(rng)    

    s = rng.standard_normal((n_rep, 20, 100))

    s[:, :, :10] += delta

    result = stats.ttest_1samp(s, popmean=0, axis=1)

    power, fwer, fdr, unc_fdr_se = metrics(result.pvalue < alpha)

    bonf_power, bonf_fwer, bonf_fdr, bonf_fdr_se = metrics(result.pvalue < alpha /100)

    bh_power, bh_fwer, bh_fdr, bh_fdr_se = metrics(benjamini_hochberg(result.pvalue))   

    # Units of analysis differs for power vs fwer. 
    unc_power_se = np.sqrt(power * (1 - power) / (n_rep * 10))
    unc_fwer_se = np.sqrt(fwer * (1 - fwer) / n_rep)

    bh_power_se = np.sqrt(bh_power * (1 - bh_power) / (n_rep * 10))
    bh_fwer_se = np.sqrt(bh_fwer * (1 - bh_fwer) / n_rep)

    bonf_power_se = np.sqrt(bonf_power * (1 - bonf_power) / (n_rep * 10))
    bonf_fwer_se = np.sqrt(bonf_fwer * (1 - bonf_fwer) / n_rep)

    return dict(bh_power=bh_power,
                bh_power_se=bh_power_se,
                bh_fwer=bh_fwer,
                bh_fwer_se=bh_fwer_se,
                bh_fdr=bh_fdr, 
                bh_fdr_se=bh_fdr_se, 
                bonf_power=bonf_power, 
                bonf_power_se=bonf_power_se, 
                bonf_fwer=bonf_fwer, 
                bonf_fwer_se=bonf_fwer_se, 
                bonf_fdr=bonf_fdr, 
                bonf_fdr_se=bonf_fdr_se, 
                unc_power=power, 
                unc_power_se=unc_power_se, 
                unc_fwer=fwer, 
                unc_fwer_se=unc_fwer_se, 
                unc_fdr=fdr, 
                unc_fdr_se=unc_fdr_se)


table = []

# rng is passed in rather than created inside, so there is independent noise per delta, deliberately not paired.
rng = np.random.default_rng(69)

for x in [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5]:

    results = run(x, rng)

    row = [x] + [results[key] for key in ['bh_power', 'bh_power_se', 'bh_fwer', 'bh_fwer_se', 'bh_fdr', 'bh_fdr_se', 'bonf_power', 'bonf_power_se', 'bonf_fwer', 'bonf_fwer_se', 'bonf_fdr', 'bonf_fdr_se', 'unc_power', 'unc_power_se', 'unc_fwer', 'unc_fwer_se', 'unc_fdr', 'unc_fdr_se']]
    table.append(row)

df = pd.DataFrame(table, columns=['delta', 'bh_power', 'bh_power_se', 'bh_fwer', 'bh_fwer_se', 'bh_fdr', 'bh_fdr_se', 'bonf_power', 'bonf_power_se', 'bonf_fwer', 'bonf_fwer_se', 'bonf_fdr', 'bonf_fdr_se', 'unc_power', 'unc_power_se', 'unc_fwer', 'unc_fwer_se', 'unc_fdr', 'unc_fdr_se'])

fig, ax = plt.subplots(figsize=(7, 5))
for col, se, label in [('unc_power', 'unc_power_se', 'Uncorrected'),
                       ('bh_power', 'bh_power_se', 'BH'),
                       ('bonf_power', 'bonf_power_se', 'Bonferroni')]:
    ax.errorbar(df['delta'], df[col], yerr=df[se], marker='o', capsize=3, label=label)

crit = stats.t.ppf(1 - 0.05/2, df=19)
d = np.linspace(0, 1.5, 100)
nc = d * np.sqrt(20)
analytic = stats.nct.sf(crit, df=19, nc=nc) + stats.nct.cdf(-crit, df=19, nc=nc)
ax.plot(d, analytic, 'k--', lw=1, label='Analytic (nct)')

ax.set_xlabel('δ'); ax.set_ylabel('Power'); ax.set_ylim(0, 1.02)
ax.legend(); ax.grid(alpha=0.3)
fig.savefig('drill03_power.png', dpi=150, bbox_inches='tight')

fig2, ax2 = plt.subplots(figsize=(7, 5))
for col, se, label in [('unc_fdr', 'unc_fdr_se', 'Uncorrected'),
                       ('bh_fdr', 'bh_fdr_se', 'BH'),
                       ('bonf_fdr', 'bonf_fdr_se', 'Bonferroni')]:
    ax2.errorbar(df['delta'], df[col], yerr=df[se], marker='o', capsize=3, label=label)

ax2.axhline(0.05, color='grey', ls=':', lw=1, label='q = 0.05')
ax2.set_xlabel('δ'); ax2.set_ylabel('False discovery rate'); ax2.set_ylim(0, 1.02)
ax2.legend(); ax2.grid(alpha=0.3)
fig2.savefig('drill03_fdr.png', dpi=150, bbox_inches='tight')

print(df.to_string(index=False))