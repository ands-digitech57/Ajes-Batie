Integration steps (quick)

1. Create and activate a virtual environment (Windows PowerShell):

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. `.env` is already created with a secure secret key. Update it with your values:

```powershell
# Edit .env and set your email credentials for password reset to work
# EMAIL_HOST=smtp.gmail.com (or your provider)
# EMAIL_HOST_USER=your-email@example.com
# EMAIL_HOST_PASSWORD=your-app-password-or-smtp-password
# DEFAULT_FROM_EMAIL=no-reply@ajesconnect.com
```

4. Run migrations and create a superuser:

```powershell
python manage.py migrate
python manage.py createsuperuser
```

5. Run the development server:

```powershell
python manage.py runserver
```

6. Test password reset:
- Go to http://127.0.0.1:8000/compte/connexion/
- Click "Mot de passe oublié ?"
- Enter an email address associated with a user account
- Check your email inbox (or spam folder) for the reset link

Notes:
- Static files will be collected into the `staticfiles` folder when running `collectstatic`.
- If you use image fields, ensure `Pillow` is installed (already in `requirements.txt`).

Database and media configuration:
- By default the project uses SQLite locally with `DB_ENGINE=django.db.backends.sqlite3` and `DB_NAME=db.sqlite3`.
- For PostgreSQL, set `DB_ENGINE=django.db.backends.postgresql`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.
- Static files are served from `static/` in development and collected into `staticfiles/` for production.
- Media uploads are stored under `media/`.

Password reset (test and production)

- Local testing (development): the project uses the console email backend by default so password reset emails are printed in the server console. To test:

```powershell
# Start server (if not already running)
python manage.py runserver
# Visit http://127.0.0.1:8000/compte/mot-de-passe-oublie/ and submit the user's email.
# Look at the terminal where runserver runs: you'll see the reset URL printed. Paste it in the browser to set a new password.
```

- Production: set SMTP environment variables and switch the email backend. Example env vars to set in `.env`:

```
DJANGO_EMAIL_BACKEND=smtp
EMAIL_HOST=smtp.yourprovider.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-smtp-username
EMAIL_HOST_PASSWORD=your-smtp-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=no-reply@yourdomain.com
```

- Use a real secret key and disable debug before going live:

```powershell
DJANGO_SECRET_KEY=replace-me-with-a-secure-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

- Security settings for production:

```powershell
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_PROXY_SSL_HEADER=1
```

Mailgun (SMTP) example — works with the same SMTP settings above (replace host/credentials):

```
DJANGO_EMAIL_BACKEND=smtp
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_HOST_USER=postmaster@sandboxXXXX.mailgun.org
EMAIL_HOST_PASSWORD=your-mailgun-smtp-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=MySite <no-reply@yourdomain.com>
```

AWS SES (SMTP) example — use SES SMTP credentials or install `django-ses` for API mode:

```
DJANGO_EMAIL_BACKEND=ses
SES_SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SES_SMTP_PORT=587
SES_SMTP_USER=YOUR_SES_SMTP_USERNAME
SES_SMTP_PASSWORD=YOUR_SES_SMTP_PASSWORD
SES_EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=no-reply@yourdomain.com
```

Then restart the app. Password reset links will be sent by email to users.

Production deployment

To deploy to production with HTTPS and security hardening:

1. Update `.env` for production:

```env
DJANGO_SECRET_KEY=your-secure-key-generated
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Use a real SMTP service
DJANGO_EMAIL_BACKEND=smtp
EMAIL_HOST=smtp.yourprovider.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-username
EMAIL_HOST_PASSWORD=your-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=no-reply@yourdomain.com

# Security settings for production
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_PROXY_SSL_HEADER=1
```

2. Collect static files:

```powershell
python manage.py collectstatic --noinput
```

3. Run with a production WSGI server (e.g., Gunicorn):

```powershell
pip install gunicorn
gunicorn AjesConnect.wsgi --bind 0.0.0.0:8000
```

4. Use a reverse proxy (nginx/Apache) to serve HTTPS and media files.

Testing notes
- Password reset emails are sent via configured SMTP backend. Test locally with `EMAIL_HOST=smtp.gmail.com` and an app-specific password if using Gmail.
- To check security warnings locally, run: `python manage.py check --deploy`. This will show you what needs to be enabled for production.
- The `.env` file is already protected in `.gitignore`, so it won't be committed to version control.
- For development, `DEBUG=True` and missing security headers are fine. In production, update `.env` to set `DEBUG=False` and security headers as shown above.
