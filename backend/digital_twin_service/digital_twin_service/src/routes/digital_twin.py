"""
Digital Twin API Routes
=======================

Flask routes for managing digital twins and their states.
"""

from flask import Blueprint, request, jsonify
from src.models.digital_twin import db, DigitalTwin, TwinStateHistory
from datetime import datetime
import uuid

digital_twin_bp = Blueprint('digital_twin', __name__)


@digital_twin_bp.route('/twins', methods=['POST'])
def create_twin():
    """
    Create a new digital twin.
    
    Expected JSON payload:
    {
        "participant_id": "string",
        "session_id": "string",
        "config": {object}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        participant_id = data.get('participant_id')
        session_id = data.get('session_id')
        config = data.get('config', {})
        
        if not participant_id or not session_id:
            return jsonify({'error': 'participant_id and session_id are required'}), 400
        
        # Generate unique twin ID
        twin_id = f"twin_{participant_id}_{session_id}_{uuid.uuid4().hex[:8]}"
        
        # Create new digital twin
        twin = DigitalTwin(
            twin_id=twin_id,
            participant_id=participant_id,
            session_id=session_id,
            config=config
        )
        
        db.session.add(twin)
        db.session.commit()
        
        return jsonify({
            'message': 'Digital twin created successfully',
            'twin': twin.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@digital_twin_bp.route('/twins/<twin_id>', methods=['GET'])
def get_twin(twin_id):
    """Get digital twin by ID."""
    try:
        twin = DigitalTwin.query.filter_by(twin_id=twin_id).first()
        
        if not twin:
            return jsonify({'error': 'Digital twin not found'}), 404
        
        return jsonify({'twin': twin.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@digital_twin_bp.route('/twins/<twin_id>/state', methods=['PUT'])
def update_twin_state(twin_id):
    """
    Update digital twin state.
    
    Expected JSON payload:
    {
        "current_state": {object},
        "synchrony_metrics": {object},
        "biofeedback_state": {object}
    }
    """
    try:
        twin = DigitalTwin.query.filter_by(twin_id=twin_id).first()
        
        if not twin:
            return jsonify({'error': 'Digital twin not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Update state components
        if 'current_state' in data:
            twin.set_current_state(data['current_state'])
        
        if 'synchrony_metrics' in data:
            twin.set_synchrony_metrics(data['synchrony_metrics'])
        
        if 'biofeedback_state' in data:
            twin.set_biofeedback_state(data['biofeedback_state'])
        
        # Save to history
        history_entry = TwinStateHistory(
            twin_id=twin_id,
            state_data=data.get('current_state'),
            synchrony_data=data.get('synchrony_metrics'),
            biofeedback_data=data.get('biofeedback_state'),
            event_type='state_update'
        )
        
        db.session.add(history_entry)
        db.session.commit()
        
        return jsonify({
            'message': 'Twin state updated successfully',
            'twin': twin.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@digital_twin_bp.route('/twins/<twin_id>/synchrony', methods=['PUT'])
def update_synchrony_metrics(twin_id):
    """
    Update synchrony metrics for a digital twin.
    
    Expected JSON payload:
    {
        "plv": float,
        "crqa_metrics": {object},
        "fnirs_coherence": {object},
        "timestamp": "ISO string"
    }
    """
    try:
        twin = DigitalTwin.query.filter_by(twin_id=twin_id).first()
        
        if not twin:
            return jsonify({'error': 'Digital twin not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Update synchrony metrics
        current_metrics = twin.get_synchrony_metrics()
        current_metrics.update(data)
        current_metrics['last_updated'] = datetime.utcnow().isoformat()
        
        twin.set_synchrony_metrics(current_metrics)
        
        # Save to history
        history_entry = TwinStateHistory(
            twin_id=twin_id,
            synchrony_data=data,
            event_type='synchrony_update'
        )
        
        db.session.add(history_entry)
        db.session.commit()
        
        return jsonify({
            'message': 'Synchrony metrics updated successfully',
            'metrics': current_metrics
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@digital_twin_bp.route('/twins/<twin_id>/biofeedback', methods=['PUT'])
def update_biofeedback_state(twin_id):
    """
    Update biofeedback state for a digital twin.
    
    Expected JSON payload:
    {
        "visual_cues": {object},
        "audio_feedback": {object},
        "haptic_feedback": {object},
        "ar_elements": {object}
    }
    """
    try:
        twin = DigitalTwin.query.filter_by(twin_id=twin_id).first()
        
        if not twin:
            return jsonify({'error': 'Digital twin not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Update biofeedback state
        current_feedback = twin.get_biofeedback_state()
        current_feedback.update(data)
        current_feedback['last_updated'] = datetime.utcnow().isoformat()
        
        twin.set_biofeedback_state(current_feedback)
        
        # Save to history
        history_entry = TwinStateHistory(
            twin_id=twin_id,
            biofeedback_data=data,
            event_type='biofeedback_update'
        )
        
        db.session.add(history_entry)
        db.session.commit()
        
        return jsonify({
            'message': 'Biofeedback state updated successfully',
            'biofeedback_state': current_feedback
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@digital_twin_bp.route('/twins/<twin_id>/history', methods=['GET'])
def get_twin_history(twin_id):
    """Get historical states for a digital twin."""
    try:
        # Get query parameters
        limit = request.args.get('limit', 100, type=int)
        event_type = request.args.get('event_type')
        
        # Build query
        query = TwinStateHistory.query.filter_by(twin_id=twin_id)
        
        if event_type:
            query = query.filter_by(event_type=event_type)
        
        history = query.order_by(TwinStateHistory.timestamp.desc()).limit(limit).all()
        
        return jsonify({
            'history': [entry.to_dict() for entry in history],
            'count': len(history)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@digital_twin_bp.route('/twins/session/<session_id>', methods=['GET'])
def get_twins_by_session(session_id):
    """Get all digital twins for a session."""
    try:
        twins = DigitalTwin.query.filter_by(session_id=session_id, is_active=True).all()
        
        return jsonify({
            'twins': [twin.to_dict() for twin in twins],
            'count': len(twins)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@digital_twin_bp.route('/twins/<twin_id>', methods=['DELETE'])
def deactivate_twin(twin_id):
    """Deactivate a digital twin."""
    try:
        twin = DigitalTwin.query.filter_by(twin_id=twin_id).first()
        
        if not twin:
            return jsonify({'error': 'Digital twin not found'}), 404
        
        twin.is_active = False
        twin.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'Digital twin deactivated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@digital_twin_bp.route('/twins/<twin_id>/config', methods=['PUT'])
def update_twin_config(twin_id):
    """
    Update digital twin configuration.
    
    Expected JSON payload:
    {
        "config": {object}
    }
    """
    try:
        twin = DigitalTwin.query.filter_by(twin_id=twin_id).first()
        
        if not twin:
            return jsonify({'error': 'Digital twin not found'}), 404
        
        data = request.get_json()
        if not data or 'config' not in data:
            return jsonify({'error': 'Config data required'}), 400
        
        twin.set_config(data['config'])
        db.session.commit()
        
        return jsonify({
            'message': 'Twin configuration updated successfully',
            'config': twin.get_config()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@digital_twin_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'digital_twin_service',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

