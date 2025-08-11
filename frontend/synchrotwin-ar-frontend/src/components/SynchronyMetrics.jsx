/**
 * Synchrony Metrics Component
 * ==========================
 * 
 * Real-time visualization of neural synchrony metrics (PLV, CRQA, fNIRS).
 */

import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area,
  RadialBarChart,
  RadialBar,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { 
  Brain, 
  Activity, 
  Zap, 
  TrendingUp, 
  TrendingDown,
  Minus,
  Info
} from 'lucide-react';

const SynchronyMetrics = ({ 
  synchronyData, 
  lastUpdate, 
  isSessionActive = false, 
  detailed = false 
}) => {
  const [historicalData, setHistoricalData] = useState([]);
  const [selectedMetric, setSelectedMetric] = useState('plv');
  
  // Add new data to historical tracking
  useEffect(() => {
    if (synchronyData && lastUpdate) {
      const newDataPoint = {
        timestamp: lastUpdate.getTime(),
        time: lastUpdate.toLocaleTimeString(),
        plv: synchronyData.plv || 0,
        crqa_determinism: synchronyData.crqa_determinism || 0,
        fnirs_coherence: synchronyData.fnirs_coherence || 0
      };
      
      setHistoricalData(prev => {
        const updated = [...prev, newDataPoint];
        // Keep last 50 data points
        return updated.slice(-50);
      });
    }
  }, [synchronyData, lastUpdate]);

  // Calculate synchrony level and trend
  const synchronyLevel = useMemo(() => {
    if (!synchronyData) return { level: 0, label: 'No Data', color: 'gray' };
    
    const plv = synchronyData.plv || 0;
    
    if (plv >= 0.8) return { level: plv, label: 'Very High', color: '#22c55e' };
    if (plv >= 0.6) return { level: plv, label: 'High', color: '#84cc16' };
    if (plv >= 0.4) return { level: plv, label: 'Moderate', color: '#eab308' };
    if (plv >= 0.2) return { level: plv, label: 'Low', color: '#f97316' };
    return { level: plv, label: 'Very Low', color: '#ef4444' };
  }, [synchronyData]);

  // Calculate trend
  const trend = useMemo(() => {
    if (historicalData.length < 2) return 'stable';
    
    const recent = historicalData.slice(-5);
    const current = recent[recent.length - 1]?.plv || 0;
    const previous = recent[0]?.plv || 0;
    
    const change = current - previous;
    if (Math.abs(change) < 0.05) return 'stable';
    return change > 0 ? 'increasing' : 'decreasing';
  }, [historicalData]);

  const getTrendIcon = () => {
    switch (trend) {
      case 'increasing': return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'decreasing': return <TrendingDown className="w-4 h-4 text-red-500" />;
      default: return <Minus className="w-4 h-4 text-gray-500" />;
    }
  };

  // Prepare data for radial chart
  const radialData = [
    {
      name: 'PLV',
      value: (synchronyData?.plv || 0) * 100,
      fill: '#8884d8'
    }
  ];

  // Prepare data for pie chart (all metrics)
  const pieData = [
    {
      name: 'PLV',
      value: (synchronyData?.plv || 0) * 100,
      fill: '#8884d8'
    },
    {
      name: 'CRQA',
      value: (synchronyData?.crqa_determinism || 0) * 100,
      fill: '#82ca9d'
    },
    {
      name: 'fNIRS',
      value: (synchronyData?.fnirs_coherence || 0) * 100,
      fill: '#ffc658'
    }
  ];

  const COLORS = ['#8884d8', '#82ca9d', '#ffc658'];

  if (!detailed) {
    // Compact view for overview
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Brain className="w-5 h-5" />
            <span>Neural Synchrony</span>
            {getTrendIcon()}
          </CardTitle>
          <CardDescription>
            Real-time synchrony metrics between participants
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Main Synchrony Level */}
          <div className="text-center space-y-2">
            <div className="text-3xl font-bold" style={{ color: synchronyLevel.color }}>
              {(synchronyLevel.level * 100).toFixed(1)}%
            </div>
            <Badge variant="outline" style={{ borderColor: synchronyLevel.color }}>
              {synchronyLevel.label}
            </Badge>
          </div>

          {/* Progress Bars */}
          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Phase-Locking Value (PLV)</span>
                <span>{((synchronyData?.plv || 0) * 100).toFixed(1)}%</span>
              </div>
              <Progress value={(synchronyData?.plv || 0) * 100} className="h-2" />
            </div>
            
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>CRQA Determinism</span>
                <span>{((synchronyData?.crqa_determinism || 0) * 100).toFixed(1)}%</span>
              </div>
              <Progress value={(synchronyData?.crqa_determinism || 0) * 100} className="h-2" />
            </div>
            
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>fNIRS Coherence</span>
                <span>{((synchronyData?.fnirs_coherence || 0) * 100).toFixed(1)}%</span>
              </div>
              <Progress value={(synchronyData?.fnirs_coherence || 0) * 100} className="h-2" />
            </div>
          </div>

          {/* Last Update */}
          <div className="text-xs text-muted-foreground text-center">
            {lastUpdate 
              ? `Last updated: ${lastUpdate.toLocaleTimeString()}`
              : 'No data received'
            }
          </div>

          {/* Mini Chart */}
          {historicalData.length > 0 && (
            <div className="h-20">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={historicalData}>
                  <Line 
                    type="monotone" 
                    dataKey="plv" 
                    stroke="#8884d8" 
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </CardContent>
      </Card>
    );
  }

  // Detailed view
  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">PLV Synchrony</CardTitle>
            <Brain className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {((synchronyData?.plv || 0) * 100).toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground">
              Phase-locking value
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">CRQA Determinism</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {((synchronyData?.crqa_determinism || 0) * 100).toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground">
              Cross-recurrence analysis
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">fNIRS Coherence</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {((synchronyData?.fnirs_coherence || 0) * 100).toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground">
              Functional connectivity
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Time Series Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Synchrony Over Time</CardTitle>
            <CardDescription>
              Real-time tracking of synchrony metrics
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs value={selectedMetric} onValueChange={setSelectedMetric}>
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="plv">PLV</TabsTrigger>
                <TabsTrigger value="crqa_determinism">CRQA</TabsTrigger>
                <TabsTrigger value="fnirs_coherence">fNIRS</TabsTrigger>
              </TabsList>
              
              <div className="h-64 mt-4">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={historicalData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="time" 
                      tick={{ fontSize: 12 }}
                      interval="preserveStartEnd"
                    />
                    <YAxis 
                      domain={[0, 1]}
                      tick={{ fontSize: 12 }}
                    />
                    <Tooltip 
                      formatter={(value) => [`${(value * 100).toFixed(1)}%`, selectedMetric.toUpperCase()]}
                      labelFormatter={(label) => `Time: ${label}`}
                    />
                    <Area
                      type="monotone"
                      dataKey={selectedMetric}
                      stroke={COLORS[['plv', 'crqa_determinism', 'fnirs_coherence'].indexOf(selectedMetric)]}
                      fill={COLORS[['plv', 'crqa_determinism', 'fnirs_coherence'].indexOf(selectedMetric)]}
                      fillOpacity={0.3}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </Tabs>
          </CardContent>
        </Card>

        {/* Radial Progress */}
        <Card>
          <CardHeader>
            <CardTitle>Current Synchrony Level</CardTitle>
            <CardDescription>
              Overall synchrony status and distribution
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Radial Chart */}
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <RadialBarChart cx="50%" cy="50%" innerRadius="60%" outerRadius="90%" data={radialData}>
                    <RadialBar
                      dataKey="value"
                      cornerRadius={10}
                      fill={synchronyLevel.color}
                    />
                    <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle" className="text-2xl font-bold">
                      {(synchronyLevel.level * 100).toFixed(0)}%
                    </text>
                  </RadialBarChart>
                </ResponsiveContainer>
              </div>

              {/* Metrics Distribution */}
              <div className="h-32">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={20}
                      outerRadius={50}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `${value.toFixed(1)}%`} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Status Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Info className="w-5 h-5" />
            <span>Synchrony Analysis Status</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <p className="text-sm font-medium">Session Status</p>
              <Badge variant={isSessionActive ? "default" : "secondary"}>
                {isSessionActive ? "Active" : "Inactive"}
              </Badge>
            </div>
            <div>
              <p className="text-sm font-medium">Data Points</p>
              <p className="text-sm text-muted-foreground">{historicalData.length}</p>
            </div>
            <div>
              <p className="text-sm font-medium">Trend</p>
              <div className="flex items-center space-x-1">
                {getTrendIcon()}
                <span className="text-sm text-muted-foreground capitalize">{trend}</span>
              </div>
            </div>
            <div>
              <p className="text-sm font-medium">Last Update</p>
              <p className="text-sm text-muted-foreground">
                {lastUpdate ? lastUpdate.toLocaleTimeString() : 'No data'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SynchronyMetrics;

