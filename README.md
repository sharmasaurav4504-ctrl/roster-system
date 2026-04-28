# Roster Management System

A Django-based web application for managing employee rosters, leave requests, and shift swaps.

## Features

- Employee management with role-based access
- Roster scheduling and visualization
- Leave request system
- Shift swap requests
- CSV import/export functionality
- Responsive web interface

## Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run migrations:
   ```bash
   python manage.py migrate
   ```

3. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

4. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Deployment to Render

This project is configured for deployment on Render.com.

### Prerequisites

- A Render.com account
- Git repository with this code

### Deployment Steps

1. **Connect Repository**: Connect your GitHub/GitLab repository to Render.

2. **Create Web Service**:
   - Service Type: Web Service
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
   - Start Command: `gunicorn roster_system.wsgi:application --bind 0.0.0.0:$PORT`

3. **Environment Variables**:
   - `DEBUG`: `False`
   - `SECRET_KEY`: Generate a new secret key (or use the existing one securely)
   - `ALLOWED_HOSTS`: Your Render app URL (e.g., `your-app.onrender.com`)
   - `DATABASE_URL`: Provided automatically by Render's PostgreSQL database

4. **Database Setup**:
   - Add a PostgreSQL database in Render
   - Migrations will run automatically during build
   - If you have existing data, load it after deployment:
     ```bash
     # In Render's shell or via SSH
     python manage.py loaddata auth_data.json core_data.json
     ```

5. **Create Admin User**:
   After deployment, create a superuser:
   ```bash
   # In Render's shell
   python manage.py createsuperuser
   ```

### Alternative: Using render.yaml

If using Render's Blueprint deployment:

1. Push the `render.yaml` file to your repository
2. Connect the repository to Render
3. Render will automatically create the web service and database

## Project Structure

- `roster_system/`: Django project settings
- `core/`: Main application with models, views, templates
- `static/`: Static files (CSS, JS, images)
- `templates/`: HTML templates
- `requirements.txt`: Python dependencies
- `render.yaml`: Render deployment configuration

## Models

- **Employee**: User profiles with roles (WFM, Supervisor, Agent)
- **Roster**: Employee shift assignments by date
- **LeaveRequest**: Employee leave applications
- **SwapRequest**: Shift swap requests between employees

## Security Notes

- DEBUG is set to False in production
- SECRET_KEY should be kept secure
- ALLOWED_HOSTS is restricted to your domain
- CSRF protection is enabled
- HTTPS is enforced via SECURE_PROXY_SSL_HEADER