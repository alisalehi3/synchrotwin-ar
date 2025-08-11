"""
Cross-Recurrence Quantification Analysis (CRQA)
===============================================

This module implements Cross-Recurrence Quantification Analysis for analyzing
coupling and coordination between two time series.

References:
- Wallot, S., & Leonardi, G. (2018). Analyzing multivariate dynamics using 
  cross-recurrence quantification analysis (CRQA). Frontiers in Psychology, 9, 2232.
"""

import numpy as np
from scipy.spatial.distance import pdist, squareform, cdist
from scipy.stats import zscore
import warnings


class CRQAAnalyzer:
    """
    Cross-Recurrence Quantification Analysis for dyadic synchrony measurement.
    
    CRQA analyzes the recurrence patterns between two time series to quantify
    their coupling and coordination dynamics.
    """
    
    def __init__(self, embedding_dimension=3, time_delay=1, radius=None, 
                 distance_metric='euclidean', normalize=True):
        """
        Initialize CRQA analyzer.
        
        Args:
            embedding_dimension (int): Embedding dimension for phase space reconstruction
            time_delay (int): Time delay for embedding
            radius (float): Recurrence threshold (auto-calculated if None)
            distance_metric (str): Distance metric for recurrence calculation
            normalize (bool): Whether to normalize input signals
        """
        self.embedding_dimension = embedding_dimension
        self.time_delay = time_delay
        self.radius = radius
        self.distance_metric = distance_metric
        self.normalize = normalize
        
    def embed_signal(self, signal):
        """
        Perform time-delay embedding of the signal.
        
        Args:
            signal (np.array): Input time series
            
        Returns:
            np.array: Embedded signal matrix
        """
        if self.normalize:
            signal = zscore(signal)
            
        n = len(signal)
        m = self.embedding_dimension
        tau = self.time_delay
        
        # Calculate number of embedded vectors
        n_vectors = n - (m - 1) * tau
        
        if n_vectors <= 0:
            raise ValueError("Signal too short for given embedding parameters")
            
        # Create embedded matrix
        embedded = np.zeros((n_vectors, m))
        
        for i in range(m):
            start_idx = i * tau
            end_idx = start_idx + n_vectors
            embedded[:, i] = signal[start_idx:end_idx]
            
        return embedded
    
    def calculate_cross_distance_matrix(self, signal1, signal2):
        """
        Calculate cross-distance matrix between embedded signals.
        
        Args:
            signal1 (np.array): First time series
            signal2 (np.array): Second time series
            
        Returns:
            np.array: Cross-distance matrix
        """
        # Embed both signals
        embedded1 = self.embed_signal(signal1)
        embedded2 = self.embed_signal(signal2)
        
        # Calculate cross-distance matrix
        cross_distances = cdist(embedded1, embedded2, metric=self.distance_metric)
        
        return cross_distances
    
    def calculate_recurrence_matrix(self, signal1, signal2, radius=None):
        """
        Calculate cross-recurrence matrix.
        
        Args:
            signal1 (np.array): First time series
            signal2 (np.array): Second time series
            radius (float): Recurrence threshold
            
        Returns:
            np.array: Binary cross-recurrence matrix
        """
        # Calculate cross-distance matrix
        cross_distances = self.calculate_cross_distance_matrix(signal1, signal2)
        
        # Determine radius if not provided
        if radius is None:
            if self.radius is None:
                # Use 10% of maximum distance as default
                radius = 0.1 * np.max(cross_distances)
            else:
                radius = self.radius
        
        # Create binary recurrence matrix
        recurrence_matrix = (cross_distances <= radius).astype(int)
        
        return recurrence_matrix, radius
    
    def calculate_crqa_measures(self, signal1, signal2, radius=None):
        """
        Calculate CRQA measures from cross-recurrence matrix.
        
        Args:
            signal1 (np.array): First time series
            signal2 (np.array): Second time series
            radius (float): Recurrence threshold
            
        Returns:
            dict: Dictionary containing CRQA measures
        """
        # Get recurrence matrix
        recurrence_matrix, used_radius = self.calculate_recurrence_matrix(
            signal1, signal2, radius
        )
        
        n_rows, n_cols = recurrence_matrix.shape
        total_points = n_rows * n_cols
        
        # Recurrence Rate (RR)
        recurrence_rate = np.sum(recurrence_matrix) / total_points
        
        # Determinism (DET) - percentage of recurrent points forming diagonal lines
        diagonal_lines = self._find_diagonal_lines(recurrence_matrix, min_length=2)
        if len(diagonal_lines) > 0:
            determinism = np.sum([line['length'] for line in diagonal_lines]) / np.sum(recurrence_matrix)
        else:
            determinism = 0.0
            
        # Average Diagonal Line Length (L)
        if len(diagonal_lines) > 0:
            avg_diagonal_length = np.mean([line['length'] for line in diagonal_lines])
        else:
            avg_diagonal_length = 0.0
            
        # Maximum Diagonal Line Length (Lmax)
        if len(diagonal_lines) > 0:
            max_diagonal_length = np.max([line['length'] for line in diagonal_lines])
        else:
            max_diagonal_length = 0.0
            
        # Laminarity (LAM) - percentage of recurrent points forming vertical lines
        vertical_lines = self._find_vertical_lines(recurrence_matrix, min_length=2)
        if len(vertical_lines) > 0:
            laminarity = np.sum([line['length'] for line in vertical_lines]) / np.sum(recurrence_matrix)
        else:
            laminarity = 0.0
            
        # Trapping Time (TT) - average vertical line length
        if len(vertical_lines) > 0:
            trapping_time = np.mean([line['length'] for line in vertical_lines])
        else:
            trapping_time = 0.0
            
        # Maximum Vertical Line Length (Vmax)
        if len(vertical_lines) > 0:
            max_vertical_length = np.max([line['length'] for line in vertical_lines])
        else:
            max_vertical_length = 0.0
            
        # Entropy (ENTR) - Shannon entropy of diagonal line lengths
        if len(diagonal_lines) > 0:
            lengths = [line['length'] for line in diagonal_lines]
            length_counts = np.bincount(lengths)
            length_probs = length_counts[length_counts > 0] / len(lengths)
            entropy = -np.sum(length_probs * np.log2(length_probs))
        else:
            entropy = 0.0
            
        return {
            'recurrence_rate': recurrence_rate,
            'determinism': determinism,
            'avg_diagonal_length': avg_diagonal_length,
            'max_diagonal_length': max_diagonal_length,
            'laminarity': laminarity,
            'trapping_time': trapping_time,
            'max_vertical_length': max_vertical_length,
            'entropy': entropy,
            'radius': used_radius,
            'recurrence_matrix': recurrence_matrix,
            'diagonal_lines': diagonal_lines,
            'vertical_lines': vertical_lines
        }
    
    def _find_diagonal_lines(self, matrix, min_length=2):
        """
        Find diagonal lines in recurrence matrix.
        
        Args:
            matrix (np.array): Binary recurrence matrix
            min_length (int): Minimum line length to consider
            
        Returns:
            list: List of diagonal lines with their properties
        """
        lines = []
        n_rows, n_cols = matrix.shape
        
        # Check all possible diagonal starting points
        for start_row in range(n_rows):
            for start_col in range(n_cols):
                if matrix[start_row, start_col] == 1:
                    # Follow diagonal from this point
                    length = 0
                    row, col = start_row, start_col
                    
                    while (row < n_rows and col < n_cols and 
                           matrix[row, col] == 1):
                        length += 1
                        row += 1
                        col += 1
                    
                    if length >= min_length:
                        lines.append({
                            'start_row': start_row,
                            'start_col': start_col,
                            'length': length
                        })
                        
                        # Mark these points as processed
                        for i in range(length):
                            if start_row + i < n_rows and start_col + i < n_cols:
                                matrix[start_row + i, start_col + i] = -1
        
        # Restore matrix
        matrix[matrix == -1] = 1
        
        return lines
    
    def _find_vertical_lines(self, matrix, min_length=2):
        """
        Find vertical lines in recurrence matrix.
        
        Args:
            matrix (np.array): Binary recurrence matrix
            min_length (int): Minimum line length to consider
            
        Returns:
            list: List of vertical lines with their properties
        """
        lines = []
        n_rows, n_cols = matrix.shape
        
        # Check all possible vertical starting points
        for start_col in range(n_cols):
            for start_row in range(n_rows):
                if matrix[start_row, start_col] == 1:
                    # Follow vertical line from this point
                    length = 0
                    row = start_row
                    
                    while row < n_rows and matrix[row, start_col] == 1:
                        length += 1
                        row += 1
                    
                    if length >= min_length:
                        lines.append({
                            'start_row': start_row,
                            'start_col': start_col,
                            'length': length
                        })
                        
                        # Mark these points as processed
                        for i in range(length):
                            if start_row + i < n_rows:
                                matrix[start_row + i, start_col] = -1
        
        # Restore matrix
        matrix[matrix == -1] = 1
        
        return lines
    
    def windowed_crqa(self, signal1, signal2, window_size, overlap=0.5, radius=None):
        """
        Calculate CRQA measures using sliding windows.
        
        Args:
            signal1 (np.array): First time series
            signal2 (np.array): Second time series
            window_size (int): Window size for analysis
            overlap (float): Overlap ratio between windows (0-1)
            radius (float): Recurrence threshold
            
        Returns:
            list: List of CRQA measures for each window
        """
        if len(signal1) != len(signal2):
            raise ValueError("Signals must have the same length")
            
        step_size = int(window_size * (1 - overlap))
        results = []
        
        for start in range(0, len(signal1) - window_size + 1, step_size):
            end = start + window_size
            window_signal1 = signal1[start:end]
            window_signal2 = signal2[start:end]
            
            try:
                crqa_measures = self.calculate_crqa_measures(
                    window_signal1, window_signal2, radius
                )
                crqa_measures['window_start'] = start
                crqa_measures['window_end'] = end
                results.append(crqa_measures)
            except Exception as e:
                warnings.warn(f"CRQA calculation failed for window {start}-{end}: {e}")
                continue
                
        return results


