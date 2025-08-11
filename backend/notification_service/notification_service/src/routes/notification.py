"""
Notification API Routes
=======================

Flask routes for real-time notifications and WebSocket communication.
"""

from flask import Blueprint, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
import json
from datetime import datetime
import uuid
from collections import defaultdict, deque

notification_bp = Blueprint('notification', __name__)


class NotificationEngine:
    """
    Notification Engine for managing real-time notifications and WebSocket connections.
    """
    
    def __init__(self, socketio):
        self.socketio = socketio
        self.connected_clients = {}  # session_id -> client_info
        self.notification_history = defaultdict(lambda: deque(maxlen=100))
        self.subscriptions = defaultdict(set)  # topic -> set of session_ids
        self.client_rooms = defaultdict(set)  # session_id -> set of rooms
        
    def register_client(self, session_id, client_info):
        """Register a new client connection."""
        self.connected_clients[session_id] = {
            **client_info,
            'connected_at': datetime.utcnow(),
            'last_activity': datetime.utcnow()
        }
        
    def unregister_client(self, session_id):
        """Unregister a client connection."""
        if session_id in self.connected_clients:
            # Remove from all subscriptions
            for topic in list(self.subscriptions.keys()):
                self.subscriptions[topic].discard(session_id)
                if not self.subscriptions[topic]:
                    del self.subscriptions[topic]
            
            # Remove from client rooms
            if session_id in self.client_rooms:
                del self.client_rooms[session_id]
            
            del self.connected_clients[session_id]
    
    def subscribe_to_topic(self, session_id, topic):
        """Subscribe a client to a notification topic."""
        if session_id in self.connected_clients:
            self.subscriptions[topic].add(session_id)
            self.client_rooms[session_id].add(topic)
            return True
        return False
    
    def unsubscribe_from_topic(self, session_id, topic):
        """Unsubscribe a client from a notification topic."""
        self.subscriptions[topic].discard(session_id)
        self.client_rooms[session_id].discard(topic)
        
        if not self.subscriptions[topic]:
            del self.subscriptions[topic]
    
    def send_notification(self, topic, notification_data, target_session=None):
        """Send notification to subscribers of a topic."""
        notification = {
            'id': str(uuid.uuid4()),
            'topic': topic,
            'data': notification_data,
            'timestamp': datetime.utcnow().isoformat(),
            'type': notification_data.get('type', 'info')
        }
        
        # Store in history
        self.notification_history[topic].append(notification)
        
        # Send to specific session or all subscribers
        if target_session:
            if target_session in self.subscriptions.get(topic, set()):
                self.socketio.emit('notification', notification, room=target_session)
        else:
            # Send to all subscribers of the topic
            for session_id in self.subscriptions.get(topic, set()):
                self.socketio.emit('notification', notification, room=session_id)
        
        return notification
    
    def broadcast_system_message(self, message, message_type='info'):
        """Broadcast a system message to all connected clients."""
        notification_data = {
            'type': message_type,
            'message': message,
            'source': 'system'
        }
        
        return self.send_notification('system', notification_data)
    
    def send_synchrony_update(self, session_id, synchrony_data):
        """Send synchrony analysis update."""
        notification_data = {
            'type': 'synchrony_update',
            'synchrony_metrics': synchrony_data,
            'source': 'synchrony_analysis'
        }
        
        return self.send_notification('synchrony_updates', notification_data, target_session=session_id)
    
    def send_biofeedback_update(self, session_id, biofeedback_data):
        """Send biofeedback state update."""
        notification_data = {
            'type': 'biofeedback_update',
            'biofeedback_state': biofeedback_data,
            'source': 'ar_biofeedback'
        }
        
        return self.send_notification('biofeedback_updates', notification_data, target_session=session_id)
    
    def send_twin_update(self, twin_id, twin_data):
        """Send digital twin update."""
        notification_data = {
            'type': 'twin_update',
            'twin_id': twin_id,
            'twin_data': twin_data,
            'source': 'digital_twin'
        }
        
        return self.send_notification('twin_updates', notification_data)
    
    def send_data_stream_update(self, stream_id, stream_data):
        """Send data stream update."""
        notification_data = {
            'type': 'stream_update',
            'stream_id': stream_id,
            'stream_data': stream_data,
            'source': 'data_ingestion'
        }
        
        return self.send_notification('stream_updates', notification_data)
    
    def get_notification_history(self, topic, limit=50):
        """Get notification history for a topic."""
        history = list(self.notification_history[topic])
        return history[-limit:] if limit else history
    
    def get_client_info(self, session_id):
        """Get information about a connected client."""
        return self.connected_clients.get(session_id)
    
    def get_connected_clients(self):
        """Get list of all connected clients."""
        return list(self.connected_clients.keys())
    
    def get_topic_subscribers(self, topic):
        """Get list of subscribers for a topic."""
        return list(self.subscriptions.get(topic, set()))


