/**
 * Main Dashboard Component
 * =======================
 * 
 * Central dashboard for SynchroTwin-AR system monitoring and control.
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Alert, AlertDescription } from './ui/alert';
import { 
  Activity, 
  Brain, 
  Users, 
  Wifi, 
  WifiOff, 
  Play, 
  Pause, 
  Settings,
  BarChart3,
  Zap,
  Eye
} from 'lucide-react';
import { useWebSocket, useSynchronyUpdates, useBiofeedbackUpdates } from '../hooks/useWebSocket';
import { checkAllServicesHealth } from '../lib/api';
import SynchronyMetrics from './SynchronyMetrics';
import BiofeedbackControls from './BiofeedbackControls';
import DataStreamMonitor from './DataStreamMonitor';
import ServiceStatus from './ServiceStatus';
import NotificationPanel from './NotificationPanel';
import '../App.css';

const Dashboard = () => {
  const [servicesHealth, setServicesHealth] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeSession, setActiveSession] = useState(null);
  const [systemStatus, setSystemStatus] = useState('idle'); // idle, running, paused, error
  
  const { 
    isConnected, 
    sessionId, 
    subscriptions, 
    connectionError, 
    notifications 
  } = useWebSocket(true);
  
  const { synchronyData, lastUpdate: synchronyLastUpdate } = useSynchronyUpdates();
  const { biofeedbackState, lastUpdate: biofeedbackLastUpdate } = useBiofeedbackUpdates();

  // Check services health on mount
  useEffect(() => {
    const checkHealth = async () => {
      setIsLoading(true);
      try {
        const healthResults = await checkAllServicesHealth();
        setServicesHealth(healthResults);
      } catch (error) {
        console.error('Failed to check services health:', error);
      } finally {
        setIsLoading(false);
      }
    };

    checkHealth();
    
    // Check health every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  // Calculate overall system health
  const healthyServices = servicesHealth.filter(service => service.status === 'healthy').length;
  const totalServices = servicesHealth.length;
  const systemHealthPercentage = totalServices > 0 ? (healthyServices / totalServices) * 100 : 0;

  // Get connection status
  const getConnectionStatus = () => {
    if (!isConnected) return { status: 'disconnected', color: 'destructive' };
    if (connectionError) return { status: 'error', color: 'destructive' };
    return { status: 'connected', color: 'default' };
  };

  const connectionStatus = getConnectionStatus();

  // Handle session control
  const handleStartSession = () => {
    setSystemStatus('running');
    setActiveSession({
      id: `session_${Date.now()}`,
      startTime: new Date(),
      participants: 2
    });
  };

  const handlePauseSession = () => {
    setSystemStatus('paused');
  };

  const handleStopSession = () => {
    setSystemStatus('idle');
    setActiveSession(null);
  };

  // Get recent notifications count
  const recentNotifications = notifications.filter(
    notification => new Date() - new Date(notification.timestamp) < 5 * 60 * 1000 // Last 5 minutes
  ).length;

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">SynchroTwin-AR Dashboard</h1>
            <p className="text-muted-foreground">
              Real-time neural synchrony monitoring and AR biofeedback control
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Connection Status */}
            <Badge variant={connectionStatus.color} className="flex items-center space-x-1">
              {isConnected ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
              <span>{connectionStatus.status}</span>
            </Badge>
            
            {/* Session Controls */}
            <div className="flex items-center space-x-2">
              {systemStatus === 'idle' && (
                <Button onClick={handleStartSession} className="flex items-center space-x-1">
                  <Play className="w-4 h-4" />
                  <span>Start Session</span>
                </Button>
              )}
              
              {systemStatus === 'running' && (
                <>
                  <Button 
                    variant="outline" 
                    onClick={handlePauseSession}
                    className="flex items-center space-x-1"
                  >
                    <Pause className="w-4 h-4" />
                    <span>Pause</span>
                  </Button>
                  <Button 
                    variant="destructive" 
                    onClick={handleStopSession}
                    className="flex items-center space-x-1"
                  >
                    <span>Stop Session</span>
                  </Button>
                </>
              )}
              
              {systemStatus === 'paused' && (
                <>
                  <Button 
                    onClick={() => setSystemStatus('running')}
                    className="flex items-center space-x-1"
                  >
                    <Play className="w-4 h-4" />
                    <span>Resume</span>
                  </Button>
                  <Button 
                    variant="destructive" 
                    onClick={handleStopSession}
                    className="flex items-center space-x-1"
                  >
                    <span>Stop Session</span>
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>

        {/* System Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* System Health */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">System Health</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {systemHealthPercentage.toFixed(0)}%
              </div>
              <p className="text-xs text-muted-foreground">
                {healthyServices}/{totalServices} services healthy
              </p>
            </CardContent>
          </Card>

          {/* Active Session */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Session</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {activeSession ? 'Running' : 'None'}
              </div>
              <p className="text-xs text-muted-foreground">
                {activeSession 
                  ? `${activeSession.participants} participants`
                  : 'No active session'
                }
              </p>
            </CardContent>
          </Card>

          {/* Synchrony Level */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Synchrony Level</CardTitle>
              <Brain className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {synchronyData?.plv ? (synchronyData.plv * 100).toFixed(1) + '%' : 'N/A'}
              </div>
              <p className="text-xs text-muted-foreground">
                {synchronyLastUpdate 
                  ? `Updated ${synchronyLastUpdate.toLocaleTimeString()}`
                  : 'No data'
                }
              </p>
            </CardContent>
          </Card>

          {/* Notifications */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Notifications</CardTitle>
              <Zap className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{recentNotifications}</div>
              <p className="text-xs text-muted-foreground">
                Last 5 minutes
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Connection Error Alert */}
        {connectionError && (
          <Alert variant="destructive">
            <WifiOff className="h-4 w-4" />
            <AlertDescription>
              Connection Error: {connectionError}
            </AlertDescription>
          </Alert>
        )}

        {/* Main Content Tabs */}
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="overview" className="flex items-center space-x-1">
              <BarChart3 className="w-4 h-4" />
              <span>Overview</span>
            </TabsTrigger>
            <TabsTrigger value="synchrony" className="flex items-center space-x-1">
              <Brain className="w-4 h-4" />
              <span>Synchrony</span>
            </TabsTrigger>
            <TabsTrigger value="biofeedback" className="flex items-center space-x-1">
              <Eye className="w-4 h-4" />
              <span>Biofeedback</span>
            </TabsTrigger>
            <TabsTrigger value="streams" className="flex items-center space-x-1">
              <Activity className="w-4 h-4" />
              <span>Data Streams</span>
            </TabsTrigger>
            <TabsTrigger value="system" className="flex items-center space-x-1">
              <Settings className="w-4 h-4" />
              <span>System</span>
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <SynchronyMetrics 
                synchronyData={synchronyData}
                lastUpdate={synchronyLastUpdate}
                isSessionActive={systemStatus === 'running'}
              />
              <BiofeedbackControls 
                biofeedbackState={biofeedbackState}
                lastUpdate={biofeedbackLastUpdate}
                isSessionActive={systemStatus === 'running'}
                onConfigChange={(config) => console.log('Biofeedback config changed:', config)}
              />
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ServiceStatus 
                servicesHealth={servicesHealth}
                isLoading={isLoading}
              />
              <NotificationPanel 
                notifications={notifications.slice(0, 10)}
                isConnected={isConnected}
                subscriptions={subscriptions}
              />
            </div>
          </TabsContent>

          {/* Synchrony Tab */}
          <TabsContent value="synchrony" className="space-y-4">
            <SynchronyMetrics 
              synchronyData={synchronyData}
              lastUpdate={synchronyLastUpdate}
              isSessionActive={systemStatus === 'running'}
              detailed={true}
            />
          </TabsContent>

          {/* Biofeedback Tab */}
          <TabsContent value="biofeedback" className="space-y-4">
            <BiofeedbackControls 
              biofeedbackState={biofeedbackState}
              lastUpdate={biofeedbackLastUpdate}
              isSessionActive={systemStatus === 'running'}
              onConfigChange={(config) => console.log('Biofeedback config changed:', config)}
              detailed={true}
            />
          </TabsContent>

          {/* Data Streams Tab */}
          <TabsContent value="streams" className="space-y-4">
            <DataStreamMonitor 
              isSessionActive={systemStatus === 'running'}
            />
          </TabsContent>

          {/* System Tab */}
          <TabsContent value="system" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ServiceStatus 
                servicesHealth={servicesHealth}
                isLoading={isLoading}
                detailed={true}
              />
              <NotificationPanel 
                notifications={notifications}
                isConnected={isConnected}
                subscriptions={subscriptions}
                detailed={true}
              />
            </div>
          </TabsContent>
        </Tabs>

        {/* Session Info */}
        {activeSession && (
          <Card>
            <CardHeader>
              <CardTitle>Session Information</CardTitle>
              <CardDescription>
                Current session details and statistics
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-sm font-medium">Session ID</p>
                  <p className="text-sm text-muted-foreground">{activeSession.id}</p>
                </div>
                <div>
                  <p className="text-sm font-medium">Start Time</p>
                  <p className="text-sm text-muted-foreground">
                    {activeSession.startTime.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium">Duration</p>
                  <p className="text-sm text-muted-foreground">
                    {Math.floor((new Date() - activeSession.startTime) / 1000 / 60)} minutes
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default Dashboard;

