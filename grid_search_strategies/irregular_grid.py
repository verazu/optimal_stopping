"""
Spiral search on irregular grids using Dijkstra-order search.

In irregular grids (non-parallel streets, non-uniform blocks, dead-ends, diagonals),
the concept of "distance" becomes ambiguous. Rather than searching by Euclidean rings
or fixed block counts, we search by actual walking distance from the restaurant.

Dijkstra-order search visits street segments in order of their walking distance from
the origin, guaranteeing we search closer areas before more distant ones.
"""

import random
import heapq
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from collections import defaultdict
import numpy as np

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

class IrregularGrid:
    """Represents an irregular street grid."""
    
    def __init__(self, width=10, height=10, irregularity=0.3):
        """
        Create an irregular grid.
        
        Args:
            width: Grid width
            height: Grid height
            irregularity: How much to deviate from a regular grid (0-1)
        """
        self.width = width
        self.height = height
        self.segments = []  # List of (start, end) tuples representing street segments
        self.segment_lengths = {}  # Map segment to length
        self.graph = defaultdict(list)  # Adjacency list: point -> [(neighbor, segment_index, length)]
        self.points = set()  # All intersection points
        
        self._generate_grid(irregularity)
    
    def _generate_grid(self, irregularity):
        """Generate an irregular grid by adding noise to a regular grid."""
        # Create a base regular grid
        base_points = {}
        for i in range(self.width + 1):
            for j in range(self.height + 1):
                # Add noise to coordinates
                x = i + random.uniform(-irregularity, irregularity)
                y = j + random.uniform(-irregularity, irregularity)
                base_points[(i, j)] = (x, y)
                self.points.add((x, y))
        
        # Create horizontal segments
        for i in range(self.width + 1):
            for j in range(self.height):
                p1_key = (i, j)
                p2_key = (i, j + 1)
                # Randomly skip some segments (dead-ends, removed streets)
                if random.random() < 0.85:  # 85% chance of keeping segment
                    p1 = base_points[p1_key]
                    p2 = base_points[p2_key]
                    self._add_segment(p1, p2)
        
        # Create vertical segments
        for i in range(self.width):
            for j in range(self.height + 1):
                p1_key = (i, j)
                p2_key = (i + 1, j)
                # Randomly skip some segments
                if random.random() < 0.85:
                    p1 = base_points[p1_key]
                    p2 = base_points[p2_key]
                    self._add_segment(p1, p2)
        
        # Add some diagonal segments (cutting through blocks)
        for i in range(self.width):
            for j in range(self.height):
                if random.random() < 0.1:  # 10% chance of a diagonal
                    p1_key = (i, j)
                    p2_key = (i + 1, j + 1)
                    p1 = base_points[p1_key]
                    p2 = base_points[p2_key]
                    self._add_segment(p1, p2)
    
    def _add_segment(self, p1, p2):
        """Add a street segment between two points."""
        length = np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
        segment_idx = len(self.segments)
        self.segments.append((p1, p2))
        self.segment_lengths[segment_idx] = length
        
        # Add to graph
        self.graph[p1].append((p2, segment_idx, length))
        self.graph[p2].append((p1, segment_idx, length))
    
    def dijkstra_search_order(self, start=(0, 0)):
        """
        Return street segments ordered by walking distance from start using Dijkstra's algorithm.
        
        This is Dijkstra-order search: visit segments in order of their closest point's distance
        from the origin.
        """
        # Find closest point to start
        closest_point = min(self.points, key=lambda p: np.sqrt((p[0] - start[0])**2 + (p[1] - start[1])**2))
        
        # Dijkstra from closest point
        distances = {point: float('inf') for point in self.points}
        distances[closest_point] = 0
        pq = [(0, closest_point)]
        visited_segments = set()
        segment_order = []
        
        while pq:
            dist, point = heapq.heappop(pq)
            
            if dist > distances[point]:
                continue
            
            # Add all segments from this point to the order
            for neighbor, seg_idx, length in self.graph[point]:
                if seg_idx not in visited_segments:
                    visited_segments.add(seg_idx)
                    segment_order.append(seg_idx)
                
                new_dist = dist + length
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    heapq.heappush(pq, (new_dist, neighbor))
        
        return segment_order, distances
    
    def spiral_search_order_with_rewalks(self, start=(0, 0)):
        """
        Simulate actually walking a spiral on an irregular grid, including re-walks.
        
        When spiraling outward on irregular grids, you often have to backtrack or
        re-walk streets because the spiral doesn't close cleanly. This implementation
        actually walks the search path, counting segments traversed (including re-walks).
        """
        # Find closest point to start
        closest_point = min(self.points, key=lambda p: np.sqrt((p[0] - start[0])**2 + (p[1] - start[1])**2))
        
        # Spiral outward using BFS-like approach, but track actual walking
        segment_path = []  # List of segment indices in the order walked
        visited_segments = set()
        current_ring_points = {closest_point}
        visited_intersection_points = set()
        
        while len(visited_segments) < len(self.segments):
            # For each point in current ring, walk to adjacent unvisited segments
            next_ring_points = set()
            points_in_ring = list(current_ring_points)
            
            for point in points_in_ring:
                # Sort neighbors by distance to prefer outward movement
                neighbors = []
                for neighbor, seg_idx, length in self.graph[point]:
                    dist = np.sqrt((neighbor[0] - start[0])**2 + (neighbor[1] - start[1])**2)
                    neighbors.append((dist, neighbor, seg_idx, length))
                
                neighbors.sort()
                
                for dist, neighbor, seg_idx, length in neighbors:
                    if seg_idx not in visited_segments:
                        segment_path.append(seg_idx)
                        visited_segments.add(seg_idx)
                        next_ring_points.add(neighbor)
                    elif neighbor not in visited_intersection_points:
                        # We need to backtrack: re-walk the segment to get to new area
                        segment_path.append(seg_idx)
                        next_ring_points.add(neighbor)
                
                visited_intersection_points.add(point)
            
            if not next_ring_points:
                break
            current_ring_points = next_ring_points
        
        return segment_path
    
    def spiral_search_order(self, start=(0, 0)):
        """
        Attempt a spiral-like search on irregular grid (simpler version).
        
        Returns segments in spiral-like order without explicit re-walks.
        """
        # Find closest point to start
        closest_point = min(self.points, key=lambda p: np.sqrt((p[0] - start[0])**2 + (p[1] - start[1])**2))
        
        # BFS to find segments by distance
        from collections import deque
        segment_order = []
        visited_segments = set()
        current_ring_points = {closest_point}
        
        while len(visited_segments) < len(self.segments):
            next_ring_points = set()
            for point in current_ring_points:
                for neighbor, seg_idx, length in self.graph[point]:
                    if seg_idx not in visited_segments:
                        visited_segments.add(seg_idx)
                        segment_order.append(seg_idx)
                        next_ring_points.add(neighbor)
            
            if not next_ring_points:
                break
            current_ring_points = next_ring_points
        
        return segment_order, 0


