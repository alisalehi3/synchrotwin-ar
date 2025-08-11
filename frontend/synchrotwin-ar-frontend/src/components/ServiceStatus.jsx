/**
 * Service Status Component
 * =======================
 * 
 * Monitor the health and status of all backend microservices.
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  RefreshCw, 
  Server, 
  Database,
  Brain,
  Eye,
  Activity,
  Zap,
  Bell,
  Clock,
  Wifi
} from 'lucide-react';
import { checkAllServicesHealth } from '../lib/api';

const ServiceStatus = ({ 
  servicesHealth = [], 
  isLoading = false, 
  detailed = false 
}) => {
  const [lastCheck, setLastCheck] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [healthHistory, setHealthHistory] = useState({});

  // Update health history when servicesHealth changes
  useEffect(() => {
    if (servicesHealth.length > 0) {
      const timestamp = new Date();
      setLastCheck(timestamp);
      
      setHealthHistory(prev => {
        const updated = { ...prev };
        servicesHealth.forEach(service => {
          if (!updated[service.name]) {
            updated[service.name] = [];
          }
          updated[service.name].push({
            timestamp,
            status: service.status,
            data: service.data
          });
          // Keep last 20 entries
          updated[service.name] = updated[service.name].slice(-20);
        });
        return updated;
      });
    }
  }, [servicesHealth]);

  const refreshHealth = async () => {
    setIsRefreshing(true);
    try {
      await checkAllServicesHealth();
    } catch (error) {
      console.error('Failed to refresh health:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  const getServiceIcon = (serviceName) => {
    switch (serviceName.toLowerCase()) {
      case 'digital twin': return <Database className="w-4 h-4" />;
      case 'synchrony analysis': return <Brain className="w-4 h-4" />;
      case 'ar biofeedback': return <Eye className="w-4 h-4" />;
      case 'data ingestion': return <Activity className="w-4 h-4" />;
      case 'notification': return <Bell className="w-4 h-4" />;
      default: return <Server className="w-4 h-4" />;
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy': return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'unhealthy': return <XCircle className="w-4 h-4 text-red-500" />;
      default: return <AlertCircle className="w-4 h-4 text-yellow-500" />;
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'healthy': return { variant: 'default', color: 'text-green-600' };
      case 'unhealthy': return { variant: 'destructive', color: 'text-red-600' };
      default: return { variant: 'secondary', color: 'text-yellow-600' };
    }
  };

  const calculateUptime = (serviceName) => {
    const history = healthHistory[serviceName] || [];
    if (history.length === 0) return 0;
    
    const healthyCount = history.filter(entry => entry.status === 'healthy').length;
    return (healthyCount / history.length) * 100;
  };

  const getServiceEndpoint = (serviceName) => {
    const endpoints = {
      'Digital Twin': 'http://localhost:5000',
      'Synchrony Analysis': 'http://localhost:5001',
      'AR Biofeedback': 'http://localhost:5002',
      'Data Ingestion': 'http://localhost:5003',
      'Notification': 'http://localhost:5004'
    };
    return endpoints[serviceName] || 'Unknown';
  };

  const healthyServices = servicesHealth.filter(service => service.status === 'healthy').length;
  const totalServices = servicesHealth.length;
  const overallHealth = totalServices > 0 ? (healthyServices / totalServices) * 100 : 0;

  if (!detailed) {
    // Compact view for overview
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Server className="w-5 h-5" />
              <span>Service Status</span>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={refreshHealth}
              disabled={isRefreshing || isLoading}
            >
              <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            </Button>
          </CardTitle>
          <CardDescription>
            Backend microservices health monitoring
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Overall Health */}
          <div className="text-center space-y-2">
            <div className="text-2xl font-bold">
              {overallHealth.toFixed(0)}%
            </div>
            <div className="text-sm text-muted-foreground">
              {healthyServices}/{totalServices} services healthy
            </div>
            <Progress value={overallHealth} className="h-2" />
          </div>

          {/* Service List */}
          <div className="space-y-2">
            {isLoading ? (
              <div className="text-center py-4 text-muted-foreground">
                Checking services...
              </div>
            ) : servicesHealth.length === 0 ? (
              <div className="text-center py-4 text-muted-foreground">
                No service data available
              </div>
            ) : (
              servicesHealth.map((service) => {
                const statusBadge = getStatusBadge(service.status);
                return (
                  <div
                    key={service.name}
                    className="flex items-center justify-between p-2 border rounded"
                  >
                    <div className="flex items-center space-x-2">
                      {getServiceIcon(service.name)}
                      <span className="text-sm font-medium">{service.name}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      {getStatusIcon(service.status)}
                      <Badge variant={statusBadge.variant} className="text-xs">
                        {service.status}
                      </Badge>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Last Check */}
          {lastCheck && (
            <div className="text-xs text-muted-foreground text-center">
              Last checked: {lastCheck.toLocaleTimeString()}
            </div>
          )}
        </CardContent>
      </Card>
    );
  }

  // Detailed view
  return (
    <div className="space-y-6">
      {/* Overall Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Server className="w-5 h-5" />
              <span>System Health Overview</span>
            </div>
            <Button
              variant="outline"
              onClick={refreshHealth}
              disabled={isRefreshing || isLoading}
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-3xl font-bold">{overallHealth.toFixed(0)}%</div>
              <p className="text-sm text-muted-foreground">Overall Health</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">{healthyServices}</div>
              <p className="text-sm text-muted-foreground">Healthy Services</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-red-600">
                {totalServices - healthyServices}
              </div>
              <p className="text-sm text-muted-foreground">Unhealthy Services</p>
            </div>
          </div>
          
          <div className="mt-4">
            <Progress value={overallHealth} className="h-3" />
          </div>
        </CardContent>
      </Card>

      {/* Detailed Service Status */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {isLoading ? (
          <Card className="lg:col-span-2">
            <CardContent className="text-center py-8">
              <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-2" />
              <p className="text-muted-foreground">Checking service health...</p>
            </CardContent>
          </Card>
        ) : servicesHealth.length === 0 ? (
          <Card className="lg:col-span-2">
            <CardContent className="text-center py-8">
              <AlertCircle className="w-8 h-8 mx-auto mb-2 text-yellow-500" />
              <p className="text-muted-foreground">No service data available</p>
            </CardContent>
          </Card>
        ) : (
          servicesHealth.map((service) => {
            const statusBadge = getStatusBadge(service.status);
            const uptime = calculateUptime(service.name);
            
            return (
              <Card key={service.name}>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {getServiceIcon(service.name)}
                      <span>{service.name}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      {getStatusIcon(service.status)}
                      <Badge variant={statusBadge.variant}>
                        {service.status}
                      </Badge>
                    </div>
                  </CardTitle>
                  <CardDescription>
                    {getServiceEndpoint(service.name)}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Service Details */}
                  {service.data && (
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Service:</span>
                        <span className="font-medium">{service.data.service || 'Unknown'}</span>
                      </div>
                      
                      {service.data.timestamp && (
                        <div className="flex justify-between text-sm">
                          <span>Last Response:</span>
                          <span className="font-medium">
                            {new Date(service.data.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                      )}
                      
                      {service.data.total_streams !== undefined && (
                        <div className="flex justify-between text-sm">
                          <span>Active Streams:</span>
                          <span className="font-medium">{service.data.total_streams}</span>
                        </div>
                      )}
                      
                      {service.data.connected_clients !== undefined && (
                        <div className="flex justify-between text-sm">
                          <span>Connected Clients:</span>
                          <span className="font-medium">{service.data.connected_clients}</span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Uptime */}
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Uptime (last 20 checks):</span>
                      <span className="font-medium">{uptime.toFixed(1)}%</span>
                    </div>
                    <Progress value={uptime} className="h-2" />
                  </div>

                  {/* Error Information */}
                  {service.status === 'unhealthy' && service.error && (
                    <div className="p-2 bg-red-50 border border-red-200 rounded text-sm">
                      <div className="font-medium text-red-800">Error:</div>
                      <div className="text-red-600">{service.error}</div>
                    </div>
                  )}

                  {/* Health History Indicator */}
                  <div className="space-y-2">
                    <div className="text-sm font-medium">Recent Health History</div>
                    <div className="flex space-x-1">
                      {(healthHistory[service.name] || []).slice(-10).map((entry, index) => (
                        <div
                          key={index}
                          className={`w-3 h-3 rounded-full ${
                            entry.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
                          }`}
                          title={`${entry.status} at ${entry.timestamp.toLocaleTimeString()}`}
                        />
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })
        )}
      </div>

      {/* System Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Clock className="w-5 h-5" />
            <span>System Information</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <p className="text-sm font-medium">Last Health Check</p>
              <p className="text-sm text-muted-foreground">
                {lastCheck ? lastCheck.toLocaleString() : 'Never'}
              </p>
            </div>
            <div>
              <p className="text-sm font-medium">Total Services</p>
              <p className="text-sm text-muted-foreground">{totalServices}</p>
            </div>
            <div>
              <p className="text-sm font-medium">Monitoring Status</p>
              <div className="flex items-center space-x-1">
                <Wifi className="w-3 h-3 text-green-500" />
                <span className="text-sm text-muted-foreground">Active</span>
              </div>
            </div>
            <div>
              <p className="text-sm font-medium">Auto Refresh</p>
              <p className="text-sm text-muted-foreground">Every 30 seconds</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ServiceStatus;

