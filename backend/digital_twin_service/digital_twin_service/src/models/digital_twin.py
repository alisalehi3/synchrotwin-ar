"""
Digital Twin Model
==================

Database model for storing digital twin states and configurations.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


class DigitalTwin(db.Model):
    """
    Digital Twin model for storing twin states and metadata.
    """
    __tablename__ = 'digital_twins'
    
    id = db.Column(db.Integer, primary_key=True)
    twin_id = db.Column(db.String(100), unique=True, nullable=False)
    participant_id = db.Column(db.String(100), nullable=False)
    session_id = db.Column(db.String(100), nullable=False)
    
    # Twin state data
    current_state = db.Column(db.Text)  # JSON string
    synchrony_metrics = db.Column(db.Text)  # JSON string
    biofeedback_state = db.Column(db.Text)  # JSON string
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Configuration
    config = db.Column(db.Text)  # JSON string for twin configuration
    
    def __init__(self, twin_id, participant_id, session_id, config=None):
        self.twin_id = twin_id
        self.participant_id = participant_id
        self.session_id = session_id
        self.config = json.dumps(config) if config else '{}'
        self.current_state = '{}'
        self.synchrony_metrics = '{}'
        self.biofeedback_state = '{}'
    
    def get_current_state(self):
        """Get current state as dictionary."""
        return json.loads(self.current_state) if self.current_state else {}
    
    def set_current_state(self, state_dict):
        """Set current state from dictionary."""
        self.current_state = json.dumps(state_dict)
        self.updated_at = datetime.utcnow()
    
    def get_synchrony_metrics(self):
        """Get synchrony metrics as dictionary."""
        return json.loads(self.synchrony_metrics) if self.synchrony_metrics else {}
    
    def set_synchrony_metrics(self, metrics_dict):
        """Set synchrony metrics from dictionary."""
        self.synchrony_metrics = json.dumps(metrics_dict)
        self.updated_at = datetime.utcnow()
    
    def get_biofeedback_state(self):
        """Get biofeedback state as dictionary."""
        return json.loads(self.biofeedback_state) if self.biofeedback_state else {}
    
    def set_biofeedback_state(self, feedback_dict):
        """Set biofeedback state from dictionary."""
        self.biofeedback_state = json.dumps(feedback_dict)
        self.updated_at = datetime.utcnow()
    
    def get_config(self):
        """Get configuration as dictionary."""
        return json.loads(self.config) if self.config else {}
    
    def set_config(self, config_dict):
        """Set configuration from dictionary."""
        self.config = json.dumps(config_dict)
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'twin_id': self.twin_id,
            'participant_id': self.participant_id,
            'session_id': self.session_id,
            'current_state': self.get_current_state(),
            'synchrony_metrics': self.get_synchrony_metrics(),
            'biofeedback_state': self.get_biofeedback_state(),
            'config': self.get_config(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }


class TwinStateHistory(db.Model):
    """
    Model for storing historical states of digital twins.
    """
    __tablename__ = 'twin_state_history'
    
    id = db.Column(db.Integer, primary_key=True)
    twin_id = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # State data
    state_data = db.Column(db.Text)  # JSON string
    synchrony_data = db.Column(db.Text)  # JSON string
    biofeedback_data = db.Column(db.Text)  # JSON string
    
    # Metadata
    event_type = db.Column(db.String(50))  # 'state_update', 'synchrony_update', etc.
    
    def __init__(self, twin_id, state_data=None, synchrony_data=None, 
                 biofeedback_data=None, event_type='state_update'):
        self.twin_id = twin_id
        self.state_data = json.dumps(state_data) if state_data else '{}'
        self.synchrony_data = json.dumps(synchrony_data) if synchrony_data else '{}'
        self.biofeedback_data = json.dumps(biofeedback_data) if biofeedback_data else '{}'
        self.event_type = event_type
    
    def get_state_data(self):
        """Get state data as dictionary."""
        return json.loads(self.state_data) if self.state_data else {}
    
    def get_synchrony_data(self):
        """Get synchrony data as dictionary."""
        return json.loads(self.synchrony_data) if self.synchrony_data else {}
    
    def get_biofeedback_data(self):
        """Get biofeedback data as dictionary."""
        return json.loads(self.biofeedback_data) if self.biofeedback_data else {}
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'twin_id': self.twin_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'state_data': self.get_state_data(),
            'synchrony_data': self.get_synchrony_data(),
            'biofeedback_data': self.get_biofeedback_data(),
            'event_type': self.event_type
        }