def simulate_search(grid, strategy, num_trials=1000):
    """
    Simulate searching for a car on the irregular grid.
    
    Args:
        grid: IrregularGrid instance
        strategy: 'dijkstra' or 'spiral'
        num_trials: Number of simulation trials
    
    Returns:
        Expected walking distance and other metrics
    """
    start = (0, 0)
    
    if strategy == 'dijkstra':
        search_order, _ = grid.dijkstra_search_order(start)
    else:  # spiral
        search_order = grid.spiral_search_order_with_rewalks(start)
    
    total_distance = 0
    
    for _ in range(num_trials):
        # Randomly place car on a segment
        # For spiral, we sample from original segments; for dijkstra, we do the same
        car_segment_idx = random.randint(0, len(grid.segments) - 1)
        car_position = random.random()  # 0-1 along the segment
        
        # Walk the search path until finding the car
        distance_walked = 0
        found = False
        for seg_idx in search_order:
            segment_length = grid.segment_lengths[seg_idx]
            
            if seg_idx == car_segment_idx:
                # Found the car on this segment
                distance_walked += car_position * segment_length
                found = True
                break
            else:
                # Walk the full segment
                distance_walked += segment_length
        
        if not found:
            # Car is on a segment not in our search path (shouldn't happen with proper implementation)
            continue
        
        total_distance += distance_walked
    
    expected_distance = total_distance / num_trials
    return expected_distance


def visualize_search(grid, strategy, save_path=None):
    """Visualize the search path on the irregular grid."""
    fig, ax = plt.subplots(figsize=(10, 10))
    
    start = (0, 0)
    
    if strategy == 'dijkstra':
        search_order, distances = grid.dijkstra_search_order(start)
        title = 'Dijkstra-Order Search (by Walking Distance)'
    else:  # spiral
        search_order, revisits = grid.spiral_search_order(start)
        distances = {}
        title = f'Spiral-Like Search (Revisits: {revisits})'
    
    # Draw all segments
    for i, (p1, p2) in enumerate(grid.segments):
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'lightgray', linewidth=0.5, zorder=1)
    
    # Draw search path with color gradient
    colors = plt.cm.viridis(np.linspace(0, 1, len(search_order)))
    for step, seg_idx in enumerate(search_order):
        p1, p2 = grid.segments[seg_idx]
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=colors[step], linewidth=2, zorder=2, alpha=0.7)
    
    # Mark restaurant
    ax.plot(start[0], start[1], 'r*', markersize=20, label='Restaurant', zorder=3)
    
    ax.set_aspect('equal')
    ax.set_title(title, fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    plt.close()


def main():
    """Run the irregular grid search simulation."""
    print("Spiral Search on Irregular Grids")
    print("=" * 50)
    
    # Create an irregular grid
    print("\nGenerating irregular grid...")
    grid = IrregularGrid(width=8, height=8, irregularity=0.25)
    print(f"Grid created with {len(grid.segments)} street segments")
    
    # Test Dijkstra-order search
    print("\n--- Dijkstra-Order Search ---")
    dijkstra_distance = simulate_search(grid, 'dijkstra', num_trials=1000)
    print(f"Expected walking distance: {dijkstra_distance:.2f}")
    visualize_search(grid, 'dijkstra', 'dijkstra_search.png')
    print("Visualization saved to dijkstra_search.png")
    
    # Test spiral search
    print("\n--- Spiral-Like Search ---")
    spiral_distance = simulate_search(grid, 'spiral', num_trials=1000)
    print(f"Expected walking distance: {spiral_distance:.2f}")
    visualize_search(grid, 'spiral', 'spiral_search_irregular.png')
    print("Visualization saved to spiral_search_irregular.png")
    
    # Compare
    print("\n--- Comparison ---")
    improvement = (spiral_distance - dijkstra_distance) / spiral_distance * 100
    print(f"Dijkstra-order is {improvement:.1f}% more efficient than spiral on this grid")


if __name__ == '__main__':
    main()
