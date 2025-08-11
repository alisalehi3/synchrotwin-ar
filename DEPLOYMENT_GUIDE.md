# SynchroTwin-AR Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- npm/pnpm package manager

### 1. Backend Services Setup

#### Option A: Individual Services (Production)
```bash
# Navigate to project directory
cd synchrotwin-ar

# Setup Digital Twin Service
cd backend/digital_twin_service/digital_twin_service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/main.py &

# Setup Synchrony Analysis Service
cd ../../../synchrony_analysis_service/synchrony_analysis_service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py &

# Setup AR Biofeedback Service
cd ../../../ar_biofeedback_service/ar_biofeedback_service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py &

# Setup Data Ingestion Service
cd ../../../data_ingestion_service/data_ingestion_service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py &

# Setup Notification Service
cd ../../../notification_service/notification_service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py &
```

#### Option B: Demo Backend (Development/Testing)
```bash
# Navigate to project directory
cd synchrotwin-ar

# Install dependencies
pip install flask flask-cors flask-socketio

# Run demo backend (all services in one process)
python demo_backend.py
```

### 2. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend/synchrotwin-ar-frontend

# Install dependencies
pnpm install
# or: npm install

# Start development server
pnpm run dev --host
# or: npm run dev -- --host

# Access dashboard at: http://localhost:5173
```

## 🏗️ Production Deployment

### Docker Deployment (Recommended)

#### 1. Create Dockerfiles for each service

**Backend Service Dockerfile Example:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
EXPOSE 5000

CMD ["python", "src/main.py"]
```

**Frontend Dockerfile:**
```dockerfile
FROM node:20-alpine

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
EXPOSE 80
```

#### 2. Docker Compose Configuration
```yaml
# docker-compose.yml
version: '3.8'

services:
  digital-twin:
    build: ./backend/digital_twin_service
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    
  synchrony-analysis:
    build: ./backend/synchrony_analysis_service
    ports:
      - "5001:5001"
    environment:
      - FLASK_ENV=production
    
  ar-biofeedback:
    build: ./backend/ar_biofeedback_service
    ports:
      - "5002:5002"
    environment:
      - FLASK_ENV=production
    
  data-ingestion:
    build: ./backend/data_ingestion_service
    ports:
      - "5003:5003"
    environment:
      - FLASK_ENV=production
    
  notification:
    build: ./backend/notification_service
    ports:
      - "5004:5004"
    environment:
      - FLASK_ENV=production
    
  frontend:
    build: ./frontend/synchrotwin-ar-frontend
    ports:
      - "80:80"
    depends_on:
      - digital-twin
      - synchrony-analysis
      - ar-biofeedback
      - data-ingestion
      - notification

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
```

### Kubernetes Deployment

#### 1. Service Manifests
```yaml
# k8s/digital-twin-service.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: digital-twin-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: digital-twin-service
  template:
    metadata:
      labels:
        app: digital-twin-service
    spec:
      containers:
      - name: digital-twin
        image: synchrotwin/digital-twin:latest
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: "production"
---
apiVersion: v1
kind: Service
metadata:
  name: digital-twin-service
spec:
  selector:
    app: digital-twin-service
  ports:
  - port: 5000
    targetPort: 5000
  type: ClusterIP
```

#### 2. Ingress Configuration
```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: synchrotwin-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: synchrotwin.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
      - path: /api/twins
        pathType: Prefix
        backend:
          service:
            name: digital-twin-service
            port:
              number: 5000
```

## 🔧 Configuration

### Environment Variables

#### Backend Services
```bash
# Common environment variables
FLASK_ENV=production
FLASK_DEBUG=false
DATABASE_URL=postgresql://user:pass@localhost/synchrotwin
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO

# Service-specific variables
DIGITAL_TWIN_PORT=5000
SYNCHRONY_ANALYSIS_PORT=5001
AR_BIOFEEDBACK_PORT=5002
DATA_INGESTION_PORT=5003
NOTIFICATION_PORT=5004
```

