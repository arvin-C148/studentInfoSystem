# Student Information System - Production Deployment Guide

## Overview

This guide covers deploying your Student Information System to production with proper security measures and best practices.

## Pre-Deployment Checklist

### 1. Security Configuration

- [ ] Change default passwords for all users
- [ ] Generate a strong, unique `FLASK_SECRET_KEY`
- [ ] Set `FLASK_ENV=production`
- [ ] Configure HTTPS/SSL certificates
- [ ] Set up proper logging
- [ ] Review and test RLS policies

### 2. Database Security

- [ ] Enable Row Level Security (RLS) on all tables
- [ ] Test all RLS policies with different user roles
- [ ] Set up database backups
- [ ] Configure connection pooling
- [ ] Monitor database performance

### 3. Environment Variables

Create a production `.env` file with:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-url.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here

# Flask Configuration
FLASK_SECRET_KEY=your-super-secret-key-change-this-in-production
FLASK_ENV=production

# Database Configuration (Optional)
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.your-project-url.supabase.co:5432/postgres
```

## Deployment Options

### Option 1: Heroku Deployment

1. **Install Heroku CLI**
   ```bash
   # Download and install from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Create Heroku App**
   ```bash
   heroku create your-app-name
   ```

3. **Add PostgreSQL Add-on**
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

4. **Set Environment Variables**
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set FLASK_SECRET_KEY=your-secret-key
   heroku config:set SUPABASE_URL=your-supabase-url
   heroku config:set SUPABASE_ANON_KEY=your-supabase-anon-key
   ```

5. **Deploy**
   ```bash
   git add .
   git commit -m "Production deployment"
   git push heroku main
   ```

### Option 2: DigitalOcean App Platform

1. **Create App**
   - Go to DigitalOcean App Platform
   - Connect your GitHub repository
   - Select Python as the runtime

2. **Configure Environment**
   - Set environment variables in the dashboard
   - Configure build commands if needed

3. **Deploy**
   - DigitalOcean will automatically deploy on git push

### Option 3: AWS Elastic Beanstalk

1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize EB Application**
   ```bash
   eb init
   eb create production
   ```

3. **Set Environment Variables**
   ```bash
   eb setenv FLASK_ENV=production
   eb setenv FLASK_SECRET_KEY=your-secret-key
   eb setenv SUPABASE_URL=your-supabase-url
   eb setenv SUPABASE_ANON_KEY=your-supabase-anon-key
   ```

4. **Deploy**
   ```bash
   eb deploy
   ```

### Option 4: Docker Deployment

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   EXPOSE 5000
   
   CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
   ```

2. **Create docker-compose.yml**
   ```yaml
   version: '3.8'
   services:
     web:
       build: .
       ports:
         - "5000:5000"
       environment:
         - FLASK_ENV=production
         - FLASK_SECRET_KEY=${FLASK_SECRET_KEY}
         - SUPABASE_URL=${SUPABASE_URL}
         - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
   ```

3. **Deploy**
   ```bash
   docker-compose up -d
   ```

## Production Configuration

### 1. WSGI Server

Install and configure Gunicorn:

```bash
pip install gunicorn
```

Create `wsgi.py`:
```python
from app import app

if __name__ == "__main__":
    app.run()
```

### 2. Reverse Proxy (Nginx)

Install and configure Nginx:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. SSL/HTTPS Configuration

Use Let's Encrypt for free SSL certificates:

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 4. Process Management (Systemd)

Create `/etc/systemd/system/student-info-system.service`:

```ini
[Unit]
Description=Student Information System
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/your/app
Environment="PATH=/path/to/your/venv/bin"
ExecStart=/path/to/your/venv/bin/gunicorn --workers 3 --bind unix:student-info-system.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable student-info-system
sudo systemctl start student-info-system
```

## Security Best Practices

### 1. Database Security

- Use strong passwords for database access
- Enable SSL connections to Supabase
- Regularly rotate API keys
- Monitor database access logs

### 2. Application Security

- Enable HTTPS only
- Set secure headers
- Implement rate limiting
- Use secure session configuration

### 3. Server Security

- Keep system packages updated
- Configure firewall rules
- Use SSH key authentication
- Regular security audits

## Monitoring and Logging

### 1. Application Logging

Configure logging in your application:

```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/student_info_system.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Student Information System startup')
```

### 2. Performance Monitoring

- Set up application performance monitoring (APM)
- Monitor database query performance
- Track user activity and errors
- Set up alerts for critical issues

### 3. Health Checks

Create a health check endpoint:

```python
@app.route('/health')
def health_check():
    try:
        # Test database connection
        db.get_statistics()
        return {'status': 'healthy', 'database': 'connected'}, 200
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 500
```

## Backup Strategy

### 1. Database Backups

- Supabase provides automatic backups
- Set up additional backup strategies
- Test backup restoration procedures
- Store backups in multiple locations

### 2. Application Backups

- Backup configuration files
- Backup uploaded files (if any)
- Version control all code changes
- Document deployment procedures

## Scaling Considerations

### 1. Horizontal Scaling

- Use load balancers for multiple instances
- Configure session storage (Redis)
- Implement proper caching strategies
- Monitor resource usage

### 2. Database Scaling

- Monitor database performance
- Optimize queries and indexes
- Consider read replicas for heavy read loads
- Plan for database sharding if needed

## Maintenance

### 1. Regular Updates

- Keep dependencies updated
- Monitor security advisories
- Update SSL certificates
- Review and update documentation

### 2. Performance Optimization

- Monitor application performance
- Optimize database queries
- Implement caching where appropriate
- Regular performance audits

## Troubleshooting

### Common Issues:

1. **Database Connection Errors**
   - Check Supabase credentials
   - Verify network connectivity
   - Check RLS policies

2. **Performance Issues**
   - Monitor database query performance
   - Check application logs
   - Review server resources

3. **Security Issues**
   - Review access logs
   - Check for suspicious activity
   - Update security configurations

## Support and Documentation

- Maintain comprehensive documentation
- Set up user support channels
- Create troubleshooting guides
- Regular system health checks

## Emergency Procedures

1. **System Outage**
   - Identify the issue
   - Implement temporary fixes
   - Communicate with users
   - Plan permanent solutions

2. **Security Breach**
   - Isolate affected systems
   - Assess the damage
   - Implement security patches
   - Notify relevant parties

3. **Data Loss**
   - Stop further data loss
   - Restore from backups
   - Investigate root cause
   - Implement preventive measures 