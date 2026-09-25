import numpy as np
import matplotlib.pyplot as plt

# 1. FIXED SETTINGS (Stated at the top)
Scale = 2       # Beta (mean) parameter
N = 30          # Sample size per repetition
Rep = 10000     # Number of simulated samples
rng = np.random.default_rng(69)  # Seeded random generator

def sample_median(Scale, N, rep, rng):

    arr = rng.exponential(scale=Scale, size = (rep, N))

    return np.median(arr, axis=1), arr[0], arr[100]

my_arr, first_sample, hundredth_sample = sample_median(Scale, N, Rep, rng)

sd = np.std(my_arr)

mean = np.mean(my_arr)

# F(x) = 1 - e^(-x/beta)    and median is defined by F(m) = 1/2 
# 1 - e^(-m/beta) = 0.5
# e^(-m/beta) = 0.5         taking a ln() on both sides
# -m/beta = ln(0.5)            ln(0.5) = -ln(2)
# m/beta = ln(2)
#m = beta * ln(2)
m = Scale * np.log(2)

def bootstrap_se(s1, n=N, rep=Rep, rng=rng):

    resampled = rng.choice(s1, size=(rep, n), replace=True)

    bootstrap_median = np.median(resampled, axis=1)

    return np.std(bootstrap_median), bootstrap_median, np.mean(bootstrap_median)

calculated_se, calculated_median, calculated_mean = bootstrap_se(first_sample)
hun_se, hun_med, hun_mean = bootstrap_se(hundredth_sample)


print(my_arr.shape, 'sd = ', sd, f'bootstrap se = {calculated_se}', mean, m, f'calculated_se = {calculated_se}', f'hundredth_se = {hun_se}')

fig, ax = plt.subplots(figsize=(8,5.5))
ax.hist(my_arr, bins=50, density=True, color='#CBC3E3', label=f'Sampling distribution (simulated SE = {sd:.3f}) ')
ax.hist(calculated_median, bins=50, density=True, histtype='step', linewidth=2, color='#7D56B1', label=f'Bootstrap Dist. (SE = {calculated_se:.3f})')
ax.axvline(mean, color='#F98128', linestyle='dashed', linewidth=2, label=f'Mean of medians ({mean:.3f})')
ax.axvline(m, color='#36013F', linestyle='dotted', linewidth=2, label=f'True median ({m:.3f})')
ax.axvline(np.median(first_sample), color='#7D56B1', linestyle='dashdot', linewidth=2, label=f'Observed Sample Median ({np.median(first_sample):.3f})')
ax.set_title(f'True Sampling Distribution vs. Bootstrap Distribution (n={N})', fontsize=12, pad=15)
ax.set_xlabel("Median Value")
ax.set_ylabel("Density")
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_xlim(0.5, 2.8)
ax.grid(axis='y', alpha=0.3)
ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', frameon=False)
fig.savefig('drill05_medians.png', dpi=150, bbox_inches='tight')