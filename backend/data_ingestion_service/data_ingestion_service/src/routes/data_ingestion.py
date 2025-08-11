"""
Data Ingestion API Routes
=========================

Flask routes for real-time data ingestion from various biosignal sources.
"""

from flask import Blueprint, request, jsonify
import numpy as np
import json
from datetime import datetime
import uuid
import threading
import time
import queue
import requests
from collections import deque

data_ingestion_bp = Blueprint('data_ingestion', __name__)


class DataIngestionEngine:
    """
    Data Ingestion Engine for handling real-time biosignal data streams.
    """
    
    def __init__(self):
        self.data_streams = {}
        self.data_buffers = {}
        self.stream_configs = {}
        self.processing_threads = {}
        self.is_running = {}
        
        # Service endpoints
        self.synchrony_service_url = "http://localhost:5001/api"
        self.digital_twin_service_url = "http://localhost:5000/api"
        self.biofeedback_service_url = "http://localhost:5002/api"
        
    def create_stream(self, stream_id, config):
        """Create a new data stream."""
        if stream_id in self.data_streams:
            raise ValueError(f"Stream {stream_id} already exists")
        
        # Default configuration
        default_config = {
            'data_type': 'eeg',  # 'eeg', 'fnirs', 'ecg', 'emg', 'gsr'
            'sampling_rate': 1000,  # Hz
            'channels': ['ch1', 'ch2'],
            'buffer_size': 10000,  # samples
            'processing_window': 1000,  # samples
            'processing_overlap': 0.5,
            'auto_analysis': True,
            'analysis_methods': ['plv', 'crqa', 'fnirs'],
            'twin_id': None,
            'session_id': None
        }
        
        # Merge with provided config
        stream_config = {**default_config, **config}
        
        # Initialize stream components
        self.data_streams[stream_id] = {
            'created_at': datetime.utcnow(),
            'last_updated': datetime.utcnow(),
            'total_samples': 0,
            'status': 'created'
        }
        
        self.stream_configs[stream_id] = stream_config
        
        # Initialize data buffers for each channel
        self.data_buffers[stream_id] = {}
        for channel in stream_config['channels']:
            self.data_buffers[stream_id][channel] = deque(
                maxlen=stream_config['buffer_size']
            )
        
        self.is_running[stream_id] = False
        
        return stream_config
    
    def start_stream(self, stream_id):
        """Start data processing for a stream."""
        if stream_id not in self.data_streams:
            raise ValueError(f"Stream {stream_id} not found")
        
        if self.is_running.get(stream_id, False):
            raise ValueError(f"Stream {stream_id} is already running")
        
        self.is_running[stream_id] = True
        self.data_streams[stream_id]['status'] = 'running'
        
        # Start processing thread if auto_analysis is enabled
        if self.stream_configs[stream_id]['auto_analysis']:
            thread = threading.Thread(
                target=self._processing_loop,
                args=(stream_id,),
                daemon=True
            )
            thread.start()
            self.processing_threads[stream_id] = thread
        
        return True
    
    def stop_stream(self, stream_id):
        """Stop data processing for a stream."""
        if stream_id not in self.data_streams:
            raise ValueError(f"Stream {stream_id} not found")
        
        self.is_running[stream_id] = False
        self.data_streams[stream_id]['status'] = 'stopped'
        
        # Wait for processing thread to finish
        if stream_id in self.processing_threads:
            thread = self.processing_threads[stream_id]
            if thread.is_alive():
                thread.join(timeout=5.0)
            del self.processing_threads[stream_id]
        
        return True
    
    def ingest_data(self, stream_id, data):
        """Ingest new data into the stream."""
        if stream_id not in self.data_streams:
            raise ValueError(f"Stream {stream_id} not found")
        
        config = self.stream_configs[stream_id]
        
        # Validate data format
        if 'channels' not in data or 'samples' not in data:
            raise ValueError("Data must contain 'channels' and 'samples' fields")
        
        channels_data = data['channels']
        samples = data['samples']
        
        # Validate channels
        expected_channels = set(config['channels'])
        provided_channels = set(channels_data.keys())
        
        if not provided_channels.issubset(expected_channels):
            raise ValueError(f"Invalid channels. Expected: {expected_channels}, Got: {provided_channels}")
        
        # Add data to buffers
        for channel, channel_samples in channels_data.items():
            if channel in self.data_buffers[stream_id]:
                self.data_buffers[stream_id][channel].extend(channel_samples)
        
        # Update stream metadata
        self.data_streams[stream_id]['total_samples'] += samples
        self.data_streams[stream_id]['last_updated'] = datetime.utcnow()
        
        return {
            'stream_id': stream_id,
            'samples_ingested': samples,
            'total_samples': self.data_streams[stream_id]['total_samples'],
            'buffer_status': {
                channel: len(buffer) 
                for channel, buffer in self.data_buffers[stream_id].items()
            }
        }
    
    def get_stream_data(self, stream_id, channels=None, last_n_samples=None):
        """Get data from stream buffers."""
        if stream_id not in self.data_streams:
            raise ValueError(f"Stream {stream_id} not found")
        
        if channels is None:
            channels = self.stream_configs[stream_id]['channels']
        
        data = {}
        for channel in channels:
            if channel in self.data_buffers[stream_id]:
                buffer_data = list(self.data_buffers[stream_id][channel])
                
                if last_n_samples and len(buffer_data) > last_n_samples:
                    buffer_data = buffer_data[-last_n_samples:]
                
                data[channel] = buffer_data
        
        return data
    
    def _processing_loop(self, stream_id):
        """Background processing loop for automatic analysis."""
        config = self.stream_configs[stream_id]
        window_size = config['processing_window']
        overlap = config['processing_overlap']
        step_size = int(window_size * (1 - overlap))
        
        last_processed_sample = 0
        
        while self.is_running.get(stream_id, False):
            try:
                # Check if we have enough data for processing
                total_samples = self.data_streams[stream_id]['total_samples']
                
                if total_samples - last_processed_sample >= step_size:
                    # Get data for analysis
                    channels = config['channels']
                    
                    if len(channels) >= 2:  # Need at least 2 channels for synchrony analysis
                        data = self.get_stream_data(
                            stream_id, 
                            channels=channels[:2],  # Use first two channels
                            last_n_samples=window_size
                        )
                        
                        if (len(data.get(channels[0], [])) >= window_size and 
                            len(data.get(channels[1], [])) >= window_size):
                            
                            # Perform analysis
                            self._perform_analysis(stream_id, data, config)
                            last_processed_sample = total_samples
                
                # Sleep to avoid excessive CPU usage
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error in processing loop for stream {stream_id}: {e}")
                time.sleep(1.0)
    
    def _perform_analysis(self, stream_id, data, config):
        """Perform synchrony analysis on the data."""
        try:
            channels = list(data.keys())
            if len(channels) < 2:
                return
            
            signal1 = np.array(data[channels[0]])
            signal2 = np.array(data[channels[1]])
            
            # Prepare analysis request
            analysis_data = {
                'signal1': signal1.tolist(),
                'signal2': signal2.tolist(),
                'sampling_rate': config['sampling_rate'],
                'methods': config['analysis_methods'],
                'parameters': {
                    'plv': {'filter_band': [8, 12]},
                    'crqa': {'embedding_dimension': 3, 'normalize': True},
                    'fnirs': {'sampling_rate': config['sampling_rate']}
                }
            }
            
            # Send to synchrony analysis service
            response = requests.post(
                f"{self.synchrony_service_url}/analyze/batch",
                json=analysis_data,
                timeout=10
            )
            
            if response.status_code == 200:
                analysis_results = response.json()
                
                # Update digital twin if configured
                if config.get('twin_id'):
                    self._update_digital_twin(config['twin_id'], analysis_results)
                
                # Update biofeedback if session configured
                if config.get('session_id'):
                    self._update_biofeedback(config['session_id'], analysis_results)
                
        except Exception as e:
            print(f"Error in analysis for stream {stream_id}: {e}")
    
    def _update_digital_twin(self, twin_id, analysis_results):
        """Update digital twin with analysis results."""
        try:
            update_data = {
                'synchrony_metrics': analysis_results
            }
            
            requests.put(
                f"{self.digital_twin_service_url}/twins/{twin_id}/synchrony",
                json=update_data,
                timeout=5
            )
            
        except Exception as e:
            print(f"Error updating digital twin {twin_id}: {e}")
    
    def _update_biofeedback(self, session_id, analysis_results):
        """Update biofeedback with analysis results."""
        try:
            # Extract synchrony metrics for biofeedback
            synchrony_metrics = {}
            
            if 'plv' in analysis_results:
                synchrony_metrics['plv'] = analysis_results['plv'].get('value', 0)
            
            if 'crqa' in analysis_results:
                synchrony_metrics['crqa_determinism'] = analysis_results['crqa'].get('determinism', 0)
            
            if 'fnirs' in analysis_results:
                synchrony_metrics['fnirs_coherence'] = analysis_results['fnirs'].get('spectral_coherence', 0)
            
            update_data = {
                'synchrony_metrics': synchrony_metrics
            }
            
            requests.post(
                f"{self.biofeedback_service_url}/sessions/{session_id}/update",
                json=update_data,
                timeout=5
            )
            
        except Exception as e:
            print(f"Error updating biofeedback session {session_id}: {e}")