def demo_crqa_analysis():
    """
    Demonstration of CRQA analysis with synthetic data.
    """
    # Generate synthetic coupled signals
    t = np.linspace(0, 100, 1000)
    
    # Signal 1: Lorenz-like chaotic system
    signal1 = np.sin(0.1 * t) + 0.5 * np.sin(0.3 * t) + 0.2 * np.random.randn(len(t))
    
    # Signal 2: Coupled to signal 1 with some delay and noise
    delay = 10
    coupling_strength = 0.7
    signal2 = np.zeros_like(signal1)
    signal2[delay:] = (coupling_strength * signal1[:-delay] + 
                       (1 - coupling_strength) * np.sin(0.15 * t[delay:]) +
                       0.3 * np.random.randn(len(t) - delay))
    signal2[:delay] = np.sin(0.15 * t[:delay]) + 0.3 * np.random.randn(delay)
    
    # Initialize CRQA analyzer
    crqa = CRQAAnalyzer(embedding_dimension=3, time_delay=1, normalize=True)
    
    # Calculate CRQA measures
    results = crqa.calculate_crqa_measures(signal1, signal2)
    
    print("CRQA Analysis Results:")
    print(f"Recurrence Rate: {results['recurrence_rate']:.4f}")
    print(f"Determinism: {results['determinism']:.4f}")
    print(f"Average Diagonal Length: {results['avg_diagonal_length']:.4f}")
    print(f"Maximum Diagonal Length: {results['max_diagonal_length']:.4f}")
    print(f"Laminarity: {results['laminarity']:.4f}")
    print(f"Trapping Time: {results['trapping_time']:.4f}")
    print(f"Maximum Vertical Length: {results['max_vertical_length']:.4f}")
    print(f"Entropy: {results['entropy']:.4f}")
    print(f"Radius used: {results['radius']:.4f}")
    
    # Windowed analysis
    print("\nWindowed CRQA Analysis:")
    windowed_results = crqa.windowed_crqa(signal1, signal2, window_size=200, overlap=0.5)
    
    if windowed_results:
        avg_rr = np.mean([r['recurrence_rate'] for r in windowed_results])
        avg_det = np.mean([r['determinism'] for r in windowed_results])
        print(f"Average Recurrence Rate across windows: {avg_rr:.4f}")
        print(f"Average Determinism across windows: {avg_det:.4f}")
        print(f"Number of windows analyzed: {len(windowed_results)}")


if __name__ == "__main__":
    demo_crqa_analysis()

