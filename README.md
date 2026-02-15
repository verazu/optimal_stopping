# Optimal Stopping Problem Simulation

A Python simulation that visualizes why **37%** is the optimal stopping point in the secretary problem (also known as the marriage problem or optimal stopping problem).

## Overview

The optimal stopping problem asks: **When should you stop interviewing candidates and pick one?**

The mathematical answer is elegant: **Reject the first 37% (or more precisely, 1/e ≈ 36.8%) of candidates, then pick the first one better than all previously seen.**

This strategy gives you approximately a **37% chance** of selecting the absolute best candidate—regardless of the total number of candidates!

## What This Program Does

1. **Simulates the secretary problem** with different rejection thresholds
2. **Runs 10,000 trials** for each threshold to get empirical success rates
3. **Tests multiple pool sizes** (100 and 1,000 candidates) to show the result is universal
4. **Visualizes the results** with error bars and compares against theory
5. **Generates a plot** showing why 37% is optimal

## Installation

### Prerequisites
- Python 3.7+
- NumPy
- Matplotlib

### Setup
```bash
pip install numpy matplotlib
```

Or with conda:
```bash
conda install numpy matplotlib
```

## Usage

Run the simulation:
```bash
python simulation.py
```

This will:
- Print theoretical analysis of the problem
- Run simulations for pool sizes of 100 and 1,000 candidates
- Generate `optimal_stopping.png` with visualization
- Display the plot (if in an interactive environment)

## Output

The program generates two plots side-by-side showing:
- **X-axis**: Rejection threshold (percentage of candidates to reject)
- **Y-axis**: Success rate (probability of picking the best candidate)
- **Blue line**: Empirical results from simulation (with error bars)
- **Red dashed line**: Theoretical optimum at 36.8%

Both plots peak at ~37%, confirming the mathematical prediction.

## How It Works

### The Algorithm

For each trial:
1. Generate a random ranking of candidates (1 = best, N = worst)
2. Reject the first R% of candidates, remembering the best one seen
3. In the remaining candidates, pick the first one better than the best rejected candidate
4. Check if we picked the absolute best candidate (rank 1)

### The Mathematics

The optimal rejection threshold is found by maximizing the probability:

$$P(\text{success}) = \frac{r}{n} \cdot \int_r^n \frac{dr'}{r'}$$

where:
- n = total number of candidates
- r = number of candidates to reject

Taking the limit as n → ∞ and solving yields:

$$r^* = \frac{n}{e} \approx 0.368n$$

With success probability:

$$P(\text{success}) = \frac{1}{e} \approx 0.368$$

## Code Structure

- **`run_single_trial()`** - Simulates one secretary problem instance
- **`run_simulation()`** - Runs multiple trials and calculates success rates
- **`run_all_thresholds()`** - Tests all rejection percentages (0-100%)
- **`plot_results()`** - Generates visualization
- **`theoretical_analysis()`** - Prints mathematical insights

## Key Insights

✅ **The 37% rule is universal** - works for any pool size (asymptotically)

✅ **Simple to implement** - no complex optimization needed

✅ **Counterintuitive result** - you only need to reject ~1/3 of candidates

✅ **Widely applicable** - parking space selection, house hunting, online dating, etc.

## References

- The Secretary Problem / Marriage Problem (classic in probability theory)
- Related to the optimal stopping theory in decision analysis
- First solved in 1960s by several mathematicians independently

## Example Output

```
============================================================
OPTIMAL STOPPING PROBLEM - THEORETICAL ANALYSIS
============================================================

Optimal rejection threshold: 1/e = 0.3679 ≈ 36.8%
Probability of selecting the best candidate: 1/e = 0.3679 ≈ 36.8%

Key Insights:
  • Reject the first 37% of candidates
  • Pick the first candidate better than all previously seen
  • This strategy has a ~37% success rate
  • Success rate doesn't depend on total number of candidates!
============================================================
```

## License

Free to use and modify.