# Global data ingestion engine
ingestion_engine = DataIngestionEngine()


@data_ingestion_bp.route('/streams', methods=['POST'])
def create_stream():
    """
    Create a new data stream.
    
    Expected JSON payload:
    {
        "stream_id": "string",
        "config": {
            "data_type": "eeg|fnirs|ecg|emg|gsr",
            "sampling_rate": 1000,
            "channels": ["ch1", "ch2"],
            "buffer_size": 10000,
            "processing_window": 1000,
            "auto_analysis": true,
            "analysis_methods": ["plv", "crqa", "fnirs"],
            "twin_id": "string",
            "session_id": "string"
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        stream_id = data.get('stream_id')
        if not stream_id:
            stream_id = f"stream_{uuid.uuid4().hex[:8]}"
        
        config = data.get('config', {})
        
        stream_config = ingestion_engine.create_stream(stream_id, config)
        
        return jsonify({
            'message': 'Data stream created successfully',
            'stream_id': stream_id,
            'config': stream_config
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@data_ingestion_bp.route('/streams/<stream_id>/start', methods=['POST'])
def start_stream(stream_id):
    """Start data processing for a stream."""
    try:
        ingestion_engine.start_stream(stream_id)
        
        return jsonify({
            'message': 'Stream started successfully',
            'stream_id': stream_id
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@data_ingestion_bp.route('/streams/<stream_id>/stop', methods=['POST'])
def stop_stream(stream_id):
    """Stop data processing for a stream."""
    try:
        ingestion_engine.stop_stream(stream_id)
        
        return jsonify({
            'message': 'Stream stopped successfully',
            'stream_id': stream_id
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@data_ingestion_bp.route('/streams/<stream_id>/ingest', methods=['POST'])
def ingest_data(stream_id):
    """
    Ingest data into a stream.
    
    Expected JSON payload:
    {
        "channels": {
            "ch1": [sample1, sample2, ...],
            "ch2": [sample1, sample2, ...]
        },
        "samples": number_of_samples,
        "timestamp": "ISO_string" (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        result = ingestion_engine.ingest_data(stream_id, data)
        
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@data_ingestion_bp.route('/streams/<stream_id>/data', methods=['GET'])
def get_stream_data(stream_id):
    """Get data from stream buffers."""
    try:
        channels = request.args.getlist('channels')
        last_n_samples = request.args.get('last_n_samples', type=int)
        
        data = ingestion_engine.get_stream_data(
            stream_id, 
            channels=channels if channels else None,
            last_n_samples=last_n_samples
        )
        
        return jsonify({
            'stream_id': stream_id,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@data_ingestion_bp.route('/streams/<stream_id>', methods=['GET'])
def get_stream_info(stream_id):
    """Get stream information and status."""
    try:
        if stream_id not in ingestion_engine.data_streams:
            return jsonify({'error': 'Stream not found'}), 404
        
        stream_info = ingestion_engine.data_streams[stream_id].copy()
        stream_config = ingestion_engine.stream_configs[stream_id]
        
        # Add buffer status
        buffer_status = {
            channel: len(buffer)
            for channel, buffer in ingestion_engine.data_buffers[stream_id].items()
        }
        
        return jsonify({
            'stream_id': stream_id,
            'info': stream_info,
            'config': stream_config,
            'buffer_status': buffer_status,
            'is_running': ingestion_engine.is_running.get(stream_id, False)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@data_ingestion_bp.route('/streams', methods=['GET'])
def list_streams():
    """List all data streams."""
    try:
        streams = []
        
        for stream_id in ingestion_engine.data_streams:
            stream_info = ingestion_engine.data_streams[stream_id].copy()
            stream_info['stream_id'] = stream_id
            stream_info['is_running'] = ingestion_engine.is_running.get(stream_id, False)
            streams.append(stream_info)
        
        return jsonify({
            'streams': streams,
            'count': len(streams)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@data_ingestion_bp.route('/streams/<stream_id>', methods=['DELETE'])
def delete_stream(stream_id):
    """Delete a data stream."""
    try:
        if stream_id not in ingestion_engine.data_streams:
            return jsonify({'error': 'Stream not found'}), 404
        
        # Stop stream if running
        if ingestion_engine.is_running.get(stream_id, False):
            ingestion_engine.stop_stream(stream_id)
        
        # Clean up
        del ingestion_engine.data_streams[stream_id]
        del ingestion_engine.stream_configs[stream_id]
        del ingestion_engine.data_buffers[stream_id]
        
        if stream_id in ingestion_engine.is_running:
            del ingestion_engine.is_running[stream_id]
        
        return jsonify({
            'message': 'Stream deleted successfully',
            'stream_id': stream_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@data_ingestion_bp.route('/streams/<stream_id>/config', methods=['PUT'])
def update_stream_config(stream_id):
    """
    Update stream configuration.
    
    Expected JSON payload:
    {
        "config": {object}
    }
    """
    try:
        if stream_id not in ingestion_engine.data_streams:
            return jsonify({'error': 'Stream not found'}), 404
        
        data = request.get_json()
        if not data or 'config' not in data:
            return jsonify({'error': 'Config data required'}), 400
        
        # Update configuration
        ingestion_engine.stream_configs[stream_id].update(data['config'])
        
        return jsonify({
            'message': 'Configuration updated successfully',
            'stream_id': stream_id,
            'config': ingestion_engine.stream_configs[stream_id]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@data_ingestion_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    active_streams = sum(1 for running in ingestion_engine.is_running.values() if running)
    
    return jsonify({
        'status': 'healthy',
        'service': 'data_ingestion_service',
        'total_streams': len(ingestion_engine.data_streams),
        'active_streams': active_streams,
        'timestamp': datetime.utcnow().isoformat()
    }), 200

