import numpy as np

rng = np.random.default_rng()

s = rng.standard_normal((20, 100))

print(s, s.shape)