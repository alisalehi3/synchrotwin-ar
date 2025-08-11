import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Brain, Heart, Activity, Zap, Eye, Users, Play, Pause, RotateCcw } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import './App.css'

// Import generated images
import arOrbsImage from './assets/synchrotwin_ar_orbs.png'
import sessionUIImage from './assets/synchrotwin_session_ui.png'
import dataVizImage from './assets/synchrotwin_data_viz.png'
import digitalTwinImage from './assets/synchrotwin_digital_twin.png'

function App() {
  const [currentPhase, setCurrentPhase] = useState('baseline')
  const [sessionTime, setSessionTime] = useState(0)
  const [isRunning, setIsRunning] = useState(false)
  const [resonanceData, setResonanceData] = useState([])
  const [currentResonance, setCurrentResonance] = useState(0.32)
  const [sensorStatus, setSensorStatus] = useState({
    eeg: true,
    fnirs: true,
    hrv: true,
    imu: false
  })

  const phases = [
    { id: 'baseline', name: 'Baseline', duration: 60, color: 'bg-blue-500' },
    { id: 'sync', name: 'Silent Sync', duration: 90, color: 'bg-green-500' },
    { id: 'taskA', name: 'Task A', duration: 120, color: 'bg-yellow-500' },
    { id: 'taskB', name: 'Task B', duration: 240, color: 'bg-purple-500' },
    { id: 'debrief', name: 'Debrief', duration: 240, color: 'bg-orange-500' }
  ]

  // Simulate real-time data
  useEffect(() => {
    let interval
    if (isRunning) {
      interval = setInterval(() => {
        setSessionTime(prev => prev + 1)
        
        // Generate realistic resonance data
        const newResonance = Math.max(0, Math.min(1, 
          currentResonance + (Math.random() - 0.5) * 0.1
        ))
        setCurrentResonance(newResonance)
        
        setResonanceData(prev => {
          const newData = [...prev, {
            time: prev.length,
            resonance: newResonance,
            plv: Math.random() * 0.8 + 0.1,
            envelope: Math.random() * 0.7 + 0.2,
            crqa: Math.random() * 0.6 + 0.3
          }]
          return newData.slice(-50) // Keep last 50 points
        })
      }, 1000)
    }
    return () => clearInterval(interval)
  }, [isRunning, currentResonance])

  const getCurrentPhase = () => {
    return phases.find(p => p.id === currentPhase) || phases[0]
  }

  const getPhaseProgress = () => {
    const phase = getCurrentPhase()
    return Math.min(100, (sessionTime / phase.duration) * 100)
  }

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white">
      {/* Header */}
      <header className="border-b border-white/10 bg-black/20 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                <Brain className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  SynchroTwin-AR
                </h1>
                <p className="text-sm text-gray-400">Bridging Minds, Visualizing Synchrony</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="outline" className="text-green-400 border-green-400">
                <Activity className="w-3 h-3 mr-1" />
                Live Session
              </Badge>
              <div className="text-right">
                <div className="text-lg font-mono">{formatTime(sessionTime)}</div>
                <div className="text-xs text-gray-400">Session Time</div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        <Tabs defaultValue="ar-view" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5 bg-black/20 backdrop-blur-sm">
            <TabsTrigger value="ar-view" className="data-[state=active]:bg-blue-500">AR View</TabsTrigger>
            <TabsTrigger value="session" className="data-[state=active]:bg-green-500">Session</TabsTrigger>
            <TabsTrigger value="data" className="data-[state=active]:bg-purple-500">Data</TabsTrigger>
            <TabsTrigger value="twin" className="data-[state=active]:bg-orange-500">Digital Twin</TabsTrigger>
            <TabsTrigger value="debrief" className="data-[state=active]:bg-red-500">Debrief</TabsTrigger>
          </TabsList>

          {/* AR View Tab */}
          <TabsContent value="ar-view" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-black/40 backdrop-blur-sm border-white/10">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Eye className="w-5 h-5 text-blue-400" />
                    <span>AR Visualization</span>
                  </CardTitle>
                  <CardDescription>Real-time dyadic synchrony visualization</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="relative aspect-video bg-gradient-to-br from-blue-900/50 to-purple-900/50 rounded-lg overflow-hidden">
                    <img 
                      src={arOrbsImage} 
                      alt="AR Orbs Visualization" 
                      className="w-full h-full object-cover opacity-80"
                    />
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-center">
                        <div className="text-4xl font-bold mb-2">{(currentResonance * 100).toFixed(0)}%</div>
                        <div className="text-sm text-gray-300">Current Resonance</div>
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 grid grid-cols-2 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-400">Participant A</div>
                      <div className="w-4 h-4 bg-blue-500 rounded-full mx-auto mt-2 animate-pulse"></div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-yellow-400">Participant B</div>
                      <div className="w-4 h-4 bg-yellow-500 rounded-full mx-auto mt-2 animate-pulse"></div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-black/40 backdrop-blur-sm border-white/10">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Zap className="w-5 h-5 text-green-400" />
                    <span>Real-time Metrics</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-2">
                      <span>Resonance (R)</span>
                      <span className="font-mono">{currentResonance.toFixed(3)}</span>
                    </div>
                    <Progress value={currentResonance * 100} className="h-2" />
                  </div>
                  <div>
                    <div className="flex justify-between mb-2">
                      <span>Phase-Locking Value</span>
                      <span className="font-mono">0.742</span>
                    </div>
                    <Progress value={74.2} className="h-2" />
                  </div>
                  <div>
                    <div className="flex justify-between mb-2">
                      <span>Envelope Correlation</span>
                      <span className="font-mono">0.658</span>
                    </div>
                    <Progress value={65.8} className="h-2" />
                  </div>
                  <div>
                    <div className="flex justify-between mb-2">
                      <span>CRQA Determinism</span>
                      <span className="font-mono">0.523</span>
                    </div>
                    <Progress value={52.3} className="h-2" />
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Session Tab */}
          <TabsContent value="session" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-black/40 backdrop-blur-sm border-white/10">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Users className="w-5 h-5 text-green-400" />
                    <span>Session Control</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    <div className="text-center">
                      <img 
                        src={sessionUIImage} 
                        alt="Session UI" 
                        className="w-full max-w-md mx-auto rounded-lg"
                      />
                    </div>
                    
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between mb-2">
                          <span>Current Phase: {getCurrentPhase().name}</span>
                          <span>{Math.floor(getPhaseProgress())}%</span>
                        </div>
                        <Progress value={getPhaseProgress()} className="h-3" />
                      </div>
                      
                      <div className="flex justify-center space-x-4">
                        <Button 
                          onClick={() => setIsRunning(!isRunning)}
                          className={isRunning ? "bg-red-500 hover:bg-red-600" : "bg-green-500 hover:bg-green-600"}
                        >
                          {isRunning ? <Pause className="w-4 h-4 mr-2" /> : <Play className="w-4 h-4 mr-2" />}
                          {isRunning ? 'Pause' : 'Start'}
                        </Button>
                        <Button 
                          variant="outline" 
                          onClick={() => {
                            setSessionTime(0)
                            setIsRunning(false)
                            setResonanceData([])
                          }}
                        >
                          <RotateCcw className="w-4 h-4 mr-2" />
                          Reset
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-black/40 backdrop-blur-sm border-white/10">
                <CardHeader>
                  <CardTitle>Sensor Status</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4">
                    {Object.entries(sensorStatus).map(([sensor, status]) => (
                      <div key={sensor} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                        <div className="flex items-center space-x-2">
                          {sensor === 'eeg' && <Brain className="w-5 h-5" />}
                          {sensor === 'fnirs' && <Zap className="w-5 h-5" />}
                          {sensor === 'hrv' && <Heart className="w-5 h-5" />}
                          {sensor === 'imu' && <Activity className="w-5 h-5" />}
                          <span className="uppercase font-medium">{sensor}</span>
                        </div>
                        <Badge variant={status ? "default" : "destructive"}>
                          {status ? "Connected" : "Disconnected"}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Data Tab */}
          <TabsContent value="data" className="space-y-6">
            <Card className="bg-black/40 backdrop-blur-sm border-white/10">
              <CardHeader>
                <CardTitle>Real-time Data Visualization</CardTitle>
                <CardDescription>Live biometric streams and synchrony metrics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="text-center">
                    <img 
                      src={dataVizImage} 
                      alt="Data Visualization" 
                      className="w-full max-w-4xl mx-auto rounded-lg"
                    />
                  </div>
                  
                  {resonanceData.length > 0 && (
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={resonanceData}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                          <XAxis dataKey="time" stroke="#9CA3AF" />
                          <YAxis stroke="#9CA3AF" />
                          <Tooltip 
                            contentStyle={{ 
                              backgroundColor: '#1F2937', 
                              border: '1px solid #374151',
                              borderRadius: '8px'
                            }} 
                          />
                          <Area 
                            type="monotone" 
                            dataKey="resonance" 
                            stroke="#3B82F6" 
                            fill="#3B82F6" 
                            fillOpacity={0.3}
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Digital Twin Tab */}
          <TabsContent value="twin" className="space-y-6">
            <Card className="bg-black/40 backdrop-blur-sm border-white/10">
              <CardHeader>
                <CardTitle>Digital Twin Interface</CardTitle>
                <CardDescription>Policy divergence analysis and bias mitigation</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="text-center">
                    <img 
                      src={digitalTwinImage} 
                      alt="Digital Twin Interface" 
                      className="w-full max-w-4xl mx-auto rounded-lg"
                    />
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold">Policy Analysis</h3>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span>Default Narrative (DN)</span>
                          <span className="text-blue-400">Stable</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Observed Narrative (ON)</span>
                          <span className="text-yellow-400">Variable</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Bias Divergence</span>
                          <span className="text-red-400">0.23</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold">MRAP System</h3>
                      <div className="space-y-2">
                        <Badge variant="outline">Prior Annealing: τ=1.5</Badge>
                        <Badge variant="outline">Anti-priming: 30%</Badge>
                        <Badge variant="outline">Retrieval: Vector+Graph</Badge>
                        <Badge variant="outline">Triad Score: 0.78</Badge>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Debrief Tab */}
          <TabsContent value="debrief" className="space-y-6">
            <Card className="bg-black/40 backdrop-blur-sm border-white/10">
              <CardHeader>
                <CardTitle>Session Debrief</CardTitle>
                <CardDescription>Comprehensive analysis and insights</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Performance Metrics</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span>Average Resonance</span>
                        <span className="font-mono">0.67</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Peak Synchrony</span>
                        <span className="font-mono">0.89</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Task A Accuracy</span>
                        <span className="font-mono">78%</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Bias Reduction</span>
                        <span className="font-mono">15%</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Key Insights</h3>
                    <ul className="space-y-2 text-sm">
                      <li>• Strong initial synchrony during baseline</li>
                      <li>• Improved coordination in Task B</li>
                      <li>• Effective bias mitigation strategies</li>
                      <li>• Consistent sensor data quality</li>
                    </ul>
                  </div>
                  
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Recommendations</h3>
                    <ul className="space-y-2 text-sm">
                      <li>• Focus on breathing synchronization</li>
                      <li>• Practice silent communication</li>
                      <li>• Implement counter-bias techniques</li>
                      <li>• Schedule follow-up session</li>
                    </ul>
                  </div>
                </div>
                
                <div className="mt-6 pt-6 border-t border-white/10">
                  <Button className="w-full bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600">
                    Export Session Report
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default App

