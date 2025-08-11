#!/usr/bin/env python3
"""
SynchroTwin-AR Demo Backend
==========================

Simplified backend services for demonstration and testing.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading
import time
import random
import datetime
import json

# Create Flask apps for each service
apps = {}
socketio_instances = {}

def create_service_app(service_name, port):
    """Create a Flask app for a specific service."""
    app = Flask(f'{service_name}_service')
    CORS(app, origins="*")
    
    # Add SocketIO for notification service
    if service_name == 'notification':
        socketio = SocketIO(app, cors_allowed_origins="*")
        socketio_instances[service_name] = socketio
    
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'healthy',
            'service': f'{service_name.title()} Service',
            'timestamp': datetime.datetime.now().isoformat(),
            'port': port
        })
    
    # Service-specific endpoints
    if service_name == 'digital_twin':
        @app.route('/api/twins', methods=['GET', 'POST'])
        def twins():
            if request.method == 'GET':
                return jsonify({
                    'twins': [
                        {
                            'id': 'twin_001',
                            'participant_id': 'participant_1',
                            'state': {
                                'synchrony_level': random.uniform(0.3, 0.9),
                                'last_updated': datetime.datetime.now().isoformat()
                            }
                        }
                    ]
                })
            else:
                return jsonify({'message': 'Twin created', 'id': f'twin_{int(time.time())}'})
    
    elif service_name == 'synchrony_analysis':
        @app.route('/api/analyze/plv', methods=['POST'])
        def analyze_plv():
            return jsonify({
                'plv': random.uniform(0.2, 0.8),
                'timestamp': datetime.datetime.now().isoformat()
            })
        
        @app.route('/api/analyze/crqa', methods=['POST'])
        def analyze_crqa():
            return jsonify({
                'determinism': random.uniform(0.1, 0.7),
                'recurrence_rate': random.uniform(0.05, 0.3),
                'timestamp': datetime.datetime.now().isoformat()
            })
    
    elif service_name == 'ar_biofeedback':
        @app.route('/api/sessions', methods=['POST'])
        def create_session():
            return jsonify({
                'session_id': f'session_{int(time.time())}',
                'status': 'created'
            })
        
        @app.route('/api/sessions/<session_id>/feedback', methods=['GET'])
        def get_feedback(session_id):
            return jsonify({
                'visual_feedback': {
                    'intensity': random.uniform(0.3, 0.9),
                    'particle_count': random.randint(50, 200)
                },
                'audio_feedback': {
                    'enabled': True,
                    'volume': random.uniform(0.2, 0.8)
                }
            })
    
    elif service_name == 'data_ingestion':
        @app.route('/api/streams', methods=['GET', 'POST'])
        def streams():
            if request.method == 'GET':
                return jsonify({
                    'streams': [
                        {
                            'stream_id': 'eeg_stream_001',
                            'is_running': True,
                            'total_samples': random.randint(1000, 5000),
                            'info': {
                                'config': {
                                    'data_type': 'eeg',
                                    'sampling_rate': 1000,
                                    'buffer_size': 10000
                                }
                            }
                        }
                    ]
                })
            else:
                return jsonify({'message': 'Stream created', 'stream_id': f'stream_{int(time.time())}'})
    
    elif service_name == 'notification':
        @app.route('/api/notifications', methods=['GET'])
        def get_notifications():
            return jsonify({
                'notifications': [
                    {
                        'id': f'notif_{int(time.time())}',
                        'topic': 'synchrony_updates',
                        'data': {
                            'synchrony_metrics': {
                                'plv': random.uniform(0.3, 0.8)
                            }
                        },
                        'timestamp': datetime.datetime.now().isoformat()
                    }
                ]
            })
    
    apps[service_name] = app
    return app

def run_service(service_name, port):
    """Run a service on a specific port."""
    app = create_service_app(service_name, port)
    print(f"Starting {service_name} service on port {port}")
    
    if service_name == 'notification':
        socketio = socketio_instances[service_name]
        socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
    else:
        app.run(host='0.0.0.0', port=port, debug=False)

def generate_demo_data():
    """Generate demo data and emit via WebSocket."""
    while True:
        time.sleep(5)  # Update every 5 seconds
        
        # Generate sample synchrony data
        demo_data = {
            'synchrony_metrics': {
                'plv': random.uniform(0.2, 0.9),
                'crqa_determinism': random.uniform(0.1, 0.7),
                'fnirs_coherence': random.uniform(0.3, 0.8)
            },
            'biofeedback_state': {
                'visual_feedback': {
                    'intensity': random.uniform(0.3, 0.9),
                    'particle_count': random.randint(50, 200)
                }
            },
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        # Emit to notification service if available
        if 'notification' in socketio_instances:
            socketio = socketio_instances['notification']
            socketio.emit('synchrony_update', demo_data)
            print(f"Emitted demo data: PLV={demo_data['synchrony_metrics']['plv']:.3f}")

if __name__ == '__main__':
    services = [
        ('digital_twin', 5000),
        ('synchrony_analysis', 5001),
        ('ar_biofeedback', 5002),
        ('data_ingestion', 5003),
        ('notification', 5004)
    ]
    
    print("🚀 Starting SynchroTwin-AR Demo Backend Services...")
    
    # Start all services in separate threads
    threads = []
    for service_name, port in services:
        thread = threading.Thread(target=run_service, args=(service_name, port), daemon=True)
        thread.start()
        threads.append(thread)
        time.sleep(1)  # Stagger startup
    
    # Start demo data generator
    demo_thread = threading.Thread(target=generate_demo_data, daemon=True)
    demo_thread.start()
    
    print("✅ All services started successfully!")
    print("📊 Demo data generation active")
    print("🌐 Services available at:")
    for service_name, port in services:
        print(f"   - {service_name.title()} Service: http://localhost:{port}")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")

