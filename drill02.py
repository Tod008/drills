import numpy as np
from scipy import stats

rng = np.random.default_rng(69)

s = rng.standard_normal((20, 100))

result = stats.ttest_1samp(s, popmean=0)

p_value = result.pvalue

print(p_value.shape, min(p_value), np.sum(result.pvalue < 0.05))