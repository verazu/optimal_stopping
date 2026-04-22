import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import math
import random

def get_all_segments(n):
    """Get all street segments within Manhattan distance n from (0,0)."""
    segments = []
    # Horizontal segments: from (x,y) to (x+1,y)
    for x in range(-n, n):
        for y in range(-n, n+1):
            segments.append(((x, y), (x+1, y)))
    # Vertical segments: from (x,y) to (x,y+1)
    for x in range(-n, n+1):
        for y in range(-n, n):
            segments.append(((x, y), (x, y+1)))
    return segments

def get_neighbors(segment, all_segments):
    """Get neighboring segments that share an endpoint."""
    end1, end2 = segment
    neighbors = []
    for s in all_segments:
        if s == segment:
            continue
        s1, s2 = s
        if end1 in (s1, s2) or end2 in (s1, s2):
            neighbors.append(s)
    return neighbors

def segment_midpoint(seg):
    """Get the midpoint of a segment."""
    return ((seg[0][0] + seg[1][0]) / 2, (seg[0][1] + seg[1][1]) / 2)

def segment_distance(seg):
    """Manhattan distance from origin to segment midpoint."""
    mid = segment_midpoint(seg)
    return abs(mid[0]) + abs(mid[1])

def segment_angle(seg):
    """Angle of segment midpoint from origin."""
    mid = segment_midpoint(seg)
    return np.arctan2(mid[1], mid[0])

def get_spiral_path(segments):
    """Generate the expanding square spiral path for segments."""
    sorted_segments = sorted(segments, key=lambda s: (segment_distance(s), segment_angle(s)))
    return sorted_segments

def get_cross_spiral_path(segments, n):
    """Generate the 4-armed cross (out and back) then spiral path for segments."""
    path = []
    # Cross: 4 arms, out and back
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # N, E, S, W
    for dx, dy in directions:
        arm_segments = []
        if dx == 0:  # Vertical arm
            for i in range(n):
                arm_segments.append(((dx, i * dy), (dx, (i + 1) * dy)))
        else:  # Horizontal arm
            for i in range(n):
                arm_segments.append(((i * dx, dy), ((i + 1) * dx, dy)))
        # Out
        path.extend(arm_segments)
        # Back
        path.extend(arm_segments[::-1])
    # Remaining segments in spiral order
    cross_segments = set(path)
    remaining = [s for s in segments if s not in cross_segments]
    remaining_sorted = sorted(remaining, key=lambda s: (segment_distance(s), segment_angle(s)))
    path.extend(remaining_sorted)
    return path

def get_east_biased_spiral_path(segments):
    """Generate an east-biased spiral path for segments."""
    def biased_key(s):
        mid = segment_midpoint(s)
        # Bias towards positive x (east)
        bias = -mid[0]  # Negative to prioritize higher x
        return (segment_distance(s), bias, segment_angle(s))
    sorted_segments = sorted(segments, key=biased_key)
    return sorted_segments

def get_long_skinny_spiral_path(segments):
    """Generate a long skinny spiral path prioritizing horizontal movement."""
    def skinny_key(s):
        mid = segment_midpoint(s)
        is_horizontal = 1 if s[0][1] == s[1][1] else 0  # Prioritize horizontal
        return (segment_distance(s), -is_horizontal, segment_angle(s))
    sorted_segments = sorted(segments, key=skinny_key)
    return sorted_segments

def get_residential_street_path(segments):
    """Generate path for residential streets (not on main axes)."""
    residential = [s for s in segments if not ((s[0][0] == s[1][0] == 0) or (s[0][1] == s[1][1] == 0))]
    sorted_residential = sorted(residential, key=lambda s: (segment_distance(s), segment_angle(s)))
    return sorted_residential