#### Frontend Configuration
```javascript
// src/config/environment.js
export const config = {
  API_BASE_URL: process.env.VITE_API_BASE_URL || 'http://localhost',
  WEBSOCKET_URL: process.env.VITE_WEBSOCKET_URL || 'ws://localhost:5004',
  SERVICES: {
    DIGITAL_TWIN: process.env.VITE_DIGITAL_TWIN_URL || 'http://localhost:5000',
    SYNCHRONY_ANALYSIS: process.env.VITE_SYNCHRONY_URL || 'http://localhost:5001',
    AR_BIOFEEDBACK: process.env.VITE_BIOFEEDBACK_URL || 'http://localhost:5002',
    DATA_INGESTION: process.env.VITE_DATA_INGESTION_URL || 'http://localhost:5003',
    NOTIFICATION: process.env.VITE_NOTIFICATION_URL || 'http://localhost:5004'
  }
};
```

### Database Setup

#### PostgreSQL (Production)
```sql
-- Create database
CREATE DATABASE synchrotwin;
CREATE USER synchrotwin_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE synchrotwin TO synchrotwin_user;

-- Create tables (run from each service)
python -c "from src.models import db; db.create_all()"
```

#### Redis (Caching/Sessions)
```bash
# Install Redis
sudo apt-get install redis-server

# Configure Redis
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

## 🔒 Security Configuration

### SSL/TLS Setup
```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name synchrotwin.example.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/ {
        proxy_pass http://backend-services;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /socket.io/ {
        proxy_pass http://notification:5004;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Authentication Setup
```python
# Add to each service
from flask_jwt_extended import JWTManager

app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)

@app.before_request
def require_auth():
    if request.endpoint not in ['health', 'login']:
        verify_jwt_in_request()
```

## 📊 Monitoring and Logging

### Health Checks
```python
# Add to each service
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })
```

### Logging Configuration
```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/synchrotwin.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
```

### Prometheus Metrics
```python
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='1.0.0')
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Service Connection Errors
```bash
# Check service status
curl http://localhost:5000/api/health

# Check logs
tail -f logs/synchrotwin.log

# Restart service
sudo systemctl restart synchrotwin-digital-twin
```

#### 2. Frontend Build Issues
```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install

# Check for dependency conflicts
npm audit fix
```

#### 3. Database Connection Issues
```bash
# Test database connection
psql -h localhost -U synchrotwin_user -d synchrotwin

# Check database logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### Performance Optimization

#### 1. Backend Optimization
```python
# Use connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30
)
```

#### 2. Frontend Optimization
```javascript
// Code splitting
const Dashboard = lazy(() => import('./components/Dashboard'));

// Memoization
const MemoizedChart = memo(SynchronyChart);

// Virtual scrolling for large datasets
import { FixedSizeList as List } from 'react-window';
```

## 📈 Scaling Considerations

### Horizontal Scaling
- **Load Balancers**: Nginx, HAProxy, or cloud load balancers
- **Service Mesh**: Istio for advanced traffic management
- **Auto-scaling**: Kubernetes HPA based on CPU/memory metrics

### Database Scaling
- **Read Replicas**: PostgreSQL streaming replication
- **Sharding**: Partition data by participant or session
- **Caching**: Redis for frequently accessed data

### Monitoring Stack
- **Metrics**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Tracing**: Jaeger for distributed tracing
- **Alerting**: AlertManager for critical issues

---

## 🎯 Deployment Checklist

### Pre-deployment
- [ ] Environment variables configured
- [ ] Database migrations completed
- [ ] SSL certificates installed
- [ ] Security configurations applied
- [ ] Health checks implemented

### Post-deployment
- [ ] Service health verified
- [ ] Frontend accessibility confirmed
- [ ] WebSocket connections tested
- [ ] Performance metrics baseline established
- [ ] Monitoring alerts configured

### Production Readiness
- [ ] Load testing completed
- [ ] Backup procedures implemented
- [ ] Disaster recovery plan documented
- [ ] Security audit performed
- [ ] Documentation updated