# Global notification engine (will be initialized with SocketIO)
notification_engine = None


def init_notification_engine(socketio):
    """Initialize the notification engine with SocketIO instance."""
    global notification_engine
    notification_engine = NotificationEngine(socketio)
    return notification_engine


@notification_bp.route('/send', methods=['POST'])
def send_notification():
    """
    Send a notification to a topic.
    
    Expected JSON payload:
    {
        "topic": "string",
        "data": {object},
        "target_session": "string" (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        topic = data.get('topic')
        notification_data = data.get('data', {})
        target_session = data.get('target_session')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        notification = notification_engine.send_notification(
            topic, notification_data, target_session
        )
        
        return jsonify({
            'message': 'Notification sent successfully',
            'notification': notification
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notification_bp.route('/broadcast', methods=['POST'])
def broadcast_message():
    """
    Broadcast a system message to all clients.
    
    Expected JSON payload:
    {
        "message": "string",
        "type": "info|warning|error|success"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        message = data.get('message')
        message_type = data.get('type', 'info')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        notification = notification_engine.broadcast_system_message(message, message_type)
        
        return jsonify({
            'message': 'Broadcast sent successfully',
            'notification': notification
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notification_bp.route('/history/<topic>', methods=['GET'])
def get_notification_history(topic):
    """Get notification history for a topic."""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        history = notification_engine.get_notification_history(topic, limit)
        
        return jsonify({
            'topic': topic,
            'history': history,
            'count': len(history)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notification_bp.route('/clients', methods=['GET'])
def get_connected_clients():
    """Get list of connected clients."""
    try:
        clients = []
        
        for session_id in notification_engine.get_connected_clients():
            client_info = notification_engine.get_client_info(session_id)
            if client_info:
                clients.append({
                    'session_id': session_id,
                    'connected_at': client_info['connected_at'].isoformat(),
                    'last_activity': client_info['last_activity'].isoformat(),
                    'subscriptions': list(notification_engine.client_rooms.get(session_id, set()))
                })
        
        return jsonify({
            'clients': clients,
            'count': len(clients)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notification_bp.route('/topics', methods=['GET'])
def get_topics():
    """Get list of active topics and their subscribers."""
    try:
        topics = []
        
        for topic, subscribers in notification_engine.subscriptions.items():
            topics.append({
                'topic': topic,
                'subscriber_count': len(subscribers),
                'subscribers': list(subscribers)
            })
        
        return jsonify({
            'topics': topics,
            'count': len(topics)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notification_bp.route('/synchrony', methods=['POST'])
def send_synchrony_notification():
    """
    Send synchrony analysis notification.
    
    Expected JSON payload:
    {
        "session_id": "string",
        "synchrony_data": {object}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        session_id = data.get('session_id')
        synchrony_data = data.get('synchrony_data', {})
        
        if not session_id:
            return jsonify({'error': 'Session ID is required'}), 400
        
        notification = notification_engine.send_synchrony_update(session_id, synchrony_data)
        
        return jsonify({
            'message': 'Synchrony notification sent successfully',
            'notification': notification
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notification_bp.route('/biofeedback', methods=['POST'])
def send_biofeedback_notification():
    """
    Send biofeedback state notification.
    
    Expected JSON payload:
    {
        "session_id": "string",
        "biofeedback_data": {object}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        session_id = data.get('session_id')
        biofeedback_data = data.get('biofeedback_data', {})
        
        if not session_id:
            return jsonify({'error': 'Session ID is required'}), 400
        
        notification = notification_engine.send_biofeedback_update(session_id, biofeedback_data)
        
        return jsonify({
            'message': 'Biofeedback notification sent successfully',
            'notification': notification
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notification_bp.route('/twin', methods=['POST'])
def send_twin_notification():
    """
    Send digital twin update notification.
    
    Expected JSON payload:
    {
        "twin_id": "string",
        "twin_data": {object}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        twin_id = data.get('twin_id')
        twin_data = data.get('twin_data', {})
        
        if not twin_id:
            return jsonify({'error': 'Twin ID is required'}), 400
        
        notification = notification_engine.send_twin_update(twin_id, twin_data)
        
        return jsonify({
            'message': 'Twin notification sent successfully',
            'notification': notification
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notification_bp.route('/stream', methods=['POST'])
def send_stream_notification():
    """
    Send data stream update notification.
    
    Expected JSON payload:
    {
        "stream_id": "string",
        "stream_data": {object}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        stream_id = data.get('stream_id')
        stream_data = data.get('stream_data', {})
        
        if not stream_id:
            return jsonify({'error': 'Stream ID is required'}), 400
        
        notification = notification_engine.send_data_stream_update(stream_id, stream_data)
        
        return jsonify({
            'message': 'Stream notification sent successfully',
            'notification': notification
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notification_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    connected_clients = len(notification_engine.get_connected_clients())
    active_topics = len(notification_engine.subscriptions)
    
    return jsonify({
        'status': 'healthy',
        'service': 'notification_service',
        'connected_clients': connected_clients,
        'active_topics': active_topics,
        'timestamp': datetime.utcnow().isoformat()
    }), 200


# WebSocket event handlers
def register_socketio_handlers(socketio):
    """Register WebSocket event handlers."""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection."""
        session_id = request.sid
        client_info = {
            'user_agent': request.headers.get('User-Agent', ''),
            'remote_addr': request.remote_addr
        }
        
        notification_engine.register_client(session_id, client_info)
        join_room(session_id)  # Join personal room
        
        emit('connected', {
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        session_id = request.sid
        notification_engine.unregister_client(session_id)
        leave_room(session_id)
    
    @socketio.on('subscribe')
    def handle_subscribe(data):
        """Handle topic subscription."""
        session_id = request.sid
        topic = data.get('topic')
        
        if topic:
            success = notification_engine.subscribe_to_topic(session_id, topic)
            if success:
                join_room(topic)
                emit('subscribed', {
                    'topic': topic,
                    'timestamp': datetime.utcnow().isoformat()
                })
            else:
                emit('error', {'message': 'Failed to subscribe to topic'})
        else:
            emit('error', {'message': 'Topic is required'})
    
    @socketio.on('unsubscribe')
    def handle_unsubscribe(data):
        """Handle topic unsubscription."""
        session_id = request.sid
        topic = data.get('topic')
        
        if topic:
            notification_engine.unsubscribe_from_topic(session_id, topic)
            leave_room(topic)
            emit('unsubscribed', {
                'topic': topic,
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            emit('error', {'message': 'Topic is required'})
    
    @socketio.on('ping')
    def handle_ping():
        """Handle ping for keepalive."""
        session_id = request.sid
        if session_id in notification_engine.connected_clients:
            notification_engine.connected_clients[session_id]['last_activity'] = datetime.utcnow()
        
        emit('pong', {'timestamp': datetime.utcnow().isoformat()})
    
    @socketio.on('get_history')
    def handle_get_history(data):
        """Handle request for notification history."""
        topic = data.get('topic')
        limit = data.get('limit', 50)
        
        if topic:
            history = notification_engine.get_notification_history(topic, limit)
            emit('history', {
                'topic': topic,
                'history': history,
                'count': len(history)
            })
        else:
            emit('error', {'message': 'Topic is required'})

