# Deployment Guide

## 🚀 Deploying AI Financial Intelligence Platform

This guide covers multiple deployment scenarios from local development to production.

---

## 1. Local Development Deployment

### Prerequisites
- Python 3.8 or higher
- Windows, macOS, or Linux

### Setup Steps

#### Step 1: Clone/Setup Project
```bash
cd c:\Users\aarsh\finaceproject
```

#### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 3: Start Backend (Terminal 1)
```bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

#### Step 4: Start Frontend (Terminal 2)
```bash
streamlit run frontend/app.py
```

#### Verification
- API: http://localhost:8000/docs
- Dashboard: http://localhost:8501

---

## 2. Docker Deployment

### Create Dockerfile for Backend
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Create Dockerfile for Frontend
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build Docker Images
```bash
# Backend
docker build -t fin-intelligence-backend -f Dockerfile.backend .

# Frontend
docker build -t fin-intelligence-frontend -f Dockerfile.frontend .
```

### Run Containers
```bash
# Backend
docker run -d -p 8000:8000 \
  --name backend \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  fin-intelligence-backend

# Frontend
docker run -d -p 8501:8501 \
  --name frontend \
  --link backend:backend \
  fin-intelligence-frontend
```

---

## 3. Docker Compose Deployment

### Create docker-compose.yml
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LOG_LEVEL=INFO
    volumes:
      - ./uploads:/app/uploads
      - ./data:/app/data
    networks:
      - app_network

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "8501:8501"
    depends_on:
      - backend
    environment:
      - API_BASE_URL=http://backend:8000/api/v1
    networks:
      - app_network

  database:
    image: postgres:14-alpine
    environment:
      - POSTGRES_DB=financial_db
      - POSTGRES_USER=dbuser
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - db_data:/var/lib/postgresql/data
    networks:
      - app_network

volumes:
  db_data:

networks:
  app_network:
```

### Start with Docker Compose
```bash
docker-compose up -d
```

### Verify Services
```bash
docker-compose ps
```

### Stop Services
```bash
docker-compose down
```

---

## 4. Cloud Deployment

### AWS Deployment

#### Using AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p "Python 3.9" financial-platform

# Create environment
eb create production-env

# Deploy
eb deploy

# Open in browser
eb open
```

#### Using AWS ECS + Fargate

1. Create ECR repositories:
```bash
aws ecr create-repository --repository-name fin-backend
aws ecr create-repository --repository-name fin-frontend
```

2. Push images:
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

docker tag fin-intelligence-backend:latest $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/fin-backend:latest
docker push $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/fin-backend:latest

docker tag fin-intelligence-frontend:latest $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/fin-frontend:latest
docker push $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/fin-frontend:latest
```

3. Create ECS task definitions and services via AWS Console

### Google Cloud Run Deployment

```bash
# Install Google Cloud CLI
# Authenticate
gcloud auth login

# Create project
gcloud projects create financial-intelligence

# Deploy Backend
gcloud run deploy fin-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Deploy Frontend
gcloud run deploy fin-frontend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Heroku Deployment

```bash
# Install Heroku CLI
# Login
heroku login

# Create app
heroku create financial-intelligence

# Deploy
git push heroku main

# Open app
heroku open

# View logs
heroku logs --tail
```

---

## 5. Kubernetes Deployment

### Create k8s Manifests

#### Backend Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: financial-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fin-backend
  template:
    metadata:
      labels:
        app: fin-backend
    spec:
      containers:
      - name: backend
        image: fin-intelligence-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: openai-api-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10

---
apiVersion: v1
kind: Service
metadata:
  name: fin-backend-service
spec:
  selector:
    app: fin-backend
  type: LoadBalancer
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
```

#### Frontend Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: financial-frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: fin-frontend
  template:
    metadata:
      labels:
        app: fin-frontend
    spec:
      containers:
      - name: frontend
        image: fin-intelligence-frontend:latest
        ports:
        - containerPort: 8501
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"

---
apiVersion: v1
kind: Service
metadata:
  name: fin-frontend-service
spec:
  selector:
    app: fin-frontend
  type: LoadBalancer
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8501
```

### Deploy to Kubernetes
```bash
# Create namespace
kubectl create namespace financial

# Create secrets
kubectl create secret generic app-secrets \
  --from-literal=openai-api-key=$OPENAI_API_KEY \
  -n financial

