"""
Synchrony Analysis API Routes
=============================

Flask routes for real-time synchrony analysis using PLV, CRQA, and fNIRS coherence.
"""

from flask import Blueprint, request, jsonify
import numpy as np
import json
from datetime import datetime
import traceback

# Import our algorithm modules
from src.plv_calculator import PLVCalculator
from src.crqa_analyzer import CRQAAnalyzer
from src.fnirs_coherence import fNIRSCoherenceAnalyzer

synchrony_bp = Blueprint('synchrony', __name__)


@synchrony_bp.route('/analyze/plv', methods=['POST'])
def analyze_plv():
    """
    Calculate Phase-Locking Value between two signals.
    
    Expected JSON payload:
    {
        "signal1": [array of numbers],
        "signal2": [array of numbers],
        "sampling_rate": float,
        "filter_band": [low_freq, high_freq],
        "window_size": int (optional),
        "overlap": float (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Extract signals
        signal1 = np.array(data.get('signal1', []))
        signal2 = np.array(data.get('signal2', []))
        
        if len(signal1) == 0 or len(signal2) == 0:
            return jsonify({'error': 'Both signals must be provided'}), 400
        
        if len(signal1) != len(signal2):
            return jsonify({'error': 'Signals must have the same length'}), 400
        
        # Extract parameters
        sampling_rate = data.get('sampling_rate', 1000)
        filter_band = data.get('filter_band', [8, 12])
        window_size = data.get('window_size')
        overlap = data.get('overlap', 0.5)
        
        # Initialize PLV calculator
        plv_calc = PLVCalculator(
            sampling_rate=sampling_rate,
            filter_band=tuple(filter_band)
        )
        
        # Calculate PLV
        if window_size:
            plv_values = plv_calc.calculate_plv(
                signal1, signal2, 
                window_size=window_size, 
                overlap=overlap
            )
            result = {
                'plv_values': plv_values.tolist(),
                'mean_plv': float(np.mean(plv_values)),
                'std_plv': float(np.std(plv_values)),
                'windowed': True,
                'window_size': window_size,
                'overlap': overlap
            }
        else:
            plv = plv_calc.calculate_plv(signal1, signal2)
            result = {
                'plv': float(plv),
                'windowed': False
            }
        
        result.update({
            'sampling_rate': sampling_rate,
            'filter_band': filter_band,
            'signal_length': len(signal1),
            'timestamp': datetime.utcnow().isoformat()
        })
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@synchrony_bp.route('/analyze/crqa', methods=['POST'])
def analyze_crqa():
    """
    Perform Cross-Recurrence Quantification Analysis.
    
    Expected JSON payload:
    {
        "signal1": [array of numbers],
        "signal2": [array of numbers],
        "embedding_dimension": int,
        "time_delay": int,
        "radius": float (optional),
        "normalize": bool,
        "windowed": bool,
        "window_size": int (if windowed),
        "overlap": float (if windowed)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Extract signals
        signal1 = np.array(data.get('signal1', []))
        signal2 = np.array(data.get('signal2', []))
        
        if len(signal1) == 0 or len(signal2) == 0:
            return jsonify({'error': 'Both signals must be provided'}), 400
        
        # Extract parameters
        embedding_dimension = data.get('embedding_dimension', 3)
        time_delay = data.get('time_delay', 1)
        radius = data.get('radius')
        normalize = data.get('normalize', True)
        windowed = data.get('windowed', False)
        window_size = data.get('window_size', 200)
        overlap = data.get('overlap', 0.5)
        
        # Initialize CRQA analyzer
        crqa = CRQAAnalyzer(
            embedding_dimension=embedding_dimension,
            time_delay=time_delay,
            radius=radius,
            normalize=normalize
        )
        
        if windowed:
            # Windowed analysis
            results = crqa.windowed_crqa(
                signal1, signal2,
                window_size=window_size,
                overlap=overlap,
                radius=radius
            )
            
            if not results:
                return jsonify({'error': 'No valid windows for analysis'}), 400
            
            # Aggregate results
            aggregated = {
                'mean_recurrence_rate': float(np.mean([r['recurrence_rate'] for r in results])),
                'mean_determinism': float(np.mean([r['determinism'] for r in results])),
                'mean_avg_diagonal_length': float(np.mean([r['avg_diagonal_length'] for r in results])),
                'mean_laminarity': float(np.mean([r['laminarity'] for r in results])),
                'mean_trapping_time': float(np.mean([r['trapping_time'] for r in results])),
                'mean_entropy': float(np.mean([r['entropy'] for r in results])),
                'window_results': results,
                'num_windows': len(results),
                'windowed': True
            }
            
        else:
            # Single analysis
            crqa_results = crqa.calculate_crqa_measures(signal1, signal2, radius)
            
            # Convert numpy arrays to lists for JSON serialization
            aggregated = {
                'recurrence_rate': float(crqa_results['recurrence_rate']),
                'determinism': float(crqa_results['determinism']),
                'avg_diagonal_length': float(crqa_results['avg_diagonal_length']),
                'max_diagonal_length': float(crqa_results['max_diagonal_length']),
                'laminarity': float(crqa_results['laminarity']),
                'trapping_time': float(crqa_results['trapping_time']),
                'max_vertical_length': float(crqa_results['max_vertical_length']),
                'entropy': float(crqa_results['entropy']),
                'radius': float(crqa_results['radius']),
                'windowed': False
            }
        
        aggregated.update({
            'embedding_dimension': embedding_dimension,
            'time_delay': time_delay,
            'normalize': normalize,
            'signal_length': len(signal1),
            'timestamp': datetime.utcnow().isoformat()
        })
        
        return jsonify(aggregated), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@synchrony_bp.route('/analyze/fnirs', methods=['POST'])
def analyze_fnirs():
    """
    Perform fNIRS coherence analysis.
    
    Expected JSON payload:
    {
        "signal1": [array of numbers],
        "signal2": [array of numbers],
        "sampling_rate": float,
        "analysis_type": "spectral" | "wavelet" | "phase" | "all",
        "frequency_bands": {object} (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Extract signals
        signal1 = np.array(data.get('signal1', []))
        signal2 = np.array(data.get('signal2', []))
        
        if len(signal1) == 0 or len(signal2) == 0:
            return jsonify({'error': 'Both signals must be provided'}), 400
        
        if len(signal1) != len(signal2):
            return jsonify({'error': 'Signals must have the same length'}), 400
        
        # Extract parameters
        sampling_rate = data.get('sampling_rate', 10.0)
        analysis_type = data.get('analysis_type', 'all')
        frequency_bands = data.get('frequency_bands')
        
        # Initialize fNIRS analyzer
        analyzer = fNIRSCoherenceAnalyzer(
            sampling_rate=sampling_rate,
            frequency_bands=frequency_bands
        )
        
        results = {
            'sampling_rate': sampling_rate,
            'signal_length': len(signal1),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if analysis_type in ['spectral', 'all']:
            spectral_result = analyzer.calculate_spectral_coherence(signal1, signal2)
            results['spectral_coherence'] = {
                'mean_coherence': float(spectral_result['mean_coherence']),
                'band_coherence': {k: float(v) for k, v in spectral_result['band_coherence'].items()},
                'frequencies': spectral_result['frequencies'].tolist(),
                'coherence_values': spectral_result['coherence'].tolist()
            }
        
        if analysis_type in ['phase', 'all']:
            phase_result = analyzer.calculate_phase_coherence(signal1, signal2)
            results['phase_coherence'] = {
                'phase_coherence': float(phase_result['phase_coherence']),
                'method': phase_result['method']
            }
        
        if analysis_type in ['wavelet', 'all']:
            try:
                wavelet_result = analyzer.calculate_wavelet_coherence(signal1, signal2)
                results['wavelet_coherence'] = {
                    'mean_coherence': float(wavelet_result['mean_coherence']),
                    'band_coherence': {k: float(v) for k, v in wavelet_result['band_coherence'].items()},
                    'frequencies': wavelet_result['frequencies'].tolist()
                }
            except Exception as e:
                results['wavelet_coherence'] = {
                    'error': f'Wavelet analysis failed: {str(e)}'
                }
        
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@synchrony_bp.route('/analyze/multi-channel', methods=['POST'])
def analyze_multi_channel():
    """
    Perform multi-channel hyperscanning analysis.
    
    Expected JSON payload:
    {
        "participant1_channels": [[signal1], [signal2], ...],
        "participant2_channels": [[signal1], [signal2], ...],
        "sampling_rate": float,
        "analysis_methods": ["plv", "fnirs"] (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Extract channel data
        p1_channels = np.array(data.get('participant1_channels', []))
        p2_channels = np.array(data.get('participant2_channels', []))
        
        if p1_channels.size == 0 or p2_channels.size == 0:
            return jsonify({'error': 'Both participants channel data must be provided'}), 400
        
        sampling_rate = data.get('sampling_rate', 10.0)
        analysis_methods = data.get('analysis_methods', ['fnirs'])
        
        results = {
            'sampling_rate': sampling_rate,
            'participant1_channels': p1_channels.shape[0],
            'participant2_channels': p2_channels.shape[0],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if 'fnirs' in analysis_methods:
            # fNIRS hyperscanning analysis
            analyzer = fNIRSCoherenceAnalyzer(sampling_rate=sampling_rate)
            hyperscanning_result = analyzer.calculate_hyperscanning_metrics(
                p1_channels, p2_channels
            )
            
            results['fnirs_hyperscanning'] = {
                'mean_inter_brain_coherence': float(hyperscanning_result['mean_inter_brain_coherence']),
                'max_inter_brain_coherence': float(hyperscanning_result['max_inter_brain_coherence']),
                'mean_intra_brain_coherence': float(hyperscanning_result['mean_intra_brain_coherence']),
                'synchrony_index': float(hyperscanning_result['synchrony_index']),
                'inter_brain_coherence_matrix': hyperscanning_result['inter_brain_coherence_matrix'].tolist(),
                'inter_brain_phase_coherence_matrix': hyperscanning_result['inter_brain_phase_coherence_matrix'].tolist()
            }
        
        if 'plv' in analysis_methods:
            # PLV analysis between all channel pairs
            plv_calc = PLVCalculator(sampling_rate=sampling_rate)
            
            inter_brain_plv = np.zeros((p1_channels.shape[0], p2_channels.shape[0]))
            
            for i in range(p1_channels.shape[0]):
                for j in range(p2_channels.shape[0]):
                    plv = plv_calc.calculate_plv(p1_channels[i], p2_channels[j])
                    inter_brain_plv[i, j] = plv
            
            results['plv_analysis'] = {
                'inter_brain_plv_matrix': inter_brain_plv.tolist(),
                'mean_inter_brain_plv': float(np.mean(inter_brain_plv)),
                'max_inter_brain_plv': float(np.max(inter_brain_plv))
            }
        
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@synchrony_bp.route('/analyze/batch', methods=['POST'])
def analyze_batch():
    """
    Perform batch analysis with multiple methods.
    
    Expected JSON payload:
    {
        "signal1": [array of numbers],
        "signal2": [array of numbers],
        "sampling_rate": float,
        "methods": ["plv", "crqa", "fnirs"],
        "parameters": {
            "plv": {object},
            "crqa": {object},
            "fnirs": {object}
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Extract signals
        signal1 = np.array(data.get('signal1', []))
        signal2 = np.array(data.get('signal2', []))
        
        if len(signal1) == 0 or len(signal2) == 0:
            return jsonify({'error': 'Both signals must be provided'}), 400
        
        if len(signal1) != len(signal2):
            return jsonify({'error': 'Signals must have the same length'}), 400
        
        sampling_rate = data.get('sampling_rate', 1000)
        methods = data.get('methods', ['plv', 'crqa', 'fnirs'])
        parameters = data.get('parameters', {})
        
        results = {
            'sampling_rate': sampling_rate,
            'signal_length': len(signal1),
            'methods_analyzed': methods,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # PLV Analysis
        if 'plv' in methods:
            try:
                plv_params = parameters.get('plv', {})
                plv_calc = PLVCalculator(
                    sampling_rate=sampling_rate,
                    filter_band=tuple(plv_params.get('filter_band', [8, 12]))
                )
                plv = plv_calc.calculate_plv(signal1, signal2)
                results['plv'] = {
                    'value': float(plv),
                    'filter_band': plv_params.get('filter_band', [8, 12])
                }
            except Exception as e:
                results['plv'] = {'error': str(e)}
        
        # CRQA Analysis
        if 'crqa' in methods:
            try:
                crqa_params = parameters.get('crqa', {})
                crqa = CRQAAnalyzer(
                    embedding_dimension=crqa_params.get('embedding_dimension', 3),
                    time_delay=crqa_params.get('time_delay', 1),
                    normalize=crqa_params.get('normalize', True)
                )
                crqa_results = crqa.calculate_crqa_measures(signal1, signal2)
                results['crqa'] = {
                    'recurrence_rate': float(crqa_results['recurrence_rate']),
                    'determinism': float(crqa_results['determinism']),
                    'avg_diagonal_length': float(crqa_results['avg_diagonal_length']),
                    'laminarity': float(crqa_results['laminarity']),
                    'entropy': float(crqa_results['entropy'])
                }
            except Exception as e:
                results['crqa'] = {'error': str(e)}
        
        # fNIRS Analysis
        if 'fnirs' in methods:
            try:
                fnirs_params = parameters.get('fnirs', {})
                analyzer = fNIRSCoherenceAnalyzer(
                    sampling_rate=fnirs_params.get('sampling_rate', sampling_rate)
                )
                
                spectral_result = analyzer.calculate_spectral_coherence(signal1, signal2)
                phase_result = analyzer.calculate_phase_coherence(signal1, signal2)
                
                results['fnirs'] = {
                    'spectral_coherence': float(spectral_result['mean_coherence']),
                    'phase_coherence': float(phase_result['phase_coherence']),
                    'band_coherence': {k: float(v) for k, v in spectral_result['band_coherence'].items()}
                }
            except Exception as e:
                results['fnirs'] = {'error': str(e)}
        
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@synchrony_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'synchrony_analysis_service',
        'available_methods': ['plv', 'crqa', 'fnirs', 'multi-channel', 'batch'],
        'timestamp': datetime.utcnow().isoformat()
    }), 200

