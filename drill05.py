import numpy as np

# 1. FIXED SETTINGS (Stated at the top)
Scale = 2       # Beta (mean) parameter
N = 30          # Sample size per repetition 
Rep = 10000     # Number of simulated samples
rng = np.random.default_rng(69)  # Seeded random generator

def sample_median(e, N, rep, rng):
    print(e - N)

def run():
    sample_median(2, N, Rep, rng)

run()