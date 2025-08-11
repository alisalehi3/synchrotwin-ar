/**
 * Data Stream Monitor Component
 * ============================
 * 
 * Real-time monitoring and management of biosignal data streams.
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';
import { 
  Activity, 
  Play, 
  Pause, 
  Square, 
  Plus, 
  Trash2, 
  Settings,
  Wifi,
  WifiOff,
  Database,
  Zap,
  Brain,
  Heart,
  Eye
} from 'lucide-react';
import { dataIngestionService } from '../lib/api';
import { useStreamUpdates } from '../hooks/useWebSocket';

const DataStreamMonitor = ({ isSessionActive = false }) => {
  const [streams, setStreams] = useState([]);
  const [selectedStream, setSelectedStream] = useState(null);
  const [streamData, setStreamData] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [newStreamConfig, setNewStreamConfig] = useState({
    stream_id: '',
    data_type: 'eeg',
    sampling_rate: 1000,
    channels: ['ch1', 'ch2'],
    buffer_size: 10000,
    auto_analysis: true
  });

  const { streamData: realtimeStreamData } = useStreamUpdates();

  // Load streams on mount
  useEffect(() => {
    loadStreams();
    const interval = setInterval(loadStreams, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  // Load stream data when a stream is selected
  useEffect(() => {
    if (selectedStream) {
      loadStreamData(selectedStream);
    }
  }, [selectedStream]);

  const loadStreams = async () => {
    try {
      const response = await dataIngestionService.listStreams();
      setStreams(response.data.streams);
    } catch (error) {
      console.error('Failed to load streams:', error);
    }
  };

  const loadStreamData = async (streamId) => {
    try {
      const response = await dataIngestionService.getStreamData(streamId, [], 100);
      setStreamData(prev => ({
        ...prev,
        [streamId]: response.data.data
      }));
    } catch (error) {
      console.error('Failed to load stream data:', error);
    }
  };

  const createStream = async () => {
    try {
      setIsLoading(true);
      const streamId = newStreamConfig.stream_id || `stream_${Date.now()}`;
      await dataIngestionService.createStream(streamId, {
        ...newStreamConfig,
        stream_id: streamId
      });
      
      // Reset form
      setNewStreamConfig({
        stream_id: '',
        data_type: 'eeg',
        sampling_rate: 1000,
        channels: ['ch1', 'ch2'],
        buffer_size: 10000,
        auto_analysis: true
      });
      
      await loadStreams();
    } catch (error) {
      console.error('Failed to create stream:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const startStream = async (streamId) => {
    try {
      await dataIngestionService.startStream(streamId);
      await loadStreams();
    } catch (error) {
      console.error('Failed to start stream:', error);
    }
  };

  const stopStream = async (streamId) => {
    try {
      await dataIngestionService.stopStream(streamId);
      await loadStreams();
    } catch (error) {
      console.error('Failed to stop stream:', error);
    }
  };

  const deleteStream = async (streamId) => {
    try {
      await dataIngestionService.deleteStream(streamId);
      if (selectedStream === streamId) {
        setSelectedStream(null);
      }
      await loadStreams();
    } catch (error) {
      console.error('Failed to delete stream:', error);
    }
  };

  // Generate sample data for demonstration
  const generateSampleData = async (streamId) => {
    try {
      const sampleData = {
        channels: {
          ch1: Array.from({ length: 100 }, () => Math.random() * 100 - 50),
          ch2: Array.from({ length: 100 }, () => Math.random() * 100 - 50)
        },
        samples: 100,
        timestamp: new Date().toISOString()
      };
      
      await dataIngestionService.ingestData(streamId, sampleData.channels, sampleData.samples);
      await loadStreamData(streamId);
    } catch (error) {
      console.error('Failed to generate sample data:', error);
    }
  };

  const getDataTypeIcon = (dataType) => {
    switch (dataType) {
      case 'eeg': return <Brain className="w-4 h-4" />;
      case 'fnirs': return <Eye className="w-4 h-4" />;
      case 'ecg': return <Heart className="w-4 h-4" />;
      case 'emg': return <Zap className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  const getStreamStatus = (stream) => {
    if (stream.is_running) return { status: 'running', color: 'default', icon: <Wifi className="w-3 h-3" /> };
    return { status: 'stopped', color: 'secondary', icon: <WifiOff className="w-3 h-3" /> };
  };

  // Prepare chart data
  const prepareChartData = (data) => {
    if (!data || !data.ch1 || !data.ch2) return [];
    
    return data.ch1.map((value, index) => ({
      index,
      ch1: value,
      ch2: data.ch2[index] || 0
    }));
  };

  return (
    <div className="space-y-6">
      {/* Stream Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Streams</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{streams.length}</div>
            <p className="text-xs text-muted-foreground">
              Active data streams
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Running Streams</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {streams.filter(s => s.is_running).length}
            </div>
            <p className="text-xs text-muted-foreground">
              Currently processing
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Data Points</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {streams.reduce((total, stream) => total + (stream.total_samples || 0), 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              Total samples processed
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs defaultValue="streams" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="streams">Stream Management</TabsTrigger>
          <TabsTrigger value="monitor">Real-time Monitor</TabsTrigger>
          <TabsTrigger value="create">Create Stream</TabsTrigger>
        </TabsList>

        {/* Stream Management Tab */}
        <TabsContent value="streams" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Data Streams</CardTitle>
              <CardDescription>
                Manage and monitor all active data streams
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {streams.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    No data streams found. Create a new stream to get started.
                  </div>
                ) : (
                  streams.map((stream) => {
                    const status = getStreamStatus(stream);
                    return (
                      <div
                        key={stream.stream_id}
                        className="flex items-center justify-between p-4 border rounded-lg"
                      >
                        <div className="flex items-center space-x-4">
                          {getDataTypeIcon(stream.info?.config?.data_type)}
                          <div>
                            <h4 className="font-medium">{stream.stream_id}</h4>
                            <p className="text-sm text-muted-foreground">
                              {stream.info?.config?.data_type?.toUpperCase()} • 
                              {stream.info?.config?.sampling_rate}Hz • 
                              {stream.total_samples || 0} samples
                            </p>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <Badge variant={status.color} className="flex items-center space-x-1">
                            {status.icon}
                            <span>{status.status}</span>
                          </Badge>
                          
                          <div className="flex items-center space-x-1">
                            {stream.is_running ? (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => stopStream(stream.stream_id)}
                              >
                                <Pause className="w-4 h-4" />
                              </Button>
                            ) : (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => startStream(stream.stream_id)}
                              >
                                <Play className="w-4 h-4" />
                              </Button>
                            )}
                            
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => generateSampleData(stream.stream_id)}
                              disabled={!stream.is_running}
                            >
                              <Zap className="w-4 h-4" />
                            </Button>
                            
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => setSelectedStream(stream.stream_id)}
                            >
                              <Eye className="w-4 h-4" />
                            </Button>
                            
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => deleteStream(stream.stream_id)}
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Real-time Monitor Tab */}
        <TabsContent value="monitor" className="space-y-4">
          {selectedStream ? (
            <Card>
              <CardHeader>
                <CardTitle>Stream Monitor: {selectedStream}</CardTitle>
                <CardDescription>
                  Real-time data visualization and analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Stream Info */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                      <p className="text-sm font-medium">Status</p>
                      <Badge variant="default">
                        {streams.find(s => s.stream_id === selectedStream)?.is_running ? 'Running' : 'Stopped'}
                      </Badge>
                    </div>
                    <div>
                      <p className="text-sm font-medium">Samples</p>
                      <p className="text-sm text-muted-foreground">
                        {streams.find(s => s.stream_id === selectedStream)?.total_samples || 0}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium">Buffer Usage</p>
                      <Progress 
                        value={
                          (streams.find(s => s.stream_id === selectedStream)?.total_samples || 0) / 
                          (streams.find(s => s.stream_id === selectedStream)?.info?.config?.buffer_size || 1) * 100
                        } 
                        className="h-2 mt-1" 
                      />
                    </div>
                    <div>
                      <p className="text-sm font-medium">Last Update</p>
                      <p className="text-sm text-muted-foreground">
                        {streams.find(s => s.stream_id === selectedStream)?.info?.last_updated 
                          ? new Date(streams.find(s => s.stream_id === selectedStream).info.last_updated).toLocaleTimeString()
                          : 'No data'
                        }
                      </p>
                    </div>
                  </div>

                  {/* Data Visualization */}
                  {streamData[selectedStream] && (
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={prepareChartData(streamData[selectedStream])}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="index" />
                          <YAxis />
                          <Tooltip />
                          <Line 
                            type="monotone" 
                            dataKey="ch1" 
                            stroke="#8884d8" 
                            strokeWidth={1}
                            dot={false}
                            name="Channel 1"
                          />
                          <Line 
                            type="monotone" 
                            dataKey="ch2" 
                            stroke="#82ca9d" 
                            strokeWidth={1}
                            dot={false}
                            name="Channel 2"
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  )}

                  {/* Controls */}
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      onClick={() => loadStreamData(selectedStream)}
                    >
                      Refresh Data
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => generateSampleData(selectedStream)}
                      disabled={!streams.find(s => s.stream_id === selectedStream)?.is_running}
                    >
                      Generate Sample Data
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="text-center py-8">
                <p className="text-muted-foreground">
                  Select a stream from the Stream Management tab to monitor its data.
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Create Stream Tab */}
        <TabsContent value="create" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Create New Data Stream</CardTitle>
              <CardDescription>
                Configure a new biosignal data stream for real-time processing
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="stream-id">Stream ID</Label>
                    <Input
                      id="stream-id"
                      placeholder="Enter stream ID (optional)"
                      value={newStreamConfig.stream_id}
                      onChange={(e) => setNewStreamConfig(prev => ({
                        ...prev,
                        stream_id: e.target.value
                      }))}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Data Type</Label>
                    <Select
                      value={newStreamConfig.data_type}
                      onValueChange={(value) => setNewStreamConfig(prev => ({
                        ...prev,
                        data_type: value
                      }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="eeg">EEG (Electroencephalography)</SelectItem>
                        <SelectItem value="fnirs">fNIRS (Functional Near-Infrared Spectroscopy)</SelectItem>
                        <SelectItem value="ecg">ECG (Electrocardiography)</SelectItem>
                        <SelectItem value="emg">EMG (Electromyography)</SelectItem>
                        <SelectItem value="gsr">GSR (Galvanic Skin Response)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="sampling-rate">Sampling Rate (Hz)</Label>
                    <Input
                      id="sampling-rate"
                      type="number"
                      value={newStreamConfig.sampling_rate}
                      onChange={(e) => setNewStreamConfig(prev => ({
                        ...prev,
                        sampling_rate: parseInt(e.target.value) || 1000
                      }))}
                    />
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="channels">Channels (comma-separated)</Label>
                    <Input
                      id="channels"
                      placeholder="ch1, ch2, ch3"
                      value={newStreamConfig.channels.join(', ')}
                      onChange={(e) => setNewStreamConfig(prev => ({
                        ...prev,
                        channels: e.target.value.split(',').map(ch => ch.trim()).filter(ch => ch)
                      }))}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="buffer-size">Buffer Size</Label>
                    <Input
                      id="buffer-size"
                      type="number"
                      value={newStreamConfig.buffer_size}
                      onChange={(e) => setNewStreamConfig(prev => ({
                        ...prev,
                        buffer_size: parseInt(e.target.value) || 10000
                      }))}
                    />
                  </div>

                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="auto-analysis"
                      checked={newStreamConfig.auto_analysis}
                      onChange={(e) => setNewStreamConfig(prev => ({
                        ...prev,
                        auto_analysis: e.target.checked
                      }))}
                    />
                    <Label htmlFor="auto-analysis">Enable automatic analysis</Label>
                  </div>
                </div>
              </div>

              <div className="mt-6">
                <Button
                  onClick={createStream}
                  disabled={isLoading}
                  className="w-full"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  {isLoading ? 'Creating...' : 'Create Stream'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default DataStreamMonitor;

