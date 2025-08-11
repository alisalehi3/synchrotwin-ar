"""
Phase-Locking Value (PLV) Calculator
====================================

This module implements the Phase-Locking Value algorithm for measuring
phase synchrony between two neural signals.

References:
- Lachaux, J. P., Rodriguez, E., Martinerie, J., & Varela, F. J. (1999).
  Measuring phase synchrony in brain signals. Human Brain Mapping, 8(4), 194-208.
"""

import numpy as np
from scipy import signal
from scipy.signal import hilbert
import warnings


class PLVCalculator:
    """
    Phase-Locking Value calculator for neural synchrony analysis.
    
    The PLV measures the consistency of phase differences between two signals
    across time, providing a value between 0 (no synchrony) and 1 (perfect synchrony).
    """
    
    def __init__(self, sampling_rate=1000, filter_band=(8, 12)):
        """
        Initialize PLV calculator.
        
        Args:
            sampling_rate (float): Sampling rate of the signals in Hz
            filter_band (tuple): Frequency band for filtering (low, high) in Hz
        """
        self.sampling_rate = sampling_rate
        self.filter_band = filter_band
        
    def bandpass_filter(self, data, low_freq, high_freq, order=4):
        """
        Apply bandpass filter to the signal.
        
        Args:
            data (np.array): Input signal
            low_freq (float): Low cutoff frequency
            high_freq (float): High cutoff frequency
            order (int): Filter order
            
        Returns:
            np.array: Filtered signal
        """
        nyquist = self.sampling_rate / 2
        low = low_freq / nyquist
        high = high_freq / nyquist
        
        if high >= 1.0:
            high = 0.99
            warnings.warn(f"High frequency adjusted to {high * nyquist:.2f} Hz")
            
        b, a = signal.butter(order, [low, high], btype='band')
        filtered_data = signal.filtfilt(b, a, data)
        return filtered_data
    
    def extract_phase(self, signal_data):
        """
        Extract instantaneous phase from signal using Hilbert transform.
        
        Args:
            signal_data (np.array): Input signal
            
        Returns:
            np.array: Instantaneous phase
        """
        # Apply bandpass filter
        filtered_signal = self.bandpass_filter(
            signal_data, 
            self.filter_band[0], 
            self.filter_band[1]
        )
        
        # Apply Hilbert transform
        analytic_signal = hilbert(filtered_signal)
        
        # Extract phase
        phase = np.angle(analytic_signal)
        return phase
    
    def calculate_plv(self, signal1, signal2, window_size=None, overlap=0.5):
        """
        Calculate Phase-Locking Value between two signals.
        
        Args:
            signal1 (np.array): First signal
            signal2 (np.array): Second signal
            window_size (int): Window size for sliding window PLV (optional)
            overlap (float): Overlap ratio for sliding windows (0-1)
            
        Returns:
            float or np.array: PLV value(s)
        """
        if len(signal1) != len(signal2):
            raise ValueError("Signals must have the same length")
            
        # Extract phases
        phase1 = self.extract_phase(signal1)
        phase2 = self.extract_phase(signal2)
        
        if window_size is None:
            # Calculate PLV for entire signal
            phase_diff = phase1 - phase2
            plv = np.abs(np.mean(np.exp(1j * phase_diff)))
            return plv
        else:
            # Calculate sliding window PLV
            step_size = int(window_size * (1 - overlap))
            plv_values = []
            
            for start in range(0, len(phase1) - window_size + 1, step_size):
                end = start + window_size
                phase_diff_window = phase1[start:end] - phase2[start:end]
                plv_window = np.abs(np.mean(np.exp(1j * phase_diff_window)))
                plv_values.append(plv_window)
                
            return np.array(plv_values)
    
    def calculate_plv_matrix(self, signals):
        """
        Calculate PLV matrix for multiple signals.
        
        Args:
            signals (np.array): 2D array where each row is a signal
            
        Returns:
            np.array: PLV matrix (symmetric)
        """
        n_signals = signals.shape[0]
        plv_matrix = np.zeros((n_signals, n_signals))
        
        for i in range(n_signals):
            for j in range(i, n_signals):
                if i == j:
                    plv_matrix[i, j] = 1.0
                else:
                    plv = self.calculate_plv(signals[i], signals[j])
                    plv_matrix[i, j] = plv
                    plv_matrix[j, i] = plv
                    
        return plv_matrix
    
    def statistical_significance(self, signal1, signal2, n_surrogates=1000):
        """
        Test statistical significance of PLV using surrogate data.
        
        Args:
            signal1 (np.array): First signal
            signal2 (np.array): Second signal
            n_surrogates (int): Number of surrogate datasets
            
        Returns:
            dict: Results including PLV, p-value, and significance threshold
        """
        # Calculate original PLV
        original_plv = self.calculate_plv(signal1, signal2)
        
        # Generate surrogate PLV distribution
        surrogate_plvs = []
        
        for _ in range(n_surrogates):
            # Create surrogate by shuffling phase of second signal
            phase2 = self.extract_phase(signal2)
            shuffled_phase2 = np.random.permutation(phase2)
            
            # Reconstruct surrogate signal
            amplitude2 = np.abs(hilbert(signal2))
            surrogate_signal2 = amplitude2 * np.cos(shuffled_phase2)
            
            # Calculate PLV with surrogate
            surrogate_plv = self.calculate_plv(signal1, surrogate_signal2)
            surrogate_plvs.append(surrogate_plv)
        
        surrogate_plvs = np.array(surrogate_plvs)
        
        # Calculate p-value
        p_value = np.sum(surrogate_plvs >= original_plv) / n_surrogates
        
        # Calculate significance threshold (95th percentile)
        threshold_95 = np.percentile(surrogate_plvs, 95)
        
        return {
            'plv': original_plv,
            'p_value': p_value,
            'threshold_95': threshold_95,
            'is_significant': original_plv > threshold_95,
            'surrogate_distribution': surrogate_plvs
        }


def demo_plv_calculation():
    """
    Demonstration of PLV calculation with synthetic data.
    """
    # Generate synthetic signals
    fs = 1000  # Sampling rate
    t = np.linspace(0, 10, fs * 10)  # 10 seconds
    
    # Signal 1: 10 Hz oscillation
    signal1 = np.sin(2 * np.pi * 10 * t) + 0.5 * np.random.randn(len(t))
    
    # Signal 2: 10 Hz oscillation with phase lag
    phase_lag = np.pi / 4  # 45 degrees
    signal2 = np.sin(2 * np.pi * 10 * t + phase_lag) + 0.5 * np.random.randn(len(t))
    
    # Initialize PLV calculator
    plv_calc = PLVCalculator(sampling_rate=fs, filter_band=(8, 12))
    
    # Calculate PLV
    plv = plv_calc.calculate_plv(signal1, signal2)
    print(f"PLV between signals: {plv:.4f}")
    
    # Calculate sliding window PLV
    window_plv = plv_calc.calculate_plv(signal1, signal2, window_size=1000, overlap=0.5)
    print(f"Sliding window PLV (mean): {np.mean(window_plv):.4f}")
    print(f"Sliding window PLV (std): {np.std(window_plv):.4f}")
    
    # Test statistical significance
    significance_results = plv_calc.statistical_significance(signal1, signal2, n_surrogates=100)
    print(f"Statistical significance:")
    print(f"  PLV: {significance_results['plv']:.4f}")
    print(f"  p-value: {significance_results['p_value']:.4f}")
    print(f"  95% threshold: {significance_results['threshold_95']:.4f}")
    print(f"  Significant: {significance_results['is_significant']}")


if __name__ == "__main__":
    demo_plv_calculation()

