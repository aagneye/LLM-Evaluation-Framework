# Deployment Guide

## Quick Start (Development)

```bash
# 1. Clone repository
git clone <repository-url>
cd llm-eval-framework

# 2. Set up environment
cp .env.example .env
# Edit .env and add your API keys

# 3. Start services
docker-compose up -d

# 4. Access application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000/docs
# Grafana: http://localhost:3000
```

## Production Deployment

### Prerequisites

- Docker 24+ and Docker Compose
- Domain name with DNS configured
- SSL certificates
- PostgreSQL (managed service recommended)
- Redis (managed service recommended)
- S3-compatible storage

### Environment Variables

Create `.env.production`:

```bash
# Database
POSTGRES_USER=llmeval
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=llm_eval_prod

# Redis
REDIS_URL=redis://<redis-host>:6379/0

# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
SECRET_KEY=<generate-with-openssl-rand-hex-32>

# S3 Storage
S3_ENDPOINT_URL=https://s3.amazonaws.com
S3_BUCKET_NAME=llm-eval-datasets
S3_ACCESS_KEY=...
S3_SECRET_KEY=...

# Monitoring
GRAFANA_PASSWORD=<strong-password>

# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
JSON_LOGS=true
```

### Deploy with Docker Compose

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f backend
```

### Database Migration

```bash
# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Create initial superuser
docker-compose -f docker-compose.prod.yml exec backend python -m app.scripts.create_superuser
```

### Nginx Configuration

Create `/etc/nginx/sites-available/llm-eval`:

```nginx
upstream backend {
    server localhost:8000;
}

upstream frontend {
    server localhost:80;
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /ws/ {
        proxy_pass http://backend/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Kubernetes Deployment

```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-eval-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: llm-eval-backend
  template:
    metadata:
      labels:
        app: llm-eval-backend
    spec:
      containers:
      - name: backend
        image: llm-eval-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: llm-eval-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: llm-eval-secrets
              key: redis-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: llm-eval-backend
spec:
  selector:
    app: llm-eval-backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

### AWS Deployment

#### Using ECS Fargate

```bash
# 1. Create ECR repositories
aws ecr create-repository --repository-name llm-eval-backend
aws ecr create-repository --repository-name llm-eval-frontend

# 2. Build and push images
docker build -t llm-eval-backend:latest -f backend/Dockerfile.prod backend/
docker tag llm-eval-backend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/llm-eval-backend:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/llm-eval-backend:latest

# 3. Create ECS cluster
aws ecs create-cluster --cluster-name llm-eval-cluster

# 4. Create task definition (see task-definition.json)
aws ecs register-task-definition --cli-input-json file://task-definition.json

# 5. Create service
aws ecs create-service \
  --cluster llm-eval-cluster \
  --service-name llm-eval-backend \
  --task-definition llm-eval-backend \
  --desired-count 2 \
  --launch-type FARGATE
```

#### Using RDS and ElastiCache

```bash
# Create RDS PostgreSQL
aws rds create-db-instance \
  --db-instance-identifier llm-eval-db \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --master-username admin \
  --master-user-password <password> \
  --allocated-storage 100

# Create ElastiCache Redis
aws elasticache create-cache-cluster \
  --cache-cluster-id llm-eval-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1
```

### Monitoring Setup

#### Prometheus

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'llm-eval-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
```

#### Grafana

1. Access Grafana at http://localhost:3000
2. Login with admin/<GRAFANA_PASSWORD>
3. Add Prometheus data source
4. Import dashboard from `monitoring/grafana-dashboard.json`

### Backup Strategy

#### Database Backups

```bash
# Automated daily backup
0 2 * * * docker-compose -f docker-compose.prod.yml exec -T postgres \
  pg_dump -U postgres llm_eval_prod | gzip > /backups/llm_eval_$(date +\%Y\%m\%d).sql.gz

# Restore from backup
gunzip < /backups/llm_eval_20240315.sql.gz | \
  docker-compose -f docker-compose.prod.yml exec -T postgres \
  psql -U postgres llm_eval_prod
```

#### Redis Backups

```bash
# Trigger Redis save
docker-compose -f docker-compose.prod.yml exec redis redis-cli BGSAVE

# Copy RDB file
docker cp <container-id>:/data/dump.rdb /backups/redis_$(date +\%Y\%m\%d).rdb
```

### Scaling

#### Horizontal Scaling

```bash
# Scale workers
docker-compose -f docker-compose.prod.yml up -d --scale worker=5

# Scale backend (with load balancer)
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

#### Vertical Scaling

Update resource limits in `docker-compose.prod.yml`:

```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 4G
      reservations:
        cpus: '1'
        memory: 2G
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Metrics
curl http://localhost:8000/metrics

# Database connection
docker-compose -f docker-compose.prod.yml exec postgres pg_isready

# Redis connection
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping
```

### Troubleshooting

#### View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100 backend
```

#### Common Issues

**Database connection failed**:
```bash
# Check database is running
docker-compose -f docker-compose.prod.yml ps postgres

# Check connection
docker-compose -f docker-compose.prod.yml exec backend \
  python -c "from app.database import engine; engine.connect()"
```

**Redis connection failed**:
```bash
# Check Redis is running
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping

# Check connection from backend
docker-compose -f docker-compose.prod.yml exec backend \
  python -c "from redis import Redis; Redis.from_url('redis://redis:6379/0').ping()"
```

**Worker not processing jobs**:
```bash
# Check worker logs
docker-compose -f docker-compose.prod.yml logs -f worker

# Check queue length
docker-compose -f docker-compose.prod.yml exec redis redis-cli LLEN rq:queue:experiments
```

### Security Hardening

1. **Use secrets management**:
   - AWS Secrets Manager
   - HashiCorp Vault
   - Kubernetes Secrets

2. **Enable firewall**:
   ```bash
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw enable
   ```

3. **Regular updates**:
   ```bash
   docker-compose -f docker-compose.prod.yml pull
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **Monitor security logs**:
   ```bash
   docker-compose -f docker-compose.prod.yml logs -f | grep -i "security\|attack\|injection"
   ```

### Performance Tuning

**PostgreSQL**:
```sql
-- Increase connection pool
ALTER SYSTEM SET max_connections = 200;

-- Tune memory
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '6GB';
```

**Redis**:
```bash
# Increase max memory
redis-cli CONFIG SET maxmemory 2gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

**Uvicorn Workers**:
```yaml
backend:
  command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```