def calculate_expected_distance(path, segments, weights=None, num_trials=10000):
    """Calculate the expected walking distance using Monte Carlo simulation."""
    if weights is None:
        weights = [1] * len(segments)
    
    # Normalize weights to probabilities
    total_weight = sum(weights)
    probabilities = [w / total_weight for w in weights]
    
    if path == "random":
        # Random walk simulation
        total_distance = 0
        start_segment = ((0, 0), (1, 0))  # Horizontal segment from (0,0) to (1,0)
        for _ in range(num_trials):
            # Sample a car segment based on weights
            car_seg_idx = np.random.choice(len(segments), p=probabilities)
            car_seg = segments[car_seg_idx]
            
            # Generate random walk
            path_walk = []
            current = start_segment
            max_steps = 1000  # Prevent infinite loops
            steps = 0
            while current != car_seg and steps < max_steps:
                path_walk.append(current)
                neighbors = get_neighbors(current, segments)
                if not neighbors:
                    break
                current = random.choice(neighbors)
                steps += 1
            if current == car_seg:
                total_distance += len(path_walk)
            else:
                # If didn't find, add max_steps
                total_distance += max_steps
        expected_distance = total_distance / num_trials
    else:
        # Systematic path simulation
        total_distance = 0
        for _ in range(num_trials):
            # Sample a car segment based on weights
            car_seg_idx = np.random.choice(len(segments), p=probabilities)
            car_seg = segments[car_seg_idx]
            
            # Find the step when we walk the segment containing the car
            for i, seg in enumerate(path):
                if seg == car_seg:
                    total_distance += (i + 1)  # +1 because you walk the segment to find it
                    break
        
        expected_distance = total_distance / num_trials
    return expected_distance

def visualize_path(path, title, filename):
    """Visualize the search path by plotting connected midpoints."""
    midpoints = [segment_midpoint(seg) for seg in path]
    x_coords = [m[0] for m in midpoints]
    y_coords = [m[1] for m in midpoints]
    fig, ax = plt.subplots(figsize=(8, 8))
    # Plot the path as a line with markers
    ax.plot(x_coords, y_coords, marker='o', linestyle='-', markersize=3, linewidth=1, color='blue')
    # Color points by step
    colors = plt.cm.viridis(np.linspace(0, 1, len(path)))
    for i, (x, y) in enumerate(zip(x_coords, y_coords)):
        ax.scatter(x, y, color=colors[i], s=20, zorder=5)
    # Colorbar
    sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(vmin=0, vmax=len(path)))
    sm.set_array([])
    fig.colorbar(sm, ax=ax, label='Step number')
    ax.set_title(title)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.grid(True)
    ax.axis('equal')
    plt.savefig(filename)
    plt.close()

def main():
    np.random.seed(42)  # For reproducible results
    n = 5  # radius
    all_segments = get_all_segments(n)
    residential_segments = [s for s in all_segments if not ((s[0][0] == s[1][0] == 0) or (s[0][1] == s[1][1] == 0))]
    
    weights_uniform = [1] * len(all_segments)
    weights_east = [1 + max(0, segment_midpoint(s)[0]) for s in all_segments]
    
    strategies = [
        ("Spiral (Uniform)", get_spiral_path(all_segments), all_segments, weights_uniform),
        ("Cross + Spiral", get_cross_spiral_path(all_segments, n), all_segments, weights_uniform),
        ("Random", "random", all_segments, weights_uniform),
        ("East Biased Spiral", get_east_biased_spiral_path(all_segments), all_segments, weights_east),
        ("Long Skinny Spiral", get_long_skinny_spiral_path(all_segments), all_segments, weights_uniform),
        ("Residential Street", get_residential_street_path(residential_segments), residential_segments, [1] * len(residential_segments)),
    ]
    
    print("Expected Walking Distances (n=5, 10,000 trials):")
    for name, path, segments, weights in strategies:
        expected_dist = calculate_expected_distance(path, segments, weights)
        print(f"{name}: {expected_dist:.2f}")
        if path != "random":  # Skip visualization for random walk
            visualize_path(path, f"{name} Search Path", f"{name.lower().replace(' ', '_').replace('+', '').replace('(', '').replace(')', '')}_path.png")
    
    print("\nVisualizations saved as PNG files (random walk not visualized).")

    # Generate sample random path for visualization
    random.seed(42)  # For reproducibility
    start_segment = ((0, 0), (1, 0))  # Horizontal segment from (0,0) to (1,0)
    sample_random_path = [start_segment]
    visited = set([start_segment])
    current = start_segment
    for _ in range(len(all_segments) * 2):  # Arbitrary limit to prevent infinite loop
        neighbors = [n for n in get_neighbors(current, all_segments) if n not in visited]
        if not neighbors:
            break
        current = random.choice(neighbors)
        sample_random_path.append(current)
        visited.add(current)
    
    # Visualize sample random path
    visualize_path(sample_random_path, "Sample Random Walk Path", "random_path.png")

if __name__ == "__main__":
    main()