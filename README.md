# Chakula Poa - Django REST API Backend

REST API for the Chakula Poa meal subscription platform serving all restaurants and food service locations across Tanzania.

## Table of Contents

- [Quick Start (Local Development)](#quick-start-local-development)
- [Database Configuration](#database-configuration)
- [API Endpoints](#api-endpoints)
- [Deploy to Render (Cloud)](#deploy-to-render-cloud)
- [Environment Variables](#environment-variables)
- [Location Types](#location-types)
- [User Roles](#user-roles)
- [Troubleshooting](#troubleshooting)

---

## Quick Start (Local Development)

### Prerequisites

- Python 3.11+
- pip (Python package manager)
- Git

### Step 1: Clone and Navigate

```bash
git clone https://github.com/Big-pappi/chakula-poa.git
cd chakula-poa/backend
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows (Command Prompt)
venv\Scripts\activate

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings (optional for local dev - SQLite works by default)
```

### Step 5: Run Database Migrations

```bash
python manage.py migrate
```

### Step 6: Create Initial Data

```bash
python manage.py setup_initial_data
```

This creates:
- **Super Admin Account:**
  - Email: chedybreezy@gmail.com
  - Phone: 0712000001
  - Password: Amaruwebster093@
- Sample locations (restaurants, universities, markets, offices, hospitals, industrial)
- Subscription plans (Weekly, Monthly, Semester)

### Step 7: Run Development Server

```bash
python manage.py runserver
```

The API is now running at:
- **API Base URL:** `http://127.0.0.1:8000/api/`
- **Admin Panel:** `http://127.0.0.1:8000/admin/`

---

## Database Configuration

### Option 1: SQLite (Default for Local Development)

No configuration needed. A `db.sqlite3` file will be created automatically.

Best for: Quick local testing and development.

### Option 2: PostgreSQL (Recommended for Production Parity)

1. Install PostgreSQL locally
2. Create a database:
   ```sql
   CREATE DATABASE chakula_poa;
   CREATE USER chakula_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE chakula_poa TO chakula_user;
   ```
3. Update `.env`:
   ```env
   DATABASE_URL=postgres://chakula_user:your_password@localhost:5432/chakula_poa
   ```

---

## API Endpoints

### Public Endpoints (No Authentication Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/restaurants/` | List all locations |
| GET | `/api/restaurants/types/` | Get location types |
| GET | `/api/restaurants/regions/` | Get Tanzania regions |
| POST | `/api/users/register/` | Register new user |
| POST | `/api/users/login/` | User login (returns JWT) |
| POST | `/api/token/refresh/` | Refresh JWT token |

### Authenticated Endpoints (Requires JWT Token)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/me/` | Get current user profile |
| PUT | `/api/users/me/` | Update user profile |
| GET | `/api/meals/today/` | Get today's meals |
| POST | `/api/meals/select/` | Order a meal |
| GET | `/api/subscriptions/me/` | Get user's subscription |
| GET | `/api/subscriptions/plans/` | List subscription plans |

### Staff Endpoints (Staff Role Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/staff/verify/` | Verify user CPS code |
| POST | `/api/staff/serve/` | Mark meal as served |
| GET | `/api/staff/collections/` | Get meal collections |

### Admin Endpoints (Admin Role Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/dashboard/` | Dashboard statistics |
| GET | `/api/admin/users/` | List all users |
| GET | `/api/admin/reports/demand/` | Meal demand report |
| GET | `/api/admin/reports/revenue/` | Revenue report |

### Authentication Header

Include JWT token in requests:
```
Authorization: Bearer <your_access_token>
```

---

## Hosting Options for Backend

The Django backend can be hosted on various platforms. Here are the recommended options:

| Platform | Free Tier | Best For | Database |
|----------|-----------|----------|----------|
| **Render** | Yes (with limitations) | Quick setup, auto-deploy | PostgreSQL included |
| **Railway** | Yes ($5 credit/month) | Easy scaling, good DX | PostgreSQL included |
| **PythonAnywhere** | Yes (limited) | Simple Django apps | MySQL included |
| **DigitalOcean App Platform** | No ($5/month min) | Production apps | Managed PostgreSQL |
| **Heroku** | No (paid only) | Enterprise apps | Heroku Postgres |
| **AWS Elastic Beanstalk** | Pay as you go | Large scale apps | RDS PostgreSQL |
| **Google Cloud Run** | Pay as you go | Serverless apps | Cloud SQL |

**Recommended:** Use **Render** for free hosting or **Railway** for better performance.

---

## Deploy to Render (Cloud)

### Method 1: Automatic Deployment (Recommended)

1. **Push code to GitHub**
   ```bash
   git push origin main
   ```

2. **Connect to Render**
   - Go to [render.com](https://render.com)
   - Click "New" > "Blueprint"
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml` and configure everything

3. **Wait for deployment**
   - Render will create a PostgreSQL database
   - Build and deploy the API
   - Set up environment variables automatically

4. **Get your API URL**
   - Your API will be available at: `https://chakula-poa-api.onrender.com`

### Method 2: Manual Deployment

#### Step 1: Create PostgreSQL Database

1. Go to Render Dashboard > "New" > "PostgreSQL"
2. Name: `chakula-poa-db`
3. Select free tier
4. Click "Create Database"
5. Copy the **Internal Database URL**

#### Step 2: Create Web Service

1. Go to Render Dashboard > "New" > "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name:** `chakula-poa-api`
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:**
     ```bash
     pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate && python manage.py setup_initial_data || true
     ```
   - **Start Command:**
     ```bash
     gunicorn chakula_poa.wsgi:application
     ```

#### Step 3: Set Environment Variables

In your Render web service settings, add:

| Key | Value |
|-----|-------|
| `ENVIRONMENT` | `production` |
| `DEBUG` | `false` |
| `SECRET_KEY` | (Generate a secure key) |
| `DATABASE_URL` | (Paste Internal Database URL) |
| `ALLOWED_HOSTS` | `.onrender.com` |
| `CORS_ALLOWED_ORIGINS` | `https://your-frontend.vercel.app` |

Generate a secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### Step 4: Deploy

Click "Create Web Service" and wait for deployment.

### Connecting Frontend (Vercel) to Backend (Render)

In your Vercel project, add environment variable:
```
NEXT_PUBLIC_API_URL=https://chakula-poa-api.onrender.com/api
```

---

## Deploy to Railway (Alternative)

Railway is another excellent option for hosting Django backends with PostgreSQL.

### Step 1: Install Railway CLI (Optional)
```bash
npm install -g @railway/cli
railway login
```

### Step 2: Create Project on Railway

1. Go to [railway.app](https://railway.app)
2. Click "New Project" > "Deploy from GitHub repo"
3. Select your repository and the `backend` folder as the root

### Step 3: Add PostgreSQL

1. In your Railway project, click "New" > "Database" > "PostgreSQL"
2. Railway will automatically set the `DATABASE_URL` environment variable

### Step 4: Configure Environment Variables

In Railway dashboard, go to your service settings and add:

| Variable | Value |
|----------|-------|
| `ENVIRONMENT` | `production` |
| `DEBUG` | `false` |
| `SECRET_KEY` | (Generate a secure key) |
| `ALLOWED_HOSTS` | `.railway.app,localhost` |
| `CORS_ALLOWED_ORIGINS` | `https://your-frontend.vercel.app` |

### Step 5: Configure Build Settings

- **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
- **Start Command:** `gunicorn chakula_poa.wsgi:application --bind 0.0.0.0:$PORT`

### Step 6: Deploy

Railway will automatically deploy when you push to your repository.

Your API will be available at: `https://your-project.railway.app/api/`

---

## Environment Variables

### Required for Production

| Variable | Description | Example |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment type | `production` |
| `DEBUG` | Debug mode | `false` |
| `SECRET_KEY` | Django secret key | `your-secure-key` |
| `DATABASE_URL` | PostgreSQL connection URL | `postgres://user:pass@host:5432/db` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `.onrender.com,.vercel.app` |
| `CORS_ALLOWED_ORIGINS` | Comma-separated frontend URLs | `https://chakula-poa.vercel.app` |

### Optional

| Variable | Description | Example |
|----------|-------------|---------|
| `SELCOM_API_KEY` | Selcom payment API key | `your-api-key` |
| `SELCOM_API_SECRET` | Selcom API secret | `your-secret` |
| `AT_USERNAME` | Africa's Talking username | `sandbox` |
| `AT_API_KEY` | Africa's Talking API key | `your-api-key` |

---

## Location Types

The platform supports various food service locations:

| Type | Description | Example |
|------|-------------|---------|
| `restaurant` | Standalone restaurants | Mama Lishe Kariakoo |
| `university` | University canteens | UDSM, UDOM, Mzumbe |
| `market` | Market area eateries | Kariakoo Market |
| `office` | Corporate cafeterias | TRA Staff Canteen |
| `hospital` | Hospital cafeterias | Muhimbili Cafeteria |
| `industrial` | Factory canteens | Ubungo Industrial |

---

## User Roles

| Role | Permissions |
|------|-------------|
| `user` | Subscribe, order meals, view QR code |
| `staff` | Verify codes, serve meals, view collections |
| `admin` | Manage restaurant, users, reports |
| `super_admin` | Full system access, all restaurants |
| `developer` | API access, debugging |

---

## Troubleshooting

### Common Issues

**1. "No module named 'xxx'" error**
```bash
pip install -r requirements.txt
```

**2. Database migration errors**
```bash
python manage.py makemigrations
python manage.py migrate
```

**3. Static files not loading (production)**
```bash
python manage.py collectstatic --noinput
```

**4. CORS errors**
- Ensure `CORS_ALLOWED_ORIGINS` includes your frontend URL
- Check that the URL has no trailing slash

**5. JWT token expired**
- Use the refresh token endpoint: `POST /api/token/refresh/`
- Access tokens expire in 24 hours
- Refresh tokens expire in 7 days

### Health Check

Test if the API is running:
```bash
curl https://your-api-url.onrender.com/api/restaurants/
```

---

## Development Team

| Role | Name | Contact |
|------|------|---------|
| Frontend Developer | Philip Steven Chediel | +255 620 636 893 |
| Backend Developer | Beatrice | +255 687 156 586 |

Website: [www.bluegrid.co.tz](https://www.bluegrid.co.tz)