# Apply manifests
kubectl apply -f backend-deployment.yaml -n financial
kubectl apply -f frontend-deployment.yaml -n financial

# Check status
kubectl get pods -n financial
kubectl get services -n financial

# Port forward for local testing
kubectl port-forward service/fin-backend-service 8000:80 -n financial
kubectl port-forward service/fin-frontend-service 8501:80 -n financial
```

---

## 6. Production Best Practices

### Environment Configuration
```bash
# Create .env.production
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=WARNING
OPENAI_API_KEY=${OPENAI_API_KEY}
DATABASE_URL=postgresql://user:pass@db-host:5432/financial_db
VECTOR_STORE_PATH=/data/vector_store.json
```

### Security Measures
1. **API Keys**: Use environment variables, never commit to git
2. **HTTPS**: Use SSL/TLS certificates
3. **Authentication**: Add API key or JWT authentication
4. **Rate Limiting**: Implement rate limiting on API endpoints
5. **Logging**: Use centralized logging (ELK, Datadog)
6. **Monitoring**: Set up alerts and dashboards

### Scalability
1. **Load Balancer**: Use Nginx or cloud provider LB
2. **Auto-scaling**: Configure based on CPU/memory
3. **Database**: Use managed PostgreSQL
4. **Vector DB**: Use Pinecone or Weaviate
5. **Caching**: Add Redis for performance
6. **CDN**: Use CloudFront or Cloudflare

### Backup & Recovery
```bash
# Backup uploads
aws s3 sync uploads/ s3://fin-platform-backups/uploads/

# Backup database
pg_dump financial_db > backup_$(date +%Y%m%d).sql

# Upload to S3
aws s3 cp backup_*.sql s3://fin-platform-backups/
```

---

## 7. Monitoring & Logging

### Prometheus Metrics
Add to backend/main.py:
```python
from prometheus_client import Counter, Histogram, generate_latest

request_count = Counter('api_requests_total', 'Total API requests')
request_duration = Histogram('api_request_duration', 'API request duration')

@app.middleware("http")
async def add_metrics(request, call_next):
    request_count.inc()
    with request_duration.time():
        response = await call_next(request)
    return response
```

### CloudWatch Logs (AWS)
```python
import watchtower
import logging

logger = logging.getLogger(__name__)
logger.addHandler(watchtower.CloudWatchLogHandler())
```

### Datadog Integration
```python
from datadog import statsd

statsd.gauge('api.response_time', duration)
statsd.increment('api.requests.total')
```

---

## 8. CI/CD Pipeline

### GitHub Actions Example
```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Docker Images
        run: |
          docker build -t fin-backend .
          docker build -t fin-frontend -f Dockerfile.frontend .
      
      - name: Push to Registry
        run: |
          aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_URI
          docker tag fin-backend:latest $ECR_URI/fin-backend:latest
          docker push $ECR_URI/fin-backend:latest
      
      - name: Deploy to ECS
        run: |
          aws ecs update-service --cluster production --service fin-backend --force-new-deployment
```

---

## 9. Troubleshooting Deployment

### Container Won't Start
```bash
docker logs <container_id>
kubectl logs <pod_name> -n namespace
```

### API Connection Issues
```bash
# Test API from container
docker exec <backend_container> curl http://localhost:8000/api/v1/health

# Check network
docker network ls
docker network inspect <network_name>
```

### Memory/CPU Issues
```bash
docker stats <container_id>
kubectl top pods -n namespace
```

---

## 10. Post-Deployment Checklist

- [ ] API health check passing
- [ ] Frontend connecting to backend
- [ ] SSL/TLS certificates installed
- [ ] Database backups configured
- [ ] Monitoring and alerting active
- [ ] Logging working
- [ ] Auto-scaling configured
- [ ] Load balancer active
- [ ] DNS updated
- [ ] Documentation updated

---

## Support & Resources

- **Docker Docs**: https://docs.docker.com
- **Kubernetes Docs**: https://kubernetes.io/docs
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment
- **Streamlit Deployment**: https://docs.streamlit.io/library/get-started/installation
- **AWS Docs**: https://aws.amazon.com/documentation
- **GCP Docs**: https://cloud.google.com/docs

---

**Ready to deploy? Choose your platform and follow the steps above!** 🚀
