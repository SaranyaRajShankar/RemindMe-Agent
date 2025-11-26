# RemindMe Agent - Django Web Interface

An AI-powered meeting reminder system with a Django web interface for managing Google account connections.

## Features

- 🌐 **Web Dashboard** - Beautiful, responsive interface for managing accounts
- 🔐 **OAuth Integration** - Secure Google account authentication
- 👥 **Multi-User Support** - Manage multiple connected accounts
- 📧 **Email Reminders** - Automated meeting reminders via Gmail
- 📅 **Calendar Integration** - Fetches meetings from Google Calendar

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Django Setup

Run migrations to set up the database:

```bash
python manage.py migrate
```

### 3. Google OAuth Configuration

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Google Calendar API
   - Gmail API
4. Create OAuth 2.0 credentials (Desktop application)
5. Download the credentials and save as `oauthCredentials.json` in the project root
6. **Important**: Add `http://localhost:8000/auth/callback` as an authorized redirect URI in your OAuth credentials

### 4. Environment Variables

Create a `.env` file (optional, if needed):

```
GOOGLE_API_KEY=your_api_key_here
```

### 5. Run the Server

```bash
python manage.py runserver
```

The web interface will be available at: **http://localhost:8000**

## Usage

### Web Interface

1. Open `http://localhost:8000` in your browser
2. Click **"Connect Google Account"**
3. Complete the OAuth authentication flow
4. Your account will be saved and you'll receive daily meeting reminders

### Running Daily Reminders

For automated daily reminders, run:

```bash
python cron.py
```

Or set up a scheduled task/cron job to run this daily.

## Project Structure

```
.
├── manage.py                 # Django management script
├── remindme_project/         # Django project settings
│   ├── settings.py          # Configuration
│   └── urls.py              # Main URL routing
├── dashboard/                # Web application
│   ├── views.py             # API and page views
│   └── urls.py              # App URL routing
├── templates/                # HTML templates
│   ├── index.html           # Main dashboard
│   ├── success.html         # Success page
│   └── error.html           # Error page
├── static/                   # Static files
│   ├── style.css            # Stylesheet
│   └── script.js            # JavaScript
├── AgentPro.py              # Main agent application
├── cron.py                  # Daily batch processor
├── database.py              # Database operations
├── getMeeting.py            # Calendar integration
├── sendMail.py              # Email sending
└── users.db                 # SQLite database
```

## API Endpoints

- `GET /` - Dashboard homepage
- `GET /api/users` - List all connected users
- `POST /api/auth/start` - Start OAuth flow
- `GET /auth/callback` - OAuth callback handler
- `DELETE /api/users/<email>/` - Delete a user
- `GET /api/health` - Health check

## Security Notes

- Never commit `oauthCredentials.json` or `token.json` to version control
- In production, change `SECRET_KEY` in `settings.py`
- Use environment variables for sensitive configuration
- Consider using Redis or a database for OAuth state storage in production
- Update `ALLOWED_HOSTS` in `settings.py` for production deployment

## Troubleshooting

### OAuth Redirect URI Mismatch

If you get a redirect URI error, make sure:
1. The redirect URI in Google Cloud Console matches: `http://localhost:8000/auth/callback`
2. The `OAUTH_REDIRECT_URI` in `settings.py` matches exactly

### Static Files Not Loading

Run Django's collectstatic command:

```bash
python manage.py collectstatic
```

### Database Errors

If you encounter database errors, try:

```bash
python manage.py migrate --run-syncdb
```

## License

MIT

