# AWS Deployment Guide

## Prerequisites
- AWS CLI configured with appropriate credentials
- Docker installed (optional, for containerized deployment)

## Option 1: EC2 (Manual)

1. Launch an EC2 instance (Ubuntu 22.04, t3.medium recommended)
2. SSH into the instance
3. Install dependencies:
   ```bash
   sudo apt update && sudo apt install -y python3-pip postgresql
   pip install -r requirements.txt
   ```
4. Set up PostgreSQL and run `db/schema.sql`
5. Set environment variables in `/etc/environment`
6. Run with systemd or screen:
   ```bash
   uvicorn api.main:app --host 0.0.0.0 --port 8000
   ```

## Option 2: AWS Lambda + API Gateway

1. Package the application using Mangum adapter:
   ```python
   from mangum import Mangum
   from api.main import app
   handler = Mangum(app)
   ```
2. Create a Lambda function (Python 3.12)
3. Set API Gateway as trigger
4. Use RDS Proxy for PostgreSQL connection management
5. Store secrets in AWS Secrets Manager

## Option 3: ECS (Docker)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## AWS Services Used
- **EC2 / ECS** - Application hosting
- **RDS (PostgreSQL)** - Persistent storage
- **S3** - Static frontend hosting
- **Lambda** - Serverless agent execution
- **API Gateway** - REST endpoint management
- **CloudWatch** - Monitoring and logging

## CI/CD Pipeline (GitHub Actions)
```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to EC2
        run: |
          ssh -o StrictHostKeyChecking=no ubuntu@$EC2_HOST "
            cd smart-inbox-agent &&
            git pull &&
            pip install -r requirements.txt &&
            sudo systemctl restart smart-inbox
          "
```
