# Deployment Guide

Deploy your Claims Management Dashboard to production.

## 1. Heroku Deployment

### Prerequisites
- Heroku CLI installed
- Free Heroku account

### Backend Deployment

```bash
# Create Heroku app for backend
heroku create your-claims-backend

# Add Python buildpack
heroku buildpacks:add heroku/python -a your-claims-backend

# Set environment variables
heroku config:set SERVICENOW_INSTANCE=your_instance.service-now.com -a your-claims-backend
heroku config:set SERVICENOW_USERNAME=your_username -a your-claims-backend
heroku config:set SERVICENOW_PASSWORD=your_password -a your-claims-backend
heroku config:set FLASK_ENV=production -a your-claims-backend

# Create Procfile in backend/
echo "web: python app.py" > backend/Procfile

# Deploy
git push heroku main
```

### Frontend Deployment

```bash
# Create Heroku app for frontend
heroku create your-claims-frontend

# Add Node.js buildpack
heroku buildpacks:add heroku/nodejs -a your-claims-frontend

# Set environment variable for API URL
heroku config:set REACT_APP_API_URL=https://your-claims-backend.herokuapp.com -a your-claims-frontend

# Create Procfile in frontend/
echo "web: npm run build && npm start" > frontend/Procfile

# Deploy
git push heroku main
```

## 2. AWS Deployment

### Using Elastic Beanstalk

#### Backend

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.9 claims-backend

# Create environment
eb create claims-backend-env

# Deploy
eb deploy

# Set environment variables
eb setenv SERVICENOW_INSTANCE=your_instance.service-now.com
```

#### Frontend

```bash
# Build React app
cd frontend
npm run build

# Upload to S3
aws s3 sync build/ s3://your-bucket-name/

# CloudFront for CDN
# Configure CloudFront distribution for your S3 bucket
```

## 3. Azure Deployment

### App Service

```bash
# Create resource group
az group create --name claims-rg --location eastus

# Backend
az appservice plan create --name claims-plan --resource-group claims-rg --sku B1 --is-linux
az webapp create --resource-group claims-rg --plan claims-plan --name claims-backend-api --runtime "python|3.9"

# Configure
az webapp config appsettings set --resource-group claims-rg --name claims-backend-api \
  --settings SERVICENOW_INSTANCE=your_instance.service-now.com \
  SERVICENOW_USERNAME=your_username \
  SERVICENOW_PASSWORD=your_password

# Deploy
az webapp up --name claims-backend-api --resource-group claims-rg
```

## 4. Google Cloud Deployment

### Cloud Run

```bash
# Build and deploy backend
gcloud run deploy claims-backend \
  --source ./backend \
  --platform managed \
  --region us-central1 \
  --set-env-vars SERVICENOW_INSTANCE=your_instance.service-now.com

# Build and deploy frontend
gcloud run deploy claims-frontend \
  --source ./frontend \
  --platform managed \
  --region us-central1
```

## 5. Docker Compose (VPS/Self-hosted)

### Setup on DigitalOcean Droplet

```bash
# SSH into droplet
ssh root@your_droplet_ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Clone repository
git clone your-repo-url
cd dashboard

# Create .env file
nano .env
# Add your credentials

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

## 6. Kubernetes Deployment

### Prerequisites
- Kubernetes cluster (GKE, EKS, AKS, or local)
- kubectl installed
- Docker images pushed to registry

### Deploy

```bash
# Create namespace
kubectl create namespace claims

# Create secrets
kubectl create secret generic servicenow-credentials \
  --from-literal=instance=your_instance.service-now.com \
  --from-literal=username=your_username \
  --from-literal=password=your_password \
  -n claims

# Apply deployments
kubectl apply -f k8s/ -n claims

# Check status
kubectl get pods -n claims
kubectl logs -f deployment/claims-backend -n claims

# Expose services
kubectl expose deployment claims-backend --type=LoadBalancer -n claims
kubectl expose deployment claims-frontend --type=LoadBalancer -n claims
```

### k8s/backend-deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: claims-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: claims-backend
  template:
    metadata:
      labels:
        app: claims-backend
    spec:
      containers:
      - name: backend
        image: your-registry/claims-backend:latest
        ports:
        - containerPort: 5000
        env:
        - name: SERVICENOW_INSTANCE
          valueFrom:
            secretKeyRef:
              name: servicenow-credentials
              key: instance
        - name: SERVICENOW_USERNAME
          valueFrom:
            secretKeyRef:
              name: servicenow-credentials
              key: username
        - name: SERVICENOW_PASSWORD
          valueFrom:
            secretKeyRef:
              name: servicenow-credentials
              key: password
        - name: FLASK_ENV
          value: "production"
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
          requests:
            memory: "256Mi"
            cpu: "250m"
```

## 7. Security Checklist

- [ ] Use HTTPS/SSL certificates (Let's Encrypt)
- [ ] Configure firewall rules
- [ ] Use environment variables for secrets
- [ ] Enable database encryption
- [ ] Set up monitoring and alerts
- [ ] Configure backup strategy
- [ ] Enable auto-scaling
- [ ] Set up CI/CD pipeline
- [ ] Regular security audits
- [ ] Enable logging and monitoring

## 8. Performance Optimization

- Enable caching (Redis)
- Use CDN for static files
- Implement database indexing
- Set up load balancing
- Use compression (gzip)
- Optimize images
- Implement rate limiting
- Monitor performance metrics

## 9. Monitoring Setup

### Using CloudWatch (AWS)

```python
# Add to app.py
import logging
import watchtower

logging.basicConfig(
    handlers=[
        watchtower.CloudWatchLogHandler()
    ]
)
```

### Using DataDog

```bash
# Install agent
DD_API_KEY=your_key DD_AGENT_MAJOR_VERSION=7 \
DD_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true \
pip install datadog
```

## 10. Rollback Procedure

### Heroku
```bash
heroku releases -a your-app
heroku rollback v12 -a your-app
```

### Docker
```bash
docker-compose down
git revert <commit-hash>
docker-compose up -d
```

### Kubernetes
```bash
kubectl rollout history deployment/claims-backend -n claims
kubectl rollout undo deployment/claims-backend -n claims
```

---

For more details, see the main README.md
