# SynchroTwin-AR: Real-time Neural Synchrony & AR Biofeedback System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18.0+-blue.svg)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)](https://flask.palletsprojects.com/)

## 🧠 Overview

SynchroTwin-AR is a cutting-edge system for real-time neural synchrony monitoring and augmented reality biofeedback. It combines advanced neuroscience algorithms with modern web technologies to create a comprehensive platform for studying and enhancing inter-brain synchrony.

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
- Node.js 18+
- npm or yarn package manager

### 1. Clone and Setup
```bash
git clone https://github.com/alisalehi3/synchrotwin-ar.git
cd synchrotwin-ar
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run demo backend (all services)
python demo_backend.py
```

The backend will automatically:
- Start 5 microservices on ports 5000-5004
- Handle port conflicts automatically
- Generate real-time demo data
- Provide WebSocket connections

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend/synchrotwin-ar-frontend

# Install dependencies
npm install

# Start development server
npm run dev
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
├── requirements.txt              # Python dependencies
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
| Synchrony Analysis | 5001 | Real-time PLV and CRQA calculations |
| AR Biofeedback | 5002 | Biofeedback session management |
| Data Ingestion | 5003 | Data stream processing and management |
| Notification | 5004 | WebSocket notifications and real-time updates |

### API Endpoints

Each service provides a `/api/health` endpoint for monitoring:

```bash
# Check service health
curl http://localhost:5000/api/health
curl http://localhost:5001/api/health
curl http://localhost:5002/api/health
curl http://localhost:5003/api/health
curl http://localhost:5004/api/health
```

## 🎯 Features

### Real-time Dashboard
- **Service Status Monitoring**: Live health checks for all backend services
- **PLV Data Visualization**: Real-time chart showing Phase-Locking Value data
- **WebSocket Connection**: Live data streaming from backend to frontend
- **Responsive Design**: Works on desktop and mobile devices

### Demo Data Generation
- **Automatic PLV Generation**: Simulated neural synchrony data
- **WebSocket Broadcasting**: Real-time data emission every 2 seconds
- **Service Health Simulation**: Realistic service status monitoring

## 🔧 Troubleshooting

### Port Conflicts
If you see "Address already in use" errors:
- The backend automatically finds available ports
- Check the console output for actual port numbers
- Update frontend configuration if needed

### Frontend Issues
If npm install fails:
```bash
# Clear npm cache
npm cache clean --force

# Try with yarn instead
yarn install
```

### Backend Issues
If services don't start:
```bash
# Check Python version
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📊 Demo Features

### Live Data Visualization
- Real-time PLV (Phase-Locking Value) charts
- Service health monitoring
- WebSocket connection status
- Historical data display

### Service Monitoring
- Individual service health checks
- Automatic error detection
- Service status indicators
- Port conflict resolution

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Ali Salehi**
- GitHub: [@alisalehi3](https://github.com/alisalehi3)

## 🔬 Research

For detailed research information, see [research_report.md](research_report.md).

## 🚀 Deployment

For production deployment instructions, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).

## 🙏 Acknowledgments

- Built with [shadcn/ui](https://ui.shadcn.com/) components
- Powered by [Vite](https://vitejs.dev/) for fast development
- Styled with [Tailwind CSS](https://tailwindcss.com/)
- Backend powered by [Flask](https://flask.palletsprojects.com/)

---

**Note**: This is a demonstration system. For production use, implement proper security measures, data validation, and error handling.
