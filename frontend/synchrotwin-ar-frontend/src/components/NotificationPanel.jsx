/**
 * Notification Panel Component
 * ===========================
 * 
 * Real-time notification display and management with WebSocket integration.
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { ScrollArea } from './ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { 
  Bell, 
  BellOff, 
  Trash2, 
  Filter, 
  CheckCircle, 
  AlertCircle, 
  Info, 
  XCircle,
  Brain,
  Eye,
  Database,
  Activity,
  Zap,
  Clock,
  Wifi,
  WifiOff
} from 'lucide-react';

const NotificationPanel = ({ 
  notifications = [], 
  isConnected = false, 
  subscriptions = [], 
  detailed = false 
}) => {
  const [filter, setFilter] = useState('all'); // all, system, synchrony, biofeedback, twin, stream
  const [showRead, setShowRead] = useState(true);
  const [readNotifications, setReadNotifications] = useState(new Set());

  // Mark notification as read
  const markAsRead = (notificationId) => {
    setReadNotifications(prev => new Set([...prev, notificationId]));
  };

  // Mark all notifications as read
  const markAllAsRead = () => {
    const allIds = notifications.map(n => n.id);
    setReadNotifications(new Set(allIds));
  };

  // Clear all notifications
  const clearAll = () => {
    setReadNotifications(new Set());
  };

  // Filter notifications based on current filter
  const filteredNotifications = notifications.filter(notification => {
    if (filter === 'all') return true;
    return notification.topic === filter || notification.topic.includes(filter);
  }).filter(notification => {
    if (!showRead && readNotifications.has(notification.id)) return false;
    return true;
  });

  // Get notification icon based on type
  const getNotificationIcon = (notification) => {
    const type = notification.data?.type || notification.topic;
    
    switch (type) {
      case 'synchrony_update':
      case 'synchrony_updates':
        return <Brain className="w-4 h-4 text-blue-500" />;
      case 'biofeedback_update':
      case 'biofeedback_updates':
        return <Eye className="w-4 h-4 text-green-500" />;
      case 'twin_update':
      case 'twin_updates':
        return <Database className="w-4 h-4 text-purple-500" />;
      case 'stream_update':
      case 'stream_updates':
        return <Activity className="w-4 h-4 text-orange-500" />;
      case 'system':
        return <Zap className="w-4 h-4 text-yellow-500" />;
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'warning':
        return <AlertCircle className="w-4 h-4 text-yellow-500" />;
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      default:
        return <Info className="w-4 h-4 text-blue-500" />;
    }
  };

  // Get notification priority/urgency
  const getNotificationPriority = (notification) => {
    const type = notification.data?.type;
    
    if (type === 'error') return { priority: 'high', color: 'destructive' };
    if (type === 'warning') return { priority: 'medium', color: 'secondary' };
    if (type === 'success') return { priority: 'low', color: 'default' };
    return { priority: 'normal', color: 'outline' };
  };

  // Format notification message
  const formatNotificationMessage = (notification) => {
    const data = notification.data;
    
    if (data?.message) {
      return data.message;
    }
    
    switch (notification.topic) {
      case 'synchrony_updates':
        if (data?.synchrony_metrics) {
          const plv = data.synchrony_metrics.plv;
          return `Synchrony update: PLV = ${(plv * 100).toFixed(1)}%`;
        }
        return 'Synchrony metrics updated';
        
      case 'biofeedback_updates':
        if (data?.biofeedback_state?.visual_feedback) {
          const intensity = data.biofeedback_state.visual_feedback.intensity;
          return `Biofeedback update: Intensity = ${(intensity * 100).toFixed(0)}%`;
        }
        return 'Biofeedback state updated';
        
      case 'twin_updates':
        if (data?.twin_id) {
          return `Digital twin ${data.twin_id} updated`;
        }
        return 'Digital twin updated';
        
      case 'stream_updates':
        if (data?.stream_id) {
          return `Data stream ${data.stream_id} updated`;
        }
        return 'Data stream updated';
        
      default:
        return 'System notification';
    }
  };

  // Get time ago string
  const getTimeAgo = (timestamp) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now - time;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return time.toLocaleDateString();
  };

  // Count notifications by type
  const notificationCounts = {
    all: notifications.length,
    system: notifications.filter(n => n.topic === 'system').length,
    synchrony: notifications.filter(n => n.topic.includes('synchrony')).length,
    biofeedback: notifications.filter(n => n.topic.includes('biofeedback')).length,
    twin: notifications.filter(n => n.topic.includes('twin')).length,
    stream: notifications.filter(n => n.topic.includes('stream')).length
  };

  const unreadCount = notifications.filter(n => !readNotifications.has(n.id)).length;

  if (!detailed) {
    // Compact view for overview
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Bell className="w-5 h-5" />
              <span>Notifications</span>
              {unreadCount > 0 && (
                <Badge variant="destructive" className="text-xs">
                  {unreadCount}
                </Badge>
              )}
            </div>
            <div className="flex items-center space-x-1">
              {isConnected ? (
                <Wifi className="w-4 h-4 text-green-500" />
              ) : (
                <WifiOff className="w-4 h-4 text-red-500" />
              )}
            </div>
          </CardTitle>
          <CardDescription>
            Real-time system notifications
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-48">
            <div className="space-y-2">
              {filteredNotifications.length === 0 ? (
                <div className="text-center py-4 text-muted-foreground">
                  No notifications
                </div>
              ) : (
                filteredNotifications.slice(0, 5).map((notification) => {
                  const isRead = readNotifications.has(notification.id);
                  const priority = getNotificationPriority(notification);
                  
                  return (
                    <div
                      key={notification.id}
                      className={`p-2 border rounded cursor-pointer transition-colors ${
                        isRead ? 'bg-muted/50' : 'bg-background hover:bg-muted/30'
                      }`}
                      onClick={() => markAsRead(notification.id)}
                    >
                      <div className="flex items-start space-x-2">
                        {getNotificationIcon(notification)}
                        <div className="flex-1 min-w-0">
                          <p className={`text-sm ${isRead ? 'text-muted-foreground' : 'font-medium'}`}>
                            {formatNotificationMessage(notification)}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {getTimeAgo(notification.timestamp)}
                          </p>
                        </div>
                        {!isRead && (
                          <div className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0 mt-1" />
                        )}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </ScrollArea>
          
          {/* Quick Actions */}
          <div className="flex items-center justify-between mt-4 pt-4 border-t">
            <div className="text-xs text-muted-foreground">
              {subscriptions.length} subscriptions
            </div>
            <div className="flex items-center space-x-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={markAllAsRead}
                disabled={unreadCount === 0}
              >
                <CheckCircle className="w-3 h-3" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={clearAll}
              >
                <Trash2 className="w-3 h-3" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Detailed view
  return (
    <div className="space-y-6">
      {/* Notification Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Bell className="w-5 h-5" />
              <span>Notification Center</span>
              {unreadCount > 0 && (
                <Badge variant="destructive">
                  {unreadCount} unread
                </Badge>
              )}
            </div>
            <div className="flex items-center space-x-2">
              <Badge variant={isConnected ? "default" : "destructive"} className="flex items-center space-x-1">
                {isConnected ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
                <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
              </Badge>
              <Button
                variant="outline"
                size="sm"
                onClick={markAllAsRead}
                disabled={unreadCount === 0}
              >
                <CheckCircle className="w-4 h-4 mr-1" />
                Mark All Read
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={clearAll}
              >
                <Trash2 className="w-4 h-4 mr-1" />
                Clear All
              </Button>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold">{notificationCounts.all}</div>
              <p className="text-xs text-muted-foreground">Total</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">{notificationCounts.system}</div>
              <p className="text-xs text-muted-foreground">System</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{notificationCounts.synchrony}</div>
              <p className="text-xs text-muted-foreground">Synchrony</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{notificationCounts.biofeedback}</div>
              <p className="text-xs text-muted-foreground">Biofeedback</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{notificationCounts.twin}</div>
              <p className="text-xs text-muted-foreground">Twin</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">{notificationCounts.stream}</div>
              <p className="text-xs text-muted-foreground">Stream</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Notification Filters and List */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Notifications</CardTitle>
          <CardDescription>
            Filter and manage real-time system notifications
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={filter} onValueChange={setFilter} className="space-y-4">
            <TabsList className="grid w-full grid-cols-6">
              <TabsTrigger value="all">All ({notificationCounts.all})</TabsTrigger>
              <TabsTrigger value="system">System ({notificationCounts.system})</TabsTrigger>
              <TabsTrigger value="synchrony">Synchrony ({notificationCounts.synchrony})</TabsTrigger>
              <TabsTrigger value="biofeedback">Biofeedback ({notificationCounts.biofeedback})</TabsTrigger>
              <TabsTrigger value="twin">Twin ({notificationCounts.twin})</TabsTrigger>
              <TabsTrigger value="stream">Stream ({notificationCounts.stream})</TabsTrigger>
            </TabsList>

            {/* Filter Controls */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Button
                  variant={showRead ? "default" : "outline"}
                  size="sm"
                  onClick={() => setShowRead(!showRead)}
                >
                  <Filter className="w-4 h-4 mr-1" />
                  {showRead ? 'Hide Read' : 'Show Read'}
                </Button>
              </div>
              <div className="text-sm text-muted-foreground">
                Showing {filteredNotifications.length} notifications
              </div>
            </div>

            {/* Notification List */}
            <ScrollArea className="h-96">
              <div className="space-y-2">
                {filteredNotifications.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <BellOff className="w-8 h-8 mx-auto mb-2" />
                    <p>No notifications to display</p>
                  </div>
                ) : (
                  filteredNotifications.map((notification) => {
                    const isRead = readNotifications.has(notification.id);
                    const priority = getNotificationPriority(notification);
                    
                    return (
                      <div
                        key={notification.id}
                        className={`p-4 border rounded-lg cursor-pointer transition-all ${
                          isRead 
                            ? 'bg-muted/30 border-muted' 
                            : 'bg-background border-border hover:bg-muted/20'
                        }`}
                        onClick={() => markAsRead(notification.id)}
                      >
                        <div className="flex items-start space-x-3">
                          {getNotificationIcon(notification)}
                          
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between">
                              <h4 className={`text-sm ${isRead ? 'text-muted-foreground' : 'font-medium'}`}>
                                {formatNotificationMessage(notification)}
                              </h4>
                              <div className="flex items-center space-x-2">
                                <Badge variant={priority.color} className="text-xs">
                                  {priority.priority}
                                </Badge>
                                {!isRead && (
                                  <div className="w-2 h-2 bg-blue-500 rounded-full" />
                                )}
                              </div>
                            </div>
                            
                            <div className="flex items-center justify-between mt-1">
                              <p className="text-xs text-muted-foreground">
                                Topic: {notification.topic}
                              </p>
                              <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                                <Clock className="w-3 h-3" />
                                <span>{getTimeAgo(notification.timestamp)}</span>
                              </div>
                            </div>
                            
                            {/* Additional Data */}
                            {notification.data && Object.keys(notification.data).length > 1 && (
                              <div className="mt-2 p-2 bg-muted/50 rounded text-xs">
                                <details>
                                  <summary className="cursor-pointer font-medium">
                                    View Details
                                  </summary>
                                  <pre className="mt-1 text-xs overflow-x-auto">
                                    {JSON.stringify(notification.data, null, 2)}
                                  </pre>
                                </details>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </ScrollArea>
          </Tabs>
        </CardContent>
      </Card>

      {/* Subscription Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Wifi className="w-5 h-5" />
            <span>WebSocket Subscriptions</span>
          </CardTitle>
          <CardDescription>
            Active notification topic subscriptions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
            {subscriptions.length === 0 ? (
              <div className="col-span-full text-center py-4 text-muted-foreground">
                No active subscriptions
              </div>
            ) : (
              subscriptions.map((subscription) => (
                <Badge key={subscription} variant="outline" className="justify-center">
                  {subscription}
                </Badge>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default NotificationPanel;

