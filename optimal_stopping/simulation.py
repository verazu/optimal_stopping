import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, List

def run_single_trial(pool_size: int, rejection_threshold: float) -> bool:
    """
    Run a single trial of the secretary problem.
    
    Args:
        pool_size: Number of candidates to interview
        rejection_threshold: Fraction of candidates to reject (0.0 to 1.0)
    
    Returns:
        True if the best candidate was selected, False otherwise
    """
    # Generate random rankings (1 = best, pool_size = worst)
    candidates = np.random.permutation(pool_size) + 1
    
    # Number of candidates to reject in the initial phase
    num_reject = int(pool_size * rejection_threshold)
    
    # If we reject everyone or nobody, handle edge cases
    if num_reject >= pool_size:
        return False
    if num_reject == 0:
        # Pick the first candidate
        return candidates[0] == 1
    
    # Find the best candidate in the rejection phase
    best_in_rejection = np.min(candidates[:num_reject])
    
    # In the selection phase, pick the first candidate better than the best seen
    for i in range(num_reject, pool_size):
        if candidates[i] < best_in_rejection:
            # Found a candidate better than the best in rejection phase
            return candidates[i] == 1
    
    # If no candidate in selection phase beats the rejection phase best,
    # we pick the last candidate (forced choice)
    return candidates[-1] == 1


def run_simulation(pool_size: int, rejection_threshold: float, num_trials: int = 10000) -> Tuple[float, float]:
    """
    Run multiple trials and calculate success rate.
    
    Args:
        pool_size: Number of candidates
        rejection_threshold: Fraction of candidates to reject
        num_trials: Number of simulations to run
    
    Returns:
        Tuple of (success_rate, standard_error)
    """
    successes = sum(run_single_trial(pool_size, rejection_threshold) for _ in range(num_trials))
    success_rate = successes / num_trials
    std_error = np.sqrt(success_rate * (1 - success_rate) / num_trials)
    return success_rate, std_error


def run_all_thresholds(pool_size: int, num_trials: int = 10000) -> Tuple[List[float], List[float], List[float]]:
    """
    Run simulations across multiple rejection thresholds.
    
    Args:
        pool_size: Number of candidates
        num_trials: Number of trials per threshold
    
    Returns:
        Tuple of (thresholds, success_rates, std_errors)
    """
    thresholds = np.linspace(0, 1, 41)  # 0% to 100% in 2.5% increments
    success_rates = []
    std_errors = []
    
    for threshold in thresholds:
        rate, std_err = run_simulation(pool_size, threshold, num_trials)
        success_rates.append(rate)
        std_errors.append(std_err)
    
    return thresholds, success_rates, std_errors


def plot_results(pool_sizes: List[int] = [100, 1000], num_trials: int = 10000):
    """
    Plot success rate vs. rejection threshold for different pool sizes.
    
    Args:
        pool_sizes: List of candidate pool sizes to test
        num_trials: Number of trials per threshold
    """
    fig, axes = plt.subplots(1, len(pool_sizes), figsize=(14, 5))
    if len(pool_sizes) == 1:
        axes = [axes]
    
    optimal_threshold = 1 / np.e  # ≈ 0.368
    optimal_rate = 1 / np.e  # ≈ 0.368
    
    for idx, pool_size in enumerate(pool_sizes):
        print(f"Running simulation for pool size {pool_size}...")
        thresholds, rates, errors = run_all_thresholds(pool_size, num_trials)
        
        ax = axes[idx]
        
        # Plot simulation results
        ax.errorbar(thresholds * 100, rates, yerr=errors, fmt='o-', 
                   label='Simulated', alpha=0.7, capsize=3, linewidth=2)
        
        # Plot theoretical optimum
        ax.axvline(optimal_threshold * 100, color='red', linestyle='--', 
                  linewidth=2, label=f'Optimal: {optimal_threshold*100:.1f}%')
        ax.axhline(optimal_rate, color='red', linestyle='--', 
                  linewidth=1, alpha=0.5)
        
        # Formatting
        ax.set_xlabel('Rejection Threshold (%)', fontsize=11)
        ax.set_ylabel('Success Rate (Probability of Picking Best)', fontsize=11)
        ax.set_title(f'Secretary Problem: {pool_size} Candidates', fontsize=12, fontweight='bold')
        ax.set_ylim(0.2, 0.45)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=10)
    
    plt.tight_layout()
    plt.savefig('optimal_stopping.png', dpi=150, bbox_inches='tight')
    print("Plot saved as 'optimal_stopping.png'")
    plt.show()


def theoretical_analysis():
    """Print theoretical analysis of the optimal stopping problem."""
    e = np.e
    optimal_threshold = 1 / e
    optimal_probability = 1 / e
    
    print("\n" + "="*60)
    print("OPTIMAL STOPPING PROBLEM - THEORETICAL ANALYSIS")
    print("="*60)
    print(f"\nOptimal rejection threshold: 1/e = {optimal_threshold:.4f} ≈ {optimal_threshold*100:.1f}%")
    print(f"Probability of selecting the best candidate: 1/e = {optimal_probability:.4f} ≈ {optimal_probability*100:.1f}%")
    print("\nKey Insights:")
    print("  • Reject the first 37% of candidates")
    print("  • Pick the first candidate better than all previously seen")
    print("  • This strategy has a ~37% success rate")
    print("  • Success rate doesn't depend on total number of candidates!")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Print theoretical analysis
    theoretical_analysis()
    
    # Run simulations and plot results
    print("Starting simulations...")
    plot_results(pool_sizes=[100, 1000], num_trials=10000)
    print("\nSimulation complete!")
