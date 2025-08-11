"""
fNIRS Coherence Analysis
========================

This module implements coherence analysis for functional Near-Infrared Spectroscopy (fNIRS)
data to measure inter-brain synchrony in dyadic interactions.

References:
- Zhang, X., Noah, J. A., Dravida, S., & Hirsch, J. (2020). Optimization of wavelet 
  coherence analysis as a measure of neural synchrony during hyperscanning using 
  functional near-infrared spectroscopy. Neurophotonics, 7(1), 015010.
"""

import numpy as np
from scipy import signal
from scipy.signal import coherence, welch
import pywt
import warnings


class fNIRSCoherenceAnalyzer:
    """
    fNIRS coherence analyzer for inter-brain synchrony measurement.
    
    Implements multiple coherence measures including spectral coherence,
    wavelet coherence, and phase coherence for fNIRS hyperscanning data.
    """
    
    def __init__(self, sampling_rate=10.0, frequency_bands=None):
        """
        Initialize fNIRS coherence analyzer.
        
        Args:
            sampling_rate (float): Sampling rate of fNIRS data in Hz
            frequency_bands (dict): Frequency bands of interest
        """
        self.sampling_rate = sampling_rate
        
        if frequency_bands is None:
            # Default frequency bands for fNIRS analysis
            self.frequency_bands = {
                'very_low': (0.01, 0.05),    # Very low frequency
                'low': (0.05, 0.1),          # Low frequency
                'medium': (0.1, 0.2),        # Medium frequency
                'high': (0.2, 0.5)           # High frequency (limited by Nyquist)
            }
        else:
            self.frequency_bands = frequency_bands
    
    def preprocess_fnirs_signal(self, signal_data, detrend=True, bandpass_filter=True):
        """
        Preprocess fNIRS signal.
        
        Args:
            signal_data (np.array): Raw fNIRS signal
            detrend (bool): Whether to detrend the signal
            bandpass_filter (bool): Whether to apply bandpass filtering
            
        Returns:
            np.array: Preprocessed signal
        """
        processed_signal = signal_data.copy()
        
        # Detrending
        if detrend:
            processed_signal = signal.detrend(processed_signal, type='linear')
        
        # Bandpass filtering (0.01-0.5 Hz for fNIRS)
        if bandpass_filter:
            nyquist = self.sampling_rate / 2
            low_freq = 0.01 / nyquist
            high_freq = min(0.5, nyquist * 0.9) / nyquist
            
            if high_freq < low_freq:
                warnings.warn("Sampling rate too low for effective bandpass filtering")
                return processed_signal
            
            b, a = signal.butter(4, [low_freq, high_freq], btype='band')
            processed_signal = signal.filtfilt(b, a, processed_signal)
        
        return processed_signal
    
    def calculate_spectral_coherence(self, signal1, signal2, nperseg=None, noverlap=None):
        """
        Calculate spectral coherence between two fNIRS signals.
        
        Args:
            signal1 (np.array): First fNIRS signal
            signal2 (np.array): Second fNIRS signal
            nperseg (int): Length of each segment for coherence calculation
            noverlap (int): Number of points to overlap between segments
            
        Returns:
            dict: Coherence results including frequencies and coherence values
        """
        # Preprocess signals
        proc_signal1 = self.preprocess_fnirs_signal(signal1)
        proc_signal2 = self.preprocess_fnirs_signal(signal2)
        
        # Set default parameters if not provided
        if nperseg is None:
            nperseg = min(len(proc_signal1) // 4, int(self.sampling_rate * 60))  # 1 minute or 1/4 signal
        
        if noverlap is None:
            noverlap = nperseg // 2
        
        # Calculate coherence
        frequencies, coherence_values = coherence(
            proc_signal1, proc_signal2,
            fs=self.sampling_rate,
            nperseg=nperseg,
            noverlap=noverlap
        )
        
        # Calculate band-specific coherence
        band_coherence = {}
        for band_name, (low_freq, high_freq) in self.frequency_bands.items():
            band_mask = (frequencies >= low_freq) & (frequencies <= high_freq)
            if np.any(band_mask):
                band_coherence[band_name] = np.mean(coherence_values[band_mask])
            else:
                band_coherence[band_name] = 0.0
        
        return {
            'frequencies': frequencies,
            'coherence': coherence_values,
            'band_coherence': band_coherence,
            'mean_coherence': np.mean(coherence_values)
        }
    
    def calculate_wavelet_coherence(self, signal1, signal2, wavelet='cmor1.5-1.0', 
                                   scales=None):
        """
        Calculate wavelet coherence between two fNIRS signals.
        
        Args:
            signal1 (np.array): First fNIRS signal
            signal2 (np.array): Second fNIRS signal
            wavelet (str): Wavelet to use for analysis
            scales (np.array): Scales for wavelet transform
            
        Returns:
            dict: Wavelet coherence results
        """
        # Preprocess signals
        proc_signal1 = self.preprocess_fnirs_signal(signal1)
        proc_signal2 = self.preprocess_fnirs_signal(signal2)
        
        # Set default scales if not provided
        if scales is None:
            # Create scales corresponding to frequencies of interest (0.01-0.5 Hz)
            frequencies = np.logspace(np.log10(0.01), np.log10(0.5), 50)
            scales = pywt.frequency2scale(wavelet, frequencies) / self.sampling_rate
        
        # Continuous wavelet transform
        cwt1, _ = pywt.cwt(proc_signal1, scales, wavelet, sampling_period=1/self.sampling_rate)
        cwt2, _ = pywt.cwt(proc_signal2, scales, wavelet, sampling_period=1/self.sampling_rate)
        
        # Calculate cross-wavelet spectrum
        cross_spectrum = cwt1 * np.conj(cwt2)
        
        # Calculate auto-spectra
        auto_spectrum1 = np.abs(cwt1) ** 2
        auto_spectrum2 = np.abs(cwt2) ** 2
        
        # Calculate wavelet coherence
        # Smooth the spectra (simple moving average)
        smooth_window = 5
        smoothed_cross = np.zeros_like(cross_spectrum)
        smoothed_auto1 = np.zeros_like(auto_spectrum1)
        smoothed_auto2 = np.zeros_like(auto_spectrum2)
        
        for i in range(len(scales)):
            for j in range(len(proc_signal1)):
                start_idx = max(0, j - smooth_window // 2)
                end_idx = min(len(proc_signal1), j + smooth_window // 2 + 1)
                
                smoothed_cross[i, j] = np.mean(cross_spectrum[i, start_idx:end_idx])
                smoothed_auto1[i, j] = np.mean(auto_spectrum1[i, start_idx:end_idx])
                smoothed_auto2[i, j] = np.mean(auto_spectrum2[i, start_idx:end_idx])
        
        # Wavelet coherence
        wavelet_coherence = np.abs(smoothed_cross) ** 2 / (smoothed_auto1 * smoothed_auto2)
        
        # Convert scales to frequencies
        frequencies = pywt.scale2frequency(wavelet, scales) * self.sampling_rate
        
        # Calculate band-specific coherence
        band_coherence = {}
        for band_name, (low_freq, high_freq) in self.frequency_bands.items():
            band_mask = (frequencies >= low_freq) & (frequencies <= high_freq)
            if np.any(band_mask):
                band_coherence[band_name] = np.mean(wavelet_coherence[band_mask, :])
            else:
                band_coherence[band_name] = 0.0
        
        return {
            'wavelet_coherence': wavelet_coherence,
            'frequencies': frequencies,
            'scales': scales,
            'band_coherence': band_coherence,
            'cross_spectrum': cross_spectrum,
            'mean_coherence': np.mean(wavelet_coherence)
        }
    
    def calculate_phase_coherence(self, signal1, signal2, method='hilbert'):
        """
        Calculate phase coherence between two fNIRS signals.
        
        Args:
            signal1 (np.array): First fNIRS signal
            signal2 (np.array): Second fNIRS signal
            method (str): Method for phase extraction ('hilbert' or 'wavelet')
            
        Returns:
            dict: Phase coherence results
        """
        # Preprocess signals
        proc_signal1 = self.preprocess_fnirs_signal(signal1)
        proc_signal2 = self.preprocess_fnirs_signal(signal2)
        
        if method == 'hilbert':
            # Extract phases using Hilbert transform
            analytic1 = signal.hilbert(proc_signal1)
            analytic2 = signal.hilbert(proc_signal2)
            
            phase1 = np.angle(analytic1)
            phase2 = np.angle(analytic2)
            
            # Calculate phase difference
            phase_diff = phase1 - phase2
            
            # Phase coherence (similar to PLV)
            phase_coherence = np.abs(np.mean(np.exp(1j * phase_diff)))
            
            return {
                'phase_coherence': phase_coherence,
                'phase1': phase1,
                'phase2': phase2,
                'phase_difference': phase_diff,
                'method': 'hilbert'
            }
        
        elif method == 'wavelet':
            # Use wavelet-based phase extraction
            wavelet_result = self.calculate_wavelet_coherence(signal1, signal2)
            
            # Extract phase from cross-spectrum
            cross_spectrum = wavelet_result['cross_spectrum']
            phase_diff = np.angle(cross_spectrum)
            
            # Calculate phase coherence across frequencies and time
            phase_coherence = np.abs(np.mean(np.exp(1j * phase_diff)))
            
            return {
                'phase_coherence': phase_coherence,
                'phase_difference': phase_diff,
                'frequencies': wavelet_result['frequencies'],
                'method': 'wavelet'
            }
    
    def calculate_hyperscanning_metrics(self, participant1_channels, participant2_channels):
        """
        Calculate comprehensive hyperscanning metrics for multi-channel fNIRS data.
        
        Args:
            participant1_channels (np.array): fNIRS data for participant 1 (channels x time)
            participant2_channels (np.array): fNIRS data for participant 2 (channels x time)
            
        Returns:
            dict: Comprehensive hyperscanning metrics
        """
        n_channels1, n_timepoints1 = participant1_channels.shape
        n_channels2, n_timepoints2 = participant2_channels.shape
        
        if n_timepoints1 != n_timepoints2:
            raise ValueError("Participants must have the same number of time points")
        
        # Calculate inter-brain coherence matrix
        inter_brain_coherence = np.zeros((n_channels1, n_channels2))
        inter_brain_phase_coherence = np.zeros((n_channels1, n_channels2))
        
        for i in range(n_channels1):
            for j in range(n_channels2):
                # Spectral coherence
                coherence_result = self.calculate_spectral_coherence(
                    participant1_channels[i, :],
                    participant2_channels[j, :]
                )
                inter_brain_coherence[i, j] = coherence_result['mean_coherence']
                
                # Phase coherence
                phase_result = self.calculate_phase_coherence(
                    participant1_channels[i, :],
                    participant2_channels[j, :]
                )
                inter_brain_phase_coherence[i, j] = phase_result['phase_coherence']
        
        # Calculate intra-brain coherence for comparison
        intra_brain_coherence1 = self._calculate_intra_brain_coherence(participant1_channels)
        intra_brain_coherence2 = self._calculate_intra_brain_coherence(participant2_channels)
        
        # Summary statistics
        mean_inter_brain_coherence = np.mean(inter_brain_coherence)
        max_inter_brain_coherence = np.max(inter_brain_coherence)
        mean_intra_brain_coherence = (np.mean(intra_brain_coherence1) + 
                                     np.mean(intra_brain_coherence2)) / 2
        
        # Synchrony index (inter-brain vs intra-brain coherence ratio)
        synchrony_index = mean_inter_brain_coherence / mean_intra_brain_coherence if mean_intra_brain_coherence > 0 else 0
        
        return {
            'inter_brain_coherence_matrix': inter_brain_coherence,
            'inter_brain_phase_coherence_matrix': inter_brain_phase_coherence,
            'intra_brain_coherence_p1': intra_brain_coherence1,
            'intra_brain_coherence_p2': intra_brain_coherence2,
            'mean_inter_brain_coherence': mean_inter_brain_coherence,
            'max_inter_brain_coherence': max_inter_brain_coherence,
            'mean_intra_brain_coherence': mean_intra_brain_coherence,
            'synchrony_index': synchrony_index,
            'n_channels_p1': n_channels1,
            'n_channels_p2': n_channels2
        }
    
    def _calculate_intra_brain_coherence(self, channels):
        """
        Calculate intra-brain coherence matrix for a single participant.
        
        Args:
            channels (np.array): Multi-channel fNIRS data (channels x time)
            
        Returns:
            np.array: Intra-brain coherence matrix
        """
        n_channels = channels.shape[0]
        coherence_matrix = np.zeros((n_channels, n_channels))
        
        for i in range(n_channels):
            for j in range(i, n_channels):
                if i == j:
                    coherence_matrix[i, j] = 1.0
                else:
                    coherence_result = self.calculate_spectral_coherence(
                        channels[i, :], channels[j, :]
                    )
                    coherence_value = coherence_result['mean_coherence']
                    coherence_matrix[i, j] = coherence_value
                    coherence_matrix[j, i] = coherence_value
        
        return coherence_matrix


def demo_fnirs_coherence():
    """
    Demonstration of fNIRS coherence analysis with synthetic data.
    """
    # Generate synthetic fNIRS signals
    fs = 10.0  # 10 Hz sampling rate (typical for fNIRS)
    duration = 300  # 5 minutes
    t = np.linspace(0, duration, int(fs * duration))
    
    # Participant 1 signal (with slow oscillations typical of fNIRS)
    signal1 = (0.5 * np.sin(2 * np.pi * 0.05 * t) +  # 0.05 Hz oscillation
               0.3 * np.sin(2 * np.pi * 0.1 * t) +   # 0.1 Hz oscillation
               0.2 * np.random.randn(len(t)))        # Noise
    
    # Participant 2 signal (coupled to participant 1)
    coupling_delay = int(2 * fs)  # 2-second delay
    coupling_strength = 0.6
    signal2 = np.zeros_like(signal1)
    signal2[coupling_delay:] = (coupling_strength * signal1[:-coupling_delay] +
                               (1 - coupling_strength) * (
                                   0.4 * np.sin(2 * np.pi * 0.08 * t[coupling_delay:]) +
                                   0.3 * np.random.randn(len(t) - coupling_delay)
                               ))
    signal2[:coupling_delay] = 0.3 * np.random.randn(coupling_delay)
    
    # Initialize analyzer
    analyzer = fNIRSCoherenceAnalyzer(sampling_rate=fs)
    
    # Calculate spectral coherence
    spectral_result = analyzer.calculate_spectral_coherence(signal1, signal2)
    print("Spectral Coherence Analysis:")
    print(f"Mean coherence: {spectral_result['mean_coherence']:.4f}")
    print("Band-specific coherence:")
    for band, value in spectral_result['band_coherence'].items():
        print(f"  {band}: {value:.4f}")
    
    # Calculate phase coherence
    phase_result = analyzer.calculate_phase_coherence(signal1, signal2)
    print(f"\nPhase coherence: {phase_result['phase_coherence']:.4f}")
    
    # Calculate wavelet coherence
    wavelet_result = analyzer.calculate_wavelet_coherence(signal1, signal2)
    print(f"Wavelet coherence (mean): {wavelet_result['mean_coherence']:.4f}")
    
    # Multi-channel example
    print("\nMulti-channel Hyperscanning Analysis:")
    
    # Simulate multi-channel data
    n_channels = 4
    participant1_data = np.array([signal1 + 0.1 * np.random.randn(len(signal1)) 
                                 for _ in range(n_channels)])
    participant2_data = np.array([signal2 + 0.1 * np.random.randn(len(signal2)) 
                                 for _ in range(n_channels)])
    
    hyperscanning_result = analyzer.calculate_hyperscanning_metrics(
        participant1_data, participant2_data
    )
    
    print(f"Mean inter-brain coherence: {hyperscanning_result['mean_inter_brain_coherence']:.4f}")
    print(f"Mean intra-brain coherence: {hyperscanning_result['mean_intra_brain_coherence']:.4f}")
    print(f"Synchrony index: {hyperscanning_result['synchrony_index']:.4f}")


if __name__ == "__main__":
    demo_fnirs_coherence()

