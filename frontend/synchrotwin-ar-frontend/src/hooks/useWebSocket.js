/**
 * React Hook for WebSocket Integration
 * ===================================
 * 
 * Custom React hook for managing WebSocket connections and real-time notifications.
 */

import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import webSocketClient from '../lib/websocket';

export const useWebSocket = (autoConnect = true) => {
  const [isConnected, setIsConnected] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [subscriptions, setSubscriptions] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [connectionError, setConnectionError] = useState(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  
  const notificationsRef = useRef(notifications);
  const maxNotifications = 100; // Keep last 100 notifications

  // Update ref when notifications change
  useEffect(() => {
    notificationsRef.current = notifications;
  }, [notifications]);

  // Connection status handler
  const handleConnectionStatus = useCallback((data) => {
    setIsConnected(true);
    setSessionId(data.sessionId);
    setConnectionError(null);
    setReconnectAttempts(0);
  }, []);

  // Disconnection handler
  const handleDisconnection = useCallback((data) => {
    setIsConnected(false);
    setSessionId(null);
    if (data.reason !== 'io client disconnect') {
      setConnectionError(`Disconnected: ${data.reason}`);
    }
  }, []);

  // Error handler
  const handleError = useCallback((data) => {
    setConnectionError(data.error);
  }, []);

  // Subscription handlers
  const handleSubscribed = useCallback((data) => {
    setSubscriptions(prev => {
      if (!prev.includes(data.topic)) {
        return [...prev, data.topic];
      }
      return prev;
    });
  }, []);

  const handleUnsubscribed = useCallback((data) => {
    setSubscriptions(prev => prev.filter(topic => topic !== data.topic));
  }, []);

  // Notification handler
  const handleNotification = useCallback((notification) => {
    setNotifications(prev => {
      const updated = [notification, ...prev];
      return updated.slice(0, maxNotifications);
    });
  }, []);

  // Setup event listeners
  useEffect(() => {
    webSocketClient.on('ws_connected', handleConnectionStatus);
    webSocketClient.on('ws_disconnected', handleDisconnection);
    webSocketClient.on('ws_error', handleError);
    webSocketClient.on('subscribed', handleSubscribed);
    webSocketClient.on('unsubscribed', handleUnsubscribed);
    webSocketClient.on('notification', handleNotification);

    return () => {
      webSocketClient.off('ws_connected', handleConnectionStatus);
      webSocketClient.off('ws_disconnected', handleDisconnection);
      webSocketClient.off('ws_error', handleError);
      webSocketClient.off('subscribed', handleSubscribed);
      webSocketClient.off('unsubscribed', handleUnsubscribed);
      webSocketClient.off('notification', handleNotification);
    };
  }, [
    handleConnectionStatus,
    handleDisconnection,
    handleError,
    handleSubscribed,
    handleUnsubscribed,
    handleNotification
  ]);

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect && !isConnected) {
      webSocketClient.connect();
      webSocketClient.subscribeToCommonTopics();
    }

    return () => {
      if (autoConnect) {
        webSocketClient.disconnect();
      }
    };
  }, [autoConnect, isConnected]);

  // API methods
  const connect = useCallback((url) => {
    webSocketClient.connect(url);
  }, []);

  const disconnect = useCallback(() => {
    webSocketClient.disconnect();
    setIsConnected(false);
    setSessionId(null);
    setSubscriptions([]);
    setConnectionError(null);
  }, []);

  const subscribe = useCallback((topic) => {
    return webSocketClient.subscribe(topic);
  }, []);

  const unsubscribe = useCallback((topic) => {
    return webSocketClient.unsubscribe(topic);
  }, []);

  const ping = useCallback(() => {
    return webSocketClient.ping();
  }, []);

  const getHistory = useCallback((topic, limit = 50) => {
    return webSocketClient.getHistory(topic, limit);
  }, []);

  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  const removeNotification = useCallback((notificationId) => {
    setNotifications(prev => 
      prev.filter(notification => notification.id !== notificationId)
    );
  }, []);

  const getNotificationsByTopic = useCallback((topic) => {
    return notificationsRef.current.filter(notification => notification.topic === topic);
  }, []);

  const getNotificationsByType = useCallback((type) => {
    return notificationsRef.current.filter(
      notification => notification.data?.type === type
    );
  }, []);

  return {
    // Connection state
    isConnected,
    sessionId,
    subscriptions,
    connectionError,
    reconnectAttempts,
    
    // Notifications
    notifications,
    
    // Connection methods
    connect,
    disconnect,
    
    // Subscription methods
    subscribe,
    unsubscribe,
    
    // Utility methods
    ping,
    getHistory,
    clearNotifications,
    removeNotification,
    getNotificationsByTopic,
    getNotificationsByType
  };
};

// Hook for specific notification types
export const useNotifications = (topic = null, type = null) => {
  const { notifications, getNotificationsByTopic, getNotificationsByType } = useWebSocket(false);
  
  const filteredNotifications = useMemo(() => {
    if (topic) {
      return getNotificationsByTopic(topic);
    }
    if (type) {
      return getNotificationsByType(type);
    }
    return notifications;
  }, [notifications, topic, type, getNotificationsByTopic, getNotificationsByType]);

  return filteredNotifications;
};

// Hook for synchrony updates
export const useSynchronyUpdates = () => {
  const [synchronyData, setSynchronyData] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    const handleSynchronyUpdate = (notification) => {
      setSynchronyData(notification.data.synchrony_metrics);
      setLastUpdate(new Date(notification.timestamp));
    };

    webSocketClient.on('notification_synchrony_updates', handleSynchronyUpdate);

    return () => {
      webSocketClient.off('notification_synchrony_updates', handleSynchronyUpdate);
    };
  }, []);

  return { synchronyData, lastUpdate };
};

// Hook for biofeedback updates
export const useBiofeedbackUpdates = () => {
  const [biofeedbackState, setBiofeedbackState] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    const handleBiofeedbackUpdate = (notification) => {
      setBiofeedbackState(notification.data.biofeedback_state);
      setLastUpdate(new Date(notification.timestamp));
    };

    webSocketClient.on('notification_biofeedback_updates', handleBiofeedbackUpdate);

    return () => {
      webSocketClient.off('notification_biofeedback_updates', handleBiofeedbackUpdate);
    };
  }, []);

  return { biofeedbackState, lastUpdate };
};

// Hook for digital twin updates
export const useTwinUpdates = () => {
  const [twinData, setTwinData] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    const handleTwinUpdate = (notification) => {
      setTwinData(notification.data.twin_data);
      setLastUpdate(new Date(notification.timestamp));
    };

    webSocketClient.on('notification_twin_updates', handleTwinUpdate);

    return () => {
      webSocketClient.off('notification_twin_updates', handleTwinUpdate);
    };
  }, []);

  return { twinData, lastUpdate };
};

// Hook for data stream updates
export const useStreamUpdates = () => {
  const [streamData, setStreamData] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    const handleStreamUpdate = (notification) => {
      setStreamData(notification.data.stream_data);
      setLastUpdate(new Date(notification.timestamp));
    };

    webSocketClient.on('notification_stream_updates', handleStreamUpdate);

    return () => {
      webSocketClient.off('notification_stream_updates', handleStreamUpdate);
    };
  }, []);

  return { streamData, lastUpdate };
};

export default useWebSocket;

