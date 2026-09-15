# Leg 0 — statistics implementation drills

## What this is
This is a repo on the drills I'm doing daily to strengthen my coding fundamentals as I read methods from An Introduction to Statistical Learning. 
Drill03 and Drill04 have useful code, since they actually have implementation of methods I've read.

## Setup
Developed on Python 3.13.
```
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python drill03.py
```
The figures get written to their own png files.

## Drills
### drill01 — Simulating null data 
- File: drill01.py
- Seed: 69
- Parameters: None
- What it shows: (20, 100) random numpy array
- Reading it came from: None

### drill02 — T-test on simulated null data against 0
- File: drill02.py
- Seed: 69
- Parameters: (alpha=0.05)
- What it shows: The p-values of the t-test, the minimum p-value, and how many were below 0.05
- Reading it came from: None

### drill03 — Multiple testing — Bonferroni and BH vs. uncorrected.
- File: drill03.py
- Seed: 69
- Parameters: (m=100, δ=sweep from 0.0-1.5, number of simulations=2000)
- What it shows: 
drill03_power.png shows the difference between uncorrected power and Benjamini-Hochberg and Bonferroni correction across delta from 0.0 to 1.5.
drill03_fdr.png shows their false discovery rates of the different methods through deltas 0.0-1.5
- Reading it came from: An Introduction to Statistical Learning chapter 13.1-13.4

### drill04 — Re-sampling - Estimated FDR vs FDP 
- File: drill04.py
- Seed: 69
- Parameters: (n1=n2=10, m=100, δ≈1.325, number of simulations=200, B=1000, 10 non-null columns)
- What it shows: 
drill04_fdr_hat.png: shows the difference between the estimated FDR (blue) and the FDP (orange). Blue overestimates because of the all null inflation, most clear at the left edge. The crossover and the right tail gap comes from comparing an average against a single realization. 
drill04_bh_q.png: the solid curve is the realised FDR, the FDP averaged over 200 datasets at each q. The dashed diagonal is the target q. BH guarantees that the true FDR stays at or below q. The curve is slightly above when q<=0.07, but within 2 SE across the 200 datasets, consistent with noise. The curve sits near q·m_0/m = 0.9q rather than on the diagonal, because only 90 of the 100 columns are null.
- Reading it came from: An Introduction to Statistical Learning chapter 13.5

## Vocabulary notes
- **FWER vs FDR**
    - FWER is the family wise error rate, and that is the probability you have of making at least 1 Type-I error.
    - FDR is on the other hand, the expected proportion of the number of Type-I error you will make among the total number of rejections.
- **one-sample vs two-sample, one- vs two-tailed**
    - one-sample is when you have only one sample and do the t-test against a set target value. Whereas two-sample t-test compares the means of two samples with the t-test.
    - one-tailed vs two-tailed t-test difference is the cutoff of one-tail is only at one tail of the distribution, whereas two-tailed cuts at both ends of the distribution.
- **exchangeability**
    - What permutation assumes. If the null is true, then the group labels are arbitrary, and shuffling them won't affect the joint distribution. 
- **the bias in V̂**
    - V_hat is inflated because it uses all m features as null, when only m-10 are.
- **why one dataset gives a step function, not a smooth FDP curve**
    - Since there is only one dataset, V and R are given back as integers, so FDP moves in steps. FDR is the expectation across datasets, which is why it is smooth across many datasets.
