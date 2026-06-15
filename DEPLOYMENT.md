# Deployment Guide for AjesConnect

## Quick Summary
AjesConnect is ready for production deployment with:
- **Gunicorn** web server for handling requests
- **WhiteNoise** for serving static files efficiently
- **PostgreSQL** for production database (optional SQLite for small deployments)
- **AWS S3** for user uploads/media files (optional, defaults to local storage)
- **Sentry** for error tracking (optional)

---

## Development Setup (Local)

```bash
# Clone and setup
cd "Ajes connect"
python -m venv venv
.\venv\Scripts\activate

# Copy and configure environment
cp .env.example .env
# Edit .env with your development settings

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Run development server
python manage.py runserver
```

---

## Production Deployment

### 1. Environment Setup

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with production values:

```
DJANGO_SECRET_KEY=<generate-new-secret-key>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

**Generate a new secret key:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2. Database Setup

#### Option A: PostgreSQL (Recommended)

```bash
# Install PostgreSQL locally or use managed service (Heroku, RDS, etc.)
# Update .env:
DB_ENGINE=django.db.backends.postgresql
DB_NAME=ajesconnect
DB_USER=postgres
DB_PASSWORD=<strong-password>
DB_HOST=<postgres-host>
DB_PORT=5432

# Run migrations
python manage.py migrate
```

#### Option B: SQLite (Small deployments)
Default settings use SQLite - works fine for low-traffic sites.

### 3. Email Configuration

For password reset emails to work, configure SMTP:

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=<app-specific-password>
```

**Gmail setup:**
1. Enable 2-Factor Authentication on Google Account
2. Create App Password: https://myaccount.google.com/apppasswords
3. Use the generated 16-character password in `.env`

### 4. Static Files

```bash
# Collect static files (run once before deployment)
python manage.py collectstatic --noinput
```

WhiteNoise automatically serves these in production without needing separate web server configuration.

### 5. Media Files (User Uploads)

#### Option A: AWS S3 (Recommended)
```
DJANGO_USE_S3=True
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
AWS_STORAGE_BUCKET_NAME=<bucket-name>
AWS_S3_REGION_NAME=us-east-1
```

**Setup:**
1. Create S3 bucket on AWS
2. Create IAM user with S3 access
3. Note access key and secret

#### Option B: Local Storage
Leave `DJANGO_USE_S3=False` - works fine for smaller deployments.

### 6. Run Gunicorn Server

```bash
# Test Gunicorn locally
gunicorn AjesConnect.wsgi:application --bind 0.0.0.0:8000

# Or use Procfile (for Heroku/PaaS)
# Already configured: web: gunicorn AjesConnect.wsgi:application
```

---

## Deployment Platforms

### Heroku

```bash
# Install Heroku CLI, login
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set DJANGO_SECRET_KEY=<secret>
heroku config:set DJANGO_DEBUG=False
heroku config:set SECURE_SSL_REDIRECT=True
# ... set other variables from .env

# For PostgreSQL addon:
heroku addons:create heroku-postgresql:hobby-dev

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser
```

### Traditional Server (VPS/Dedicated)

```bash
# On your server:

# 1. Install system dependencies
sudo apt-get update
sudo apt-get install python3-pip python3-venv postgresql nginx

# 2. Clone repository
git clone <repo-url>
cd "Ajes connect"

# 3. Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Configure PostgreSQL
sudo -u postgres createdb ajesconnect
sudo -u postgres createuser ajesconnect_user
# Set password, grant privileges

# 5. Setup .env file
cp .env.example .env
# Edit with actual values

# 6. Collect static files
python manage.py collectstatic --noinput

# 7. Run migrations
python manage.py migrate

# 8. Create superuser
python manage.py createsuperuser

# 9. Run Gunicorn with systemd service
sudo tee /etc/systemd/system/ajesconnect.service > /dev/null << EOF
[Unit]
Description=AjesConnect Gunicorn
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/ajesconnect
ExecStart=/path/to/ajesconnect/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 AjesConnect.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable ajesconnect
sudo systemctl start ajesconnect

# 10. Configure Nginx as reverse proxy
sudo tee /etc/nginx/sites-available/ajesconnect > /dev/null << EOF
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/ajesconnect /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 11. SSL with Let's Encrypt (certbot)
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## Post-Deployment

### Verify Deployment

```bash
python manage.py check --deploy
```

Should show: `System check identified no issues (0 silenced)`

### Monitor Errors

If Sentry is configured, errors are automatically tracked. Otherwise check:
```bash
# Server logs
python manage.py runserver --verbosity 2

# Or systemd journal (VPS)
sudo journalctl -u ajesconnect -f
```

### Test Email

1. Visit `/compte/mot-de-passe-oublie/`
2. Enter your email
3. Check inbox for password reset link

---

## Troubleshooting

### Static files not loading
```bash
python manage.py collectstatic --clear --noinput
```

### Database connection error
- Verify PostgreSQL is running
- Check DB_HOST, DB_PORT, DB_USER, DB_PASSWORD in .env
- Ensure database exists: `createdb ajesconnect`

### Email not sending
- Verify EMAIL_HOST, EMAIL_PORT in .env
- Check app password (not regular password for Gmail)
- Test with: `python manage.py shell`
```python
from django.core.mail import send_mail
send_mail('Test', 'Body', 'from@example.com', ['to@example.com'])
```

### S3 upload failures
- Verify AWS credentials in .env
- Check S3 bucket exists and is in correct region
- Verify IAM user has `s3:*` permissions

---

## Performance Checklist

- [ ] DJANGO_DEBUG = False
- [ ] Secret key is unique and secure
- [ ] Database is PostgreSQL (not SQLite for production)
- [ ] HTTPS enabled (SECURE_SSL_REDIRECT=True)
- [ ] Static files collected and cached by WhiteNoise
- [ ] Media files stored on S3 (if applicable)
- [ ] Sentry configured for error tracking
- [ ] Email working (test password reset)
- [ ] Backup strategy in place (database, media)

---

## Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/)
- [Gunicorn Documentation](https://gunicorn.org/)
- [AWS S3 Setup](https://aws.amazon.com/s3/)
- [Sentry Documentation](https://docs.sentry.io/)
