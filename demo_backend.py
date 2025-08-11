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
import socket
import sys

# Create Flask apps for each service
apps = {}
socketio_instances = {}

def is_port_in_use(port):
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port):
    """Find an available port starting from start_port."""
    port = start_port
    while is_port_in_use(port):
        port += 1
    return port

def create_service_app(service_name, port):
    """Create a Flask app for a specific service."""
    app = Flask(f'{service_name}_service')
    CORS(app, origins="*")
    
    # Add SocketIO for notification service
    if service_name == 'notification':
        socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
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
                            'id': 'stream_001',
                            'type': 'eeg',
                            'status': 'active',
                            'data_points': random.randint(100, 1000)
                        }
                    ]
                })
            else:
                return jsonify({'message': 'Stream created', 'id': f'stream_{int(time.time())}'})
    
    elif service_name == 'notification':
        @app.route('/api/notifications', methods=['GET'])
        def get_notifications():
            return jsonify({
                'notifications': [
                    {
                        'id': f'notif_{int(time.time())}',
                        'type': 'info',
                        'message': 'System is running normally',
                        'timestamp': datetime.datetime.now().isoformat()
                    }
                ]
            })
        
        @socketio_instances[service_name].on('connect')
        def handle_connect():
            print(f"Client connected to {service_name} service")
            emit('status', {'data': 'Connected'})
        
        @socketio_instances[service_name].on('disconnect')
        def handle_disconnect():
            print(f"Client disconnected from {service_name} service")
    
    return app

def run_service(service_name, port):
    """Run a service on the specified port."""
    try:
        # Check if port is available, if not find another
        actual_port = find_available_port(port)
        if actual_port != port:
            print(f"Port {port} is in use, using port {actual_port} for {service_name}")
            port = actual_port
        
        app = create_service_app(service_name, port)
        
        if service_name == 'notification':
            socketio = socketio_instances[service_name]
            print(f"Starting {service_name} service on port {port}")
            socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
        else:
            print(f"Starting {service_name} service on port {port}")
            app.run(host='0.0.0.0', port=port, debug=False)
            
    except Exception as e:
        print(f"Error starting {service_name} service: {e}")

def generate_demo_data():
    """Generate demo data for WebSocket connections."""
    while True:
        try:
            # Emit demo data to notification service
            if 'notification' in socketio_instances:
                socketio = socketio_instances['notification']
                plv_value = random.uniform(0.2, 0.9)
                socketio.emit('plv_update', {
                    'plv': round(plv_value, 3),
                    'timestamp': datetime.datetime.now().isoformat()
                })
                print(f"Emitted demo data: PLV={plv_value:.3f}")
            time.sleep(2)
        except Exception as e:
            print(f"Error generating demo data: {e}")
            time.sleep(5)

if __name__ == '__main__':
    print("🚀 Starting SynchroTwin-AR Demo Backend Services...")
    
    # Define services and their default ports
    services = [
        ('digital_twin', 5000),
        ('synchrony_analysis', 5001),
        ('ar_biofeedback', 5002),
        ('data_ingestion', 5003),
        ('notification', 5004)
    ]
    
    # Start all services in separate threads
    threads = []
    for service_name, port in services:
        thread = threading.Thread(target=run_service, args=(service_name, port))
        thread.daemon = True
        threads.append(thread)
        thread.start()
        time.sleep(1)  # Small delay between service starts
    
    print("✅ All services started successfully!")
    print("📊 Demo data generation active")
    print("🌐 Services available at:")
    for service_name, port in services:
        actual_port = find_available_port(port)
        print(f"   - {service_name.title()} Service: http://localhost:{actual_port}")
    
    # Start demo data generation
    demo_thread = threading.Thread(target=generate_demo_data)
    demo_thread.daemon = True
    demo_thread.start()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        sys.exit(0)

