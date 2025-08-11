/**
 * Biofeedback Controls Component
 * =============================
 * 
 * Interactive controls for AR biofeedback configuration and real-time state monitoring.
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Slider } from './ui/slider';
import { Switch } from './ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { 
  Eye, 
  Volume2, 
  Vibrate, 
  Palette, 
  Settings, 
  Play, 
  Pause,
  RotateCcw,
  Zap,
  Circle,
  Square,
  Triangle
} from 'lucide-react';
import { arBiofeedbackService } from '../lib/api';

const BiofeedbackControls = ({ 
  biofeedbackState, 
  lastUpdate, 
  isSessionActive = false, 
  onConfigChange,
  detailed = false 
}) => {
  const [config, setConfig] = useState({
    visual_feedback: {
      enabled: true,
      type: 'particles',
      intensity: 0.7,
      color_scheme: 'blue_green',
      particle_count: 100,
      animation_speed: 1.0
    },
    audio_feedback: {
      enabled: true,
      type: 'ambient',
      volume: 0.5,
      frequency_range: [200, 800]
    },
    haptic_feedback: {
      enabled: false,
      intensity: 0.3,
      pattern: 'pulse'
    },
    thresholds: {
      low: 0.3,
      medium: 0.6,
      high: 0.8
    },
    adaptation: {
      enabled: true,
      learning_rate: 0.1,
      adaptation_window: 30
    }
  });

  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);

  // Initialize session when component mounts
  useEffect(() => {
    if (isSessionActive && !sessionId) {
      initializeSession();
    }
  }, [isSessionActive]);

  const initializeSession = async () => {
    try {
      setIsLoading(true);
      const newSessionId = `biofeedback_${Date.now()}`;
      await arBiofeedbackService.createSession(newSessionId, config);
      setSessionId(newSessionId);
      onConfigChange?.(config);
    } catch (error) {
      console.error('Failed to initialize biofeedback session:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const updateConfig = async (newConfig) => {
    setConfig(newConfig);
    onConfigChange?.(newConfig);
    
    if (sessionId) {
      try {
        await arBiofeedbackService.updateSessionConfig(sessionId, newConfig);
      } catch (error) {
        console.error('Failed to update biofeedback config:', error);
      }
    }
  };

  const handleVisualConfigChange = (key, value) => {
    const newConfig = {
      ...config,
      visual_feedback: {
        ...config.visual_feedback,
        [key]: value
      }
    };
    updateConfig(newConfig);
  };

  const handleAudioConfigChange = (key, value) => {
    const newConfig = {
      ...config,
      audio_feedback: {
        ...config.audio_feedback,
        [key]: value
      }
    };
    updateConfig(newConfig);
  };

  const handleHapticConfigChange = (key, value) => {
    const newConfig = {
      ...config,
      haptic_feedback: {
        ...config.haptic_feedback,
        [key]: value
      }
    };
    updateConfig(newConfig);
  };

  const handleThresholdChange = (key, value) => {
    const newConfig = {
      ...config,
      thresholds: {
        ...config.thresholds,
        [key]: value[0] / 100 // Convert from percentage
      }
    };
    updateConfig(newConfig);
  };

  const resetToDefaults = async () => {
    try {
      const response = await arBiofeedbackService.getDefaultConfig();
      const defaultConfig = response.data.config;
      updateConfig(defaultConfig);
    } catch (error) {
      console.error('Failed to get default config:', error);
    }
  };

  // Get feedback status based on current state
  const getFeedbackStatus = () => {
    if (!biofeedbackState) return { status: 'inactive', color: 'secondary' };
    
    const intensity = biofeedbackState.visual_feedback?.intensity || 0;
    if (intensity >= 0.8) return { status: 'high', color: 'default' };
    if (intensity >= 0.5) return { status: 'medium', color: 'default' };
    if (intensity >= 0.2) return { status: 'low', color: 'secondary' };
    return { status: 'minimal', color: 'secondary' };
  };

  const feedbackStatus = getFeedbackStatus();

  if (!detailed) {
    // Compact view for overview
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Eye className="w-5 h-5" />
            <span>AR Biofeedback</span>
          </CardTitle>
          <CardDescription>
            Real-time biofeedback configuration and status
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Status */}
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Status</span>
            <Badge variant={feedbackStatus.color}>
              {feedbackStatus.status}
            </Badge>
          </div>

          {/* Quick Controls */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label htmlFor="visual-enabled" className="text-sm">Visual Feedback</Label>
              <Switch
                id="visual-enabled"
                checked={config.visual_feedback.enabled}
                onCheckedChange={(checked) => handleVisualConfigChange('enabled', checked)}
                disabled={!isSessionActive}
              />
            </div>

            <div className="flex items-center justify-between">
              <Label htmlFor="audio-enabled" className="text-sm">Audio Feedback</Label>
              <Switch
                id="audio-enabled"
                checked={config.audio_feedback.enabled}
                onCheckedChange={(checked) => handleAudioConfigChange('enabled', checked)}
                disabled={!isSessionActive}
              />
            </div>

            <div className="flex items-center justify-between">
              <Label htmlFor="haptic-enabled" className="text-sm">Haptic Feedback</Label>
              <Switch
                id="haptic-enabled"
                checked={config.haptic_feedback.enabled}
                onCheckedChange={(checked) => handleHapticConfigChange('enabled', checked)}
                disabled={!isSessionActive}
              />
            </div>
          </div>

          {/* Intensity Slider */}
          <div className="space-y-2">
            <Label className="text-sm">Visual Intensity</Label>
            <Slider
              value={[config.visual_feedback.intensity * 100]}
              onValueChange={(value) => handleVisualConfigChange('intensity', value[0] / 100)}
              max={100}
              step={1}
              disabled={!isSessionActive || !config.visual_feedback.enabled}
            />
            <div className="text-xs text-muted-foreground text-center">
              {(config.visual_feedback.intensity * 100).toFixed(0)}%
            </div>
          </div>

          {/* Current State */}
          {biofeedbackState && (
            <div className="text-xs text-muted-foreground space-y-1">
              <div>Current Intensity: {((biofeedbackState.visual_feedback?.intensity || 0) * 100).toFixed(0)}%</div>
              <div>Particle Count: {biofeedbackState.visual_feedback?.particle_count || 0}</div>
              <div>Last Update: {lastUpdate?.toLocaleTimeString() || 'No data'}</div>
            </div>
          )}
        </CardContent>
      </Card>
    );
  }

  // Detailed view
  return (
    <div className="space-y-6">
      {/* Status and Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Eye className="w-5 h-5" />
              <span>Biofeedback Control Center</span>
            </div>
            <div className="flex items-center space-x-2">
              <Badge variant={feedbackStatus.color}>
                {feedbackStatus.status}
              </Badge>
              <Button
                variant="outline"
                size="sm"
                onClick={resetToDefaults}
                disabled={isLoading}
              >
                <RotateCcw className="w-4 h-4 mr-1" />
                Reset
              </Button>
            </div>
          </CardTitle>
          <CardDescription>
            Configure and monitor AR biofeedback parameters in real-time
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="visual" className="space-y-4">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="visual" className="flex items-center space-x-1">
                <Eye className="w-4 h-4" />
                <span>Visual</span>
              </TabsTrigger>
              <TabsTrigger value="audio" className="flex items-center space-x-1">
                <Volume2 className="w-4 h-4" />
                <span>Audio</span>
              </TabsTrigger>
              <TabsTrigger value="haptic" className="flex items-center space-x-1">
                <Vibrate className="w-4 h-4" />
                <span>Haptic</span>
              </TabsTrigger>
              <TabsTrigger value="thresholds" className="flex items-center space-x-1">
                <Settings className="w-4 h-4" />
                <span>Thresholds</span>
              </TabsTrigger>
            </TabsList>

            {/* Visual Feedback Tab */}
            <TabsContent value="visual" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Label>Enable Visual Feedback</Label>
                    <Switch
                      checked={config.visual_feedback.enabled}
                      onCheckedChange={(checked) => handleVisualConfigChange('enabled', checked)}
                      disabled={!isSessionActive}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Feedback Type</Label>
                    <Select
                      value={config.visual_feedback.type}
                      onValueChange={(value) => handleVisualConfigChange('type', value)}
                      disabled={!isSessionActive || !config.visual_feedback.enabled}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="particles">
                          <div className="flex items-center space-x-2">
                            <Circle className="w-4 h-4" />
                            <span>Particles</span>
                          </div>
                        </SelectItem>
                        <SelectItem value="geometric">
                          <div className="flex items-center space-x-2">
                            <Square className="w-4 h-4" />
                            <span>Geometric Shapes</span>
                          </div>
                        </SelectItem>
                        <SelectItem value="gradient">
                          <div className="flex items-center space-x-2">
                            <Triangle className="w-4 h-4" />
                            <span>Color Gradients</span>
                          </div>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Color Scheme</Label>
                    <Select
                      value={config.visual_feedback.color_scheme}
                      onValueChange={(value) => handleVisualConfigChange('color_scheme', value)}
                      disabled={!isSessionActive || !config.visual_feedback.enabled}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="blue_green">Blue-Green</SelectItem>
                        <SelectItem value="warm">Warm Colors</SelectItem>
                        <SelectItem value="cool">Cool Colors</SelectItem>
                        <SelectItem value="rainbow">Rainbow</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label>Intensity ({(config.visual_feedback.intensity * 100).toFixed(0)}%)</Label>
                    <Slider
                      value={[config.visual_feedback.intensity * 100]}
                      onValueChange={(value) => handleVisualConfigChange('intensity', value[0] / 100)}
                      max={100}
                      step={1}
                      disabled={!isSessionActive || !config.visual_feedback.enabled}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Particle Count ({config.visual_feedback.particle_count})</Label>
                    <Slider
                      value={[config.visual_feedback.particle_count]}
                      onValueChange={(value) => handleVisualConfigChange('particle_count', value[0])}
                      min={10}
                      max={500}
                      step={10}
                      disabled={!isSessionActive || !config.visual_feedback.enabled}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Animation Speed ({config.visual_feedback.animation_speed.toFixed(1)}x)</Label>
                    <Slider
                      value={[config.visual_feedback.animation_speed * 10]}
                      onValueChange={(value) => handleVisualConfigChange('animation_speed', value[0] / 10)}
                      min={1}
                      max={30}
                      step={1}
                      disabled={!isSessionActive || !config.visual_feedback.enabled}
                    />
                  </div>
                </div>
              </div>
            </TabsContent>

            {/* Audio Feedback Tab */}
            <TabsContent value="audio" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Label>Enable Audio Feedback</Label>
                    <Switch
                      checked={config.audio_feedback.enabled}
                      onCheckedChange={(checked) => handleAudioConfigChange('enabled', checked)}
                      disabled={!isSessionActive}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Audio Type</Label>
                    <Select
                      value={config.audio_feedback.type}
                      onValueChange={(value) => handleAudioConfigChange('type', value)}
                      disabled={!isSessionActive || !config.audio_feedback.enabled}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="ambient">Ambient Sounds</SelectItem>
                        <SelectItem value="tones">Pure Tones</SelectItem>
                        <SelectItem value="nature">Nature Sounds</SelectItem>
                        <SelectItem value="musical">Musical Tones</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label>Volume ({(config.audio_feedback.volume * 100).toFixed(0)}%)</Label>
                    <Slider
                      value={[config.audio_feedback.volume * 100]}
                      onValueChange={(value) => handleAudioConfigChange('volume', value[0] / 100)}
                      max={100}
                      step={1}
                      disabled={!isSessionActive || !config.audio_feedback.enabled}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Frequency Range</Label>
                    <div className="flex items-center space-x-2">
                      <Slider
                        value={config.audio_feedback.frequency_range}
                        onValueChange={(value) => handleAudioConfigChange('frequency_range', value)}
                        min={50}
                        max={2000}
                        step={50}
                        disabled={!isSessionActive || !config.audio_feedback.enabled}
                      />
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {config.audio_feedback.frequency_range[0]}Hz - {config.audio_feedback.frequency_range[1]}Hz
                    </div>
                  </div>
                </div>
              </div>
            </TabsContent>

            {/* Haptic Feedback Tab */}
            <TabsContent value="haptic" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Label>Enable Haptic Feedback</Label>
                    <Switch
                      checked={config.haptic_feedback.enabled}
                      onCheckedChange={(checked) => handleHapticConfigChange('enabled', checked)}
                      disabled={!isSessionActive}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Haptic Pattern</Label>
                    <Select
                      value={config.haptic_feedback.pattern}
                      onValueChange={(value) => handleHapticConfigChange('pattern', value)}
                      disabled={!isSessionActive || !config.haptic_feedback.enabled}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="pulse">Pulse</SelectItem>
                        <SelectItem value="wave">Wave</SelectItem>
                        <SelectItem value="burst">Burst</SelectItem>
                        <SelectItem value="continuous">Continuous</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label>Intensity ({(config.haptic_feedback.intensity * 100).toFixed(0)}%)</Label>
                    <Slider
                      value={[config.haptic_feedback.intensity * 100]}
                      onValueChange={(value) => handleHapticConfigChange('intensity', value[0] / 100)}
                      max={100}
                      step={1}
                      disabled={!isSessionActive || !config.haptic_feedback.enabled}
                    />
                  </div>
                </div>
              </div>
            </TabsContent>

            {/* Thresholds Tab */}
            <TabsContent value="thresholds" className="space-y-4">
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label>Low Threshold ({(config.thresholds.low * 100).toFixed(0)}%)</Label>
                  <Slider
                    value={[config.thresholds.low * 100]}
                    onValueChange={(value) => handleThresholdChange('low', value)}
                    max={100}
                    step={1}
                    disabled={!isSessionActive}
                  />
                </div>

                <div className="space-y-2">
                  <Label>Medium Threshold ({(config.thresholds.medium * 100).toFixed(0)}%)</Label>
                  <Slider
                    value={[config.thresholds.medium * 100]}
                    onValueChange={(value) => handleThresholdChange('medium', value)}
                    max={100}
                    step={1}
                    disabled={!isSessionActive}
                  />
                </div>

                <div className="space-y-2">
                  <Label>High Threshold ({(config.thresholds.high * 100).toFixed(0)}%)</Label>
                  <Slider
                    value={[config.thresholds.high * 100]}
                    onValueChange={(value) => handleThresholdChange('high', value)}
                    max={100}
                    step={1}
                    disabled={!isSessionActive}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <Label>Adaptive Thresholds</Label>
                  <Switch
                    checked={config.adaptation.enabled}
                    onCheckedChange={(checked) => updateConfig({
                      ...config,
                      adaptation: { ...config.adaptation, enabled: checked }
                    })}
                    disabled={!isSessionActive}
                  />
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Current State Display */}
      {biofeedbackState && (
        <Card>
          <CardHeader>
            <CardTitle>Current Biofeedback State</CardTitle>
            <CardDescription>
              Real-time feedback parameters and status
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm font-medium">Visual Feedback</p>
                <p className="text-2xl font-bold">
                  {((biofeedbackState.visual_feedback?.intensity || 0) * 100).toFixed(0)}%
                </p>
                <p className="text-xs text-muted-foreground">
                  {biofeedbackState.visual_feedback?.particle_count || 0} particles
                </p>
              </div>
              <div>
                <p className="text-sm font-medium">Audio Feedback</p>
                <p className="text-2xl font-bold">
                  {biofeedbackState.audio_feedback?.enabled ? 'Active' : 'Inactive'}
                </p>
                <p className="text-xs text-muted-foreground">
                  Volume: {((biofeedbackState.audio_feedback?.volume || 0) * 100).toFixed(0)}%
                </p>
              </div>
              <div>
                <p className="text-sm font-medium">Last Update</p>
                <p className="text-2xl font-bold">
                  {lastUpdate ? lastUpdate.toLocaleTimeString() : 'N/A'}
                </p>
                <p className="text-xs text-muted-foreground">
                  Session: {sessionId ? 'Active' : 'Inactive'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default BiofeedbackControls;

