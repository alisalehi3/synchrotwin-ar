# SynchroTwin-AR: Real-time Neural Synchrony & AR Biofeedback System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18.0+-blue.svg)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)](https://flask.palletsprojects.com/)

## 🧠 Overview

SynchroTwin-AR is a cutting-edge system for real-time neural synchrony monitoring and augmented reality biofeedback. It combines advanced neuroscience algorithms with modern web technologies to create a comprehensive platform for studying and enhancing inter-brain synchrony.

![SynchroTwin-AR Dashboard](screenshots/dashboard-overview.png)

## ✨ Key Features

### 🔬 Advanced Neural Analysis
- **Phase-Locking Value (PLV)**: Real-time phase synchrony measurement
- **Cross-Recurrence Quantification Analysis (CRQA)**: Coupling and coordination analysis
- **fNIRS Coherence**: Inter-brain synchrony via functional near-infrared spectroscopy

### 🎮 AR Biofeedback Engine
- **Visual Feedback**: Particle systems, geometric shapes, color gradients
- **Audio Feedback**: Ambient sounds, pure tones, nature sounds
- **Haptic Feedback**: Configurable intensity and patterns
- **Adaptive Thresholds**: Dynamic adjustment based on performance

### 📊 Professional Dashboard
- **Real-time Monitoring**: Live synchrony metrics and system status
- **Interactive Controls**: Session management and biofeedback configuration
- **Data Visualization**: Advanced charts and trend analysis
- **Service Health**: Comprehensive backend monitoring

### 🏗️ Microservices Architecture
- **Scalable Design**: Independent, containerizable services
- **Real-time Communication**: WebSocket-based live updates
- **RESTful APIs**: Comprehensive service endpoints
- **Health Monitoring**: Automatic service health checks

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- npm/pnpm package manager

### 1. Clone and Setup
```bash
git clone <repository-url>
cd synchrotwin-ar
```

### 2. Backend Setup (Demo Mode)
```bash
# Install dependencies
pip install flask flask-cors flask-socketio numpy scipy pywavelets

# Run demo backend (all services)
python demo_backend.py
```

### 3. Frontend Setup
```bash
cd frontend/synchrotwin-ar-frontend
pnpm install
pnpm run dev --host
```

### 4. Access Dashboard
Open your browser to: `http://localhost:5173`

## 📁 Project Structure

```
synchrotwin-ar/
├── algorithms/                    # Core synchrony analysis algorithms
│   ├── plv_calculator.py         # Phase-Locking Value implementation
│   ├── crqa_analyzer.py          # Cross-Recurrence Quantification Analysis
│   └── fnirs_coherence.py        # fNIRS coherence analysis
├── backend/                       # Flask microservices
│   ├── digital_twin_service/      # Digital twin management
│   ├── synchrony_analysis_service/ # Real-time synchrony analysis
│   ├── ar_biofeedback_service/    # AR biofeedback engine
│   ├── data_ingestion_service/    # Data stream management
│   └── notification_service/      # WebSocket notifications
├── frontend/                      # React dashboard
│   └── synchrotwin-ar-frontend/   # Complete dashboard interface
├── demo_backend.py               # Simplified demo backend
├── research_report.md            # Comprehensive research documentation
├── architecture_design.md        # System architecture specification
├── DEPLOYMENT_GUIDE.md          # Production deployment guide
└── PROJECT_SUMMARY.md           # Detailed project overview
```

## 🔧 Services Overview

### Backend Services (Ports 5000-5004)

| Service | Port | Description |
|---------|------|-------------|
| Digital Twin | 5000 | Manages digital twin states and configurations |
| Synchrony Analysis | 5001 | Real-time PLV, CRQA, and fNIRS analysis |
| AR Biofeedback | 5002 | Visual, audio, and haptic feedback generation |
| Data Ingestion | 5003 | Real-time biosignal data stream management |
| Notification | 5004 | WebSocket notifications and real-time updates |

### Frontend Dashboard (Port 5173)
- **Overview Tab**: System status and session management
- **Synchrony Tab**: Real-time neural synchrony visualization
- **Biofeedback Tab**: AR feedback configuration and control
- **Data Streams Tab**: Biosignal stream monitoring
- **System Tab**: Service health and system information

