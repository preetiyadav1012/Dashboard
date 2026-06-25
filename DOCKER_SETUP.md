# Docker Setup (Optional)

If you have Docker installed, you can run the entire application in containers.

## Building and Running with Docker

### 1. Create Dockerfile for Backend

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_ENV=production
ENV PORT=5000

EXPOSE 5000

CMD ["python", "app.py"]
```

### 2. Create Dockerfile for Frontend

Create `frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:18-alpine

WORKDIR /app
RUN npm install -g serve

COPY --from=build /app/build ./build

EXPOSE 3000

CMD ["serve", "-s", "build", "-l", "3000"]
```

### 3. Create docker-compose.yml

Create `docker-compose.yml` in the root directory:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - SERVICENOW_INSTANCE=${SERVICENOW_INSTANCE}
      - SERVICENOW_USERNAME=${SERVICENOW_USERNAME}
      - SERVICENOW_PASSWORD=${SERVICENOW_PASSWORD}
    volumes:
      - ./backend:/app
    networks:
      - claims-network

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:5000
    depends_on:
      - backend
    networks:
      - claims-network

networks:
  claims-network:
    driver: bridge
```

### 4. Run with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Or just start (if already built)
docker-compose up

# Stop services
docker-compose down
```

Access the application at:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:5000`

### 5. Environment Variables

Create `.env` file in root:

```
SERVICENOW_INSTANCE=your_instance.service-now.com
SERVICENOW_USERNAME=your_username
SERVICENOW_PASSWORD=your_password
```

## Docker Commands

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Rebuild containers
docker-compose build --no-cache

# Run specific service
docker-compose up backend
docker-compose up frontend

# Remove all containers and volumes
docker-compose down -v
```

## Deploy to Production

### Using Docker Hub

```bash
# Build image
docker build -t your-username/claims-dashboard-backend ./backend

# Tag for Docker Hub
docker tag claims-dashboard-backend:latest your-username/claims-dashboard-backend:latest

# Push to Docker Hub
docker push your-username/claims-dashboard-backend:latest

# Pull and run
docker pull your-username/claims-dashboard-backend:latest
docker run -p 5000:5000 -e SERVICENOW_INSTANCE=... your-username/claims-dashboard-backend
```

### Using Kubernetes (Optional)

Create `backend-deployment.yaml`:

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
        image: your-username/claims-dashboard-backend:latest
        ports:
        - containerPort: 5000
        env:
        - name: SERVICENOW_INSTANCE
          valueFrom:
            secretKeyRef:
              name: servicenow-secrets
              key: instance
```

Deploy with:
```bash
kubectl apply -f backend-deployment.yaml
```

---

Docker provides easy deployment and isolation of services!
