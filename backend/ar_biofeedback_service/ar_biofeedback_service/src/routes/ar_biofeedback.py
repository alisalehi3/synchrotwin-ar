"""
AR Biofeedback API Routes
=========================

Flask routes for managing AR biofeedback visual cues and real-time feedback.
"""

from flask import Blueprint, request, jsonify
import numpy as np
import json
from datetime import datetime
import uuid
import math

ar_biofeedback_bp = Blueprint('ar_biofeedback', __name__)


class ARBiofeedbackEngine:
    """
    AR Biofeedback Engine for generating visual cues based on synchrony metrics.
    """
    
    def __init__(self):
        self.feedback_sessions = {}
        
    def create_session(self, session_id, config=None):
        """Create a new biofeedback session."""
        if config is None:
            config = self.get_default_config()
            
        self.feedback_sessions[session_id] = {
            'config': config,
            'current_state': self.get_initial_state(),
            'history': [],
            'created_at': datetime.utcnow(),
            'last_updated': datetime.utcnow()
        }
        
        return self.feedback_sessions[session_id]
    
    def get_default_config(self):
        """Get default biofeedback configuration."""
        return {
            'visual_cues': {
                'enabled': True,
                'type': 'particle_system',  # 'particle_system', 'geometric_shapes', 'color_gradients'
                'intensity_mapping': 'linear',  # 'linear', 'exponential', 'threshold'
                'color_scheme': 'blue_to_red',  # 'blue_to_red', 'green_to_red', 'rainbow'
                'size_scaling': True,
                'opacity_scaling': True,
                'animation_speed': 1.0
            },
            'audio_feedback': {
                'enabled': False,
                'type': 'binaural_beats',  # 'binaural_beats', 'harmonic_tones', 'nature_sounds'
                'frequency_range': [40, 100],  # Hz
                'volume_scaling': True
            },
            'haptic_feedback': {
                'enabled': False,
                'type': 'vibration_patterns',  # 'vibration_patterns', 'temperature_changes'
                'intensity_scaling': True
            },
            'synchrony_thresholds': {
                'low': 0.3,
                'medium': 0.6,
                'high': 0.8
            },
            'update_frequency': 10  # Hz
        }
    
    def get_initial_state(self):
        """Get initial biofeedback state."""
        return {
            'visual_elements': [],
            'audio_state': {
                'playing': False,
                'frequency': 0,
                'volume': 0
            },
            'haptic_state': {
                'active': False,
                'intensity': 0,
                'pattern': 'none'
            },
            'synchrony_level': 'low',
            'last_synchrony_value': 0.0
        }
    
    def update_feedback(self, session_id, synchrony_metrics):
        """Update biofeedback based on synchrony metrics."""
        if session_id not in self.feedback_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.feedback_sessions[session_id]
        config = session['config']
        
        # Extract primary synchrony value
        primary_synchrony = self._extract_primary_synchrony(synchrony_metrics)
        
        # Update visual feedback
        visual_elements = self._generate_visual_feedback(primary_synchrony, config)
        
        # Update audio feedback
        audio_state = self._generate_audio_feedback(primary_synchrony, config)
        
        # Update haptic feedback
        haptic_state = self._generate_haptic_feedback(primary_synchrony, config)
        
        # Determine synchrony level
        synchrony_level = self._determine_synchrony_level(primary_synchrony, config)
        
        # Update session state
        new_state = {
            'visual_elements': visual_elements,
            'audio_state': audio_state,
            'haptic_state': haptic_state,
            'synchrony_level': synchrony_level,
            'last_synchrony_value': primary_synchrony,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        session['current_state'] = new_state
        session['last_updated'] = datetime.utcnow()
        
        # Add to history
        session['history'].append({
            'timestamp': datetime.utcnow().isoformat(),
            'synchrony_metrics': synchrony_metrics,
            'feedback_state': new_state.copy()
        })
        
        # Keep only last 100 history entries
        if len(session['history']) > 100:
            session['history'] = session['history'][-100:]
        
        return new_state
    
    def _extract_primary_synchrony(self, synchrony_metrics):
        """Extract primary synchrony value from metrics."""
        # Priority order: PLV > fNIRS coherence > CRQA determinism
        if 'plv' in synchrony_metrics:
            return float(synchrony_metrics['plv'])
        elif 'fnirs_coherence' in synchrony_metrics:
            return float(synchrony_metrics['fnirs_coherence'])
        elif 'crqa_determinism' in synchrony_metrics:
            return float(synchrony_metrics['crqa_determinism'])
        elif 'mean_coherence' in synchrony_metrics:
            return float(synchrony_metrics['mean_coherence'])
        else:
            return 0.0
    
    def _generate_visual_feedback(self, synchrony_value, config):
        """Generate visual feedback elements."""
        if not config['visual_cues']['enabled']:
            return []
        
        visual_type = config['visual_cues']['type']
        
        if visual_type == 'particle_system':
            return self._generate_particle_system(synchrony_value, config)
        elif visual_type == 'geometric_shapes':
            return self._generate_geometric_shapes(synchrony_value, config)
        elif visual_type == 'color_gradients':
            return self._generate_color_gradients(synchrony_value, config)
        else:
            return []
    
    def _generate_particle_system(self, synchrony_value, config):
        """Generate particle system visual feedback."""
        num_particles = int(10 + synchrony_value * 50)  # 10-60 particles
        
        particles = []
        for i in range(num_particles):
            # Random position in normalized space
            x = np.random.uniform(-1, 1)
            y = np.random.uniform(-1, 1)
            z = np.random.uniform(0, 2)
            
            # Size based on synchrony
            size = 0.1 + synchrony_value * 0.5
            
            # Color based on synchrony and color scheme
            color = self._get_color_for_synchrony(synchrony_value, config['visual_cues']['color_scheme'])
            
            # Opacity based on synchrony
            opacity = 0.3 + synchrony_value * 0.7
            
            # Animation properties
            velocity = {
                'x': np.random.uniform(-0.1, 0.1),
                'y': np.random.uniform(-0.1, 0.1),
                'z': np.random.uniform(-0.05, 0.05)
            }
            
            particles.append({
                'id': f'particle_{i}',
                'type': 'sphere',
                'position': {'x': x, 'y': y, 'z': z},
                'size': size,
                'color': color,
                'opacity': opacity,
                'velocity': velocity,
                'lifetime': 5.0  # seconds
            })
        
        return particles
    
    def _generate_geometric_shapes(self, synchrony_value, config):
        """Generate geometric shapes visual feedback."""
        shapes = []
        
        # Central shape that changes based on synchrony
        central_shape = {
            'id': 'central_shape',
            'type': 'torus',  # Changes complexity with synchrony
            'position': {'x': 0, 'y': 0, 'z': 1},
            'size': 0.5 + synchrony_value * 0.5,
            'color': self._get_color_for_synchrony(synchrony_value, config['visual_cues']['color_scheme']),
            'opacity': 0.7,
            'rotation': {
                'x': 0,
                'y': synchrony_value * 360,  # Rotation speed based on synchrony
                'z': 0
            },
            'animation': {
                'rotation_speed': synchrony_value * 2.0,
                'pulsing': True,
                'pulse_frequency': synchrony_value * 2.0
            }
        }
        
        shapes.append(central_shape)
        
        # Surrounding shapes for high synchrony
        if synchrony_value > 0.5:
            num_surrounding = int((synchrony_value - 0.5) * 12)  # 0-6 shapes
            for i in range(num_surrounding):
                angle = (i / num_surrounding) * 2 * math.pi
                radius = 1.5
                
                surrounding_shape = {
                    'id': f'surrounding_{i}',
                    'type': 'cube',
                    'position': {
                        'x': radius * math.cos(angle),
                        'y': radius * math.sin(angle),
                        'z': 1
                    },
                    'size': 0.2,
                    'color': self._get_color_for_synchrony(synchrony_value * 0.8, config['visual_cues']['color_scheme']),
                    'opacity': 0.5,
                    'animation': {
                        'orbit_speed': synchrony_value,
                        'orbit_radius': radius
                    }
                }
                
                shapes.append(surrounding_shape)
        
        return shapes
    
    def _generate_color_gradients(self, synchrony_value, config):
        """Generate color gradient visual feedback."""
        gradients = []
        
        # Background gradient
        gradient = {
            'id': 'background_gradient',
            'type': 'plane',
            'position': {'x': 0, 'y': 0, 'z': 0.5},
            'size': {'width': 4, 'height': 3},
            'gradient': {
                'type': 'radial',
                'center_color': self._get_color_for_synchrony(synchrony_value, config['visual_cues']['color_scheme']),
                'edge_color': self._get_color_for_synchrony(synchrony_value * 0.3, config['visual_cues']['color_scheme']),
                'intensity': synchrony_value
            },
            'opacity': 0.4 + synchrony_value * 0.4,
            'animation': {
                'pulse_frequency': synchrony_value * 1.5,
                'color_shift_speed': synchrony_value * 0.5
            }
        }
        
        gradients.append(gradient)
        
        return gradients
    
    def _get_color_for_synchrony(self, synchrony_value, color_scheme):
        """Get color based on synchrony value and color scheme."""
        if color_scheme == 'blue_to_red':
            r = int(synchrony_value * 255)
            g = 0
            b = int((1 - synchrony_value) * 255)
        elif color_scheme == 'green_to_red':
            r = int(synchrony_value * 255)
            g = int((1 - synchrony_value) * 255)
            b = 0
        elif color_scheme == 'rainbow':
            # HSV to RGB conversion for rainbow effect
            hue = synchrony_value * 300  # 0-300 degrees (blue to red)
            saturation = 1.0
            value = 1.0
            
            c = value * saturation
            x = c * (1 - abs((hue / 60) % 2 - 1))
            m = value - c
            
            if 0 <= hue < 60:
                r, g, b = c, x, 0
            elif 60 <= hue < 120:
                r, g, b = x, c, 0
            elif 120 <= hue < 180:
                r, g, b = 0, c, x
            elif 180 <= hue < 240:
                r, g, b = 0, x, c
            elif 240 <= hue < 300:
                r, g, b = x, 0, c
            else:
                r, g, b = c, 0, x
            
            r = int((r + m) * 255)
            g = int((g + m) * 255)
            b = int((b + m) * 255)
        else:
            # Default to blue
            r, g, b = 0, 0, 255
        
        return {'r': r, 'g': g, 'b': b}
    
    def _generate_audio_feedback(self, synchrony_value, config):
        """Generate audio feedback state."""
        if not config['audio_feedback']['enabled']:
            return {
                'playing': False,
                'frequency': 0,
                'volume': 0
            }
        
        audio_type = config['audio_feedback']['type']
        freq_range = config['audio_feedback']['frequency_range']
        
        # Map synchrony to frequency
        frequency = freq_range[0] + synchrony_value * (freq_range[1] - freq_range[0])
        
        # Map synchrony to volume
        volume = synchrony_value if config['audio_feedback']['volume_scaling'] else 0.5
        
        return {
            'playing': synchrony_value > 0.1,  # Only play if some synchrony
            'type': audio_type,
            'frequency': frequency,
            'volume': volume,
            'binaural_beat_frequency': frequency + 10 if audio_type == 'binaural_beats' else None
        }
    
    def _generate_haptic_feedback(self, synchrony_value, config):
        """Generate haptic feedback state."""
        if not config['haptic_feedback']['enabled']:
            return {
                'active': False,
                'intensity': 0,
                'pattern': 'none'
            }
        
        # Map synchrony to intensity
        intensity = synchrony_value if config['haptic_feedback']['intensity_scaling'] else 0.5
        
        # Determine pattern based on synchrony level
        if synchrony_value < 0.3:
            pattern = 'gentle_pulse'
        elif synchrony_value < 0.6:
            pattern = 'steady_vibration'
        else:
            pattern = 'rhythmic_pulse'
        
        return {
            'active': synchrony_value > 0.1,
            'intensity': intensity,
            'pattern': pattern,
            'frequency': synchrony_value * 50  # 0-50 Hz
        }
    
    def _determine_synchrony_level(self, synchrony_value, config):
        """Determine synchrony level based on thresholds."""
        thresholds = config['synchrony_thresholds']
        
        if synchrony_value >= thresholds['high']:
            return 'high'
        elif synchrony_value >= thresholds['medium']:
            return 'medium'
        elif synchrony_value >= thresholds['low']:
            return 'low'
        else:
            return 'very_low'


# Global biofeedback engine instance
biofeedback_engine = ARBiofeedbackEngine()


@ar_biofeedback_bp.route('/sessions', methods=['POST'])
def create_biofeedback_session():
    """
    Create a new AR biofeedback session.
    
    Expected JSON payload:
    {
        "session_id": "string",
        "config": {object} (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        session_id = data.get('session_id')
        if not session_id:
            session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        config = data.get('config')
        
        session = biofeedback_engine.create_session(session_id, config)
        
        return jsonify({
            'message': 'Biofeedback session created successfully',
            'session_id': session_id,
            'config': session['config'],
            'initial_state': session['current_state']
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ar_biofeedback_bp.route('/sessions/<session_id>/update', methods=['POST'])
def update_biofeedback(session_id):
    """
    Update biofeedback based on synchrony metrics.
    
    Expected JSON payload:
    {
        "synchrony_metrics": {
            "plv": float,
            "crqa_determinism": float,
            "fnirs_coherence": float,
            ...
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        synchrony_metrics = data.get('synchrony_metrics', {})
        
        feedback_state = biofeedback_engine.update_feedback(session_id, synchrony_metrics)
        
        return jsonify({
            'session_id': session_id,
            'feedback_state': feedback_state,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ar_biofeedback_bp.route('/sessions/<session_id>/state', methods=['GET'])
def get_biofeedback_state(session_id):
    """Get current biofeedback state for a session."""
    try:
        if session_id not in biofeedback_engine.feedback_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session = biofeedback_engine.feedback_sessions[session_id]
        
        return jsonify({
            'session_id': session_id,
            'current_state': session['current_state'],
            'config': session['config'],
            'created_at': session['created_at'].isoformat(),
            'last_updated': session['last_updated'].isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ar_biofeedback_bp.route('/sessions/<session_id>/config', methods=['PUT'])
def update_session_config(session_id):
    """
    Update biofeedback session configuration.
    
    Expected JSON payload:
    {
        "config": {object}
    }
    """
    try:
        if session_id not in biofeedback_engine.feedback_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        data = request.get_json()
        if not data or 'config' not in data:
            return jsonify({'error': 'Config data required'}), 400
        
        session = biofeedback_engine.feedback_sessions[session_id]
        session['config'].update(data['config'])
        session['last_updated'] = datetime.utcnow()
        
        return jsonify({
            'message': 'Configuration updated successfully',
            'session_id': session_id,
            'config': session['config']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ar_biofeedback_bp.route('/sessions/<session_id>/history', methods=['GET'])
def get_session_history(session_id):
    """Get biofeedback session history."""
    try:
        if session_id not in biofeedback_engine.feedback_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session = biofeedback_engine.feedback_sessions[session_id]
        limit = request.args.get('limit', 50, type=int)
        
        history = session['history'][-limit:] if limit else session['history']
        
        return jsonify({
            'session_id': session_id,
            'history': history,
            'count': len(history)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ar_biofeedback_bp.route('/sessions', methods=['GET'])
def list_sessions():
    """List all active biofeedback sessions."""
    try:
        sessions = []
        for session_id, session_data in biofeedback_engine.feedback_sessions.items():
            sessions.append({
                'session_id': session_id,
                'created_at': session_data['created_at'].isoformat(),
                'last_updated': session_data['last_updated'].isoformat(),
                'synchrony_level': session_data['current_state']['synchrony_level'],
                'last_synchrony_value': session_data['current_state']['last_synchrony_value']
            })
        
        return jsonify({
            'sessions': sessions,
            'count': len(sessions)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ar_biofeedback_bp.route('/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a biofeedback session."""
    try:
        if session_id not in biofeedback_engine.feedback_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        del biofeedback_engine.feedback_sessions[session_id]
        
        return jsonify({
            'message': 'Session deleted successfully',
            'session_id': session_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ar_biofeedback_bp.route('/config/default', methods=['GET'])
def get_default_config():
    """Get default biofeedback configuration."""
    return jsonify({
        'default_config': biofeedback_engine.get_default_config()
    }), 200


@ar_biofeedback_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'ar_biofeedback_service',
        'active_sessions': len(biofeedback_engine.feedback_sessions),
        'timestamp': datetime.utcnow().isoformat()
    }), 200