## 🧪 Core Algorithms

### Phase-Locking Value (PLV)
Measures the consistency of phase differences between two signals across time windows.

```python
from algorithms.plv_calculator import PLVCalculator

calculator = PLVCalculator()
plv = calculator.calculate_plv(signal1, signal2, sampling_rate=1000)
```

### Cross-Recurrence Quantification Analysis (CRQA)
Analyzes the recurrence patterns in phase space to quantify coupling between systems.

```python
from algorithms.crqa_analyzer import CRQAAnalyzer

analyzer = CRQAAnalyzer()
results = analyzer.analyze_crqa(signal1, signal2, embedding_dim=3, delay=1)
```

### fNIRS Coherence
Computes spectral, wavelet, and phase coherence for fNIRS signals.

```python
from algorithms.fnirs_coherence import FNIRSCoherence

coherence = FNIRSCoherence()
result = coherence.calculate_coherence(signal1, signal2, method='spectral')
```

## 📊 Dashboard Features

### Real-time Visualization
- **Time Series Charts**: Live synchrony metrics over time
- **Radial Progress**: Current synchrony levels
- **Trend Analysis**: Automatic trend detection
- **Health Indicators**: Service status visualization

### Interactive Controls
- **Session Management**: Start, pause, resume, stop sessions
- **Biofeedback Configuration**: Real-time parameter adjustment
- **Data Stream Control**: Stream creation and management
- **Notification Management**: Real-time system alerts

## 🔬 Research Applications

### Neuroscience Research
- **Hyperscanning Studies**: Multi-participant brain synchrony
- **Cognitive Load Assessment**: Real-time mental workload monitoring
- **Social Neuroscience**: Interpersonal neural coupling analysis

### Clinical Applications
- **Neurofeedback Therapy**: Real-time brain training
- **Rehabilitation**: Motor and cognitive rehabilitation
- **Mental Health**: Stress and anxiety management

### Educational Technology
- **Collaborative Learning**: Team synchrony enhancement
- **Attention Training**: Focus and concentration improvement
- **Performance Optimization**: Peak performance states

## 🏗️ Architecture

### Microservices Design
- **Independent Scaling**: Each service scales independently
- **Fault Tolerance**: Service isolation prevents cascading failures
- **Technology Diversity**: Best tool for each service
- **Development Velocity**: Independent team development

### Real-time Communication
- **WebSocket Integration**: Live data streaming
- **Event-driven Architecture**: Reactive system design
- **Pub/Sub Messaging**: Decoupled service communication
- **Real-time Notifications**: Instant system updates

## 🚀 Deployment

### Development
```bash
# Demo backend (all services in one process)
python demo_backend.py

# Frontend development server
cd frontend/synchrotwin-ar-frontend
pnpm run dev --host
```

### Production
```bash
# Docker Compose
docker-compose up -d

# Kubernetes
kubectl apply -f k8s/
```

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed deployment instructions.

## 📚 Documentation

- **[Research Report](research_report.md)**: Comprehensive algorithm documentation
- **[Architecture Design](architecture_design.md)**: System architecture specification
- **[Project Summary](PROJECT_SUMMARY.md)**: Detailed project overview
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)**: Production deployment instructions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Neuroscience Community**: For foundational research in neural synchrony
- **Open Source Libraries**: NumPy, SciPy, React, Flask, and many others
- **Research Institutions**: Supporting hyperscanning and neurofeedback research

## 📞 Contact

For questions, support, or collaboration opportunities:

- **Project Repository**: [GitHub Repository URL]
- **Documentation**: [Documentation URL]
- **Issues**: [GitHub Issues URL]

---

**SynchroTwin-AR** - Advancing the future of neural synchrony research and AR biofeedback therapy.

![Neural Synchrony](https://img.shields.io/badge/Neural-Synchrony-blue)
![AR Biofeedback](https://img.shields.io/badge/AR-Biofeedback-green)
![Real--time](https://img.shields.io/badge/Real--time-Processing-red)
![Research](https://img.shields.io/badge/Research-Grade-purple)

