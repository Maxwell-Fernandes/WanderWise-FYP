# WanderWise+ Quick Start Guide

## 🚀 Get Started in 10 Minutes

### Prerequisites Check

```bash
# Check Python version (need 3.11+)
python --version

# Check PostgreSQL (need 12+)
psql --version

# Check PostGIS
psql -U postgres -c "SELECT PostGIS_version();"
```

If any are missing, see SETUP_SUMMARY.md for installation instructions.

---

## Step 1: Database Setup (2 minutes)

```bash
# Create database
sudo -u postgres psql << EOF
CREATE DATABASE wanderwise_db;
CREATE USER wanderwise_user WITH ENCRYPTED PASSWORD 'change_this_password';
GRANT ALL PRIVILEGES ON DATABASE wanderwise_db TO wanderwise_user;
\c wanderwise_db
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
EOF

# Run setup script
psql -U wanderwise_user -d wanderwise_db -f database/database_setup.sql
```

**✓ Expected:** "WanderWise+ Database Setup Complete!" message

---

## Step 2: Python Environment (3 minutes)

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
```

**✓ Expected:** ~60 packages installed successfully

---

## Step 3: Configuration (1 minute)

```bash
# Copy and edit environment file
cp backend/.env.example backend/.env
nano backend/.env  # or use your preferred editor
```

**Required changes:**
```env
DB_PASSWORD="your_actual_password_here"
SECRET_KEY="$(openssl rand -hex 32)"
```

Save and exit.

---

## Step 4: Import Data (2 minutes)

```bash
# Run import script
python backend/scripts/import_csv_data.py
```

**✓ Expected:** "Successfully inserted 100 places"

---

## Step 5: Optimize (Optional, 2 minutes)

```bash
# Populate distance matrix for faster route optimization
psql -U wanderwise_user -d wanderwise_db << EOF
SELECT populate_full_distance_matrix();
REFRESH MATERIALIZED VIEW popular_places;
REFRESH MATERIALIZED VIEW goa_beaches;
EOF
```

**✓ Expected:** Query returns row count (~10,000 entries)

---

## ✅ Verification

### Check Database

```bash
psql -U wanderwise_user -d wanderwise_db -c "SELECT COUNT(*) FROM goa_places;"
```

**Expected:** 100

### Check Distance Matrix (if you ran Step 5)

```bash
psql -U wanderwise_user -d wanderwise_db -c "SELECT COUNT(*) FROM distance_matrix;"
```

**Expected:** ~9,900

---

## 🎯 What's Next?

Your database is ready! Now you need to build the FastAPI backend.

### Recommended Order:

1. **Configuration & Database Connection**
   - Create `backend/app/config.py`
   - Create `backend/app/database.py`

2. **Models**
   - Create `backend/app/models/places.py`

3. **Schemas**
   - Create `backend/app/schemas/places.py`

4. **API Endpoints**
   - Create `backend/app/api/places.py`
   - Create `backend/app/main.py`

5. **Test It**
   ```bash
   uvicorn app.main:app --reload
   ```
   Visit: http://localhost:8000/docs

---

## 📚 Documentation

- **Full Setup:** See `SETUP_SUMMARY.md`
- **Development Guide:** See `CLAUDE.md`
- **Project Overview:** See `README.md`
- **Database Schema:** See `database/database_setup.sql` (has comments)

---

## 🆘 Quick Fixes

### "Database does not exist"
```bash
sudo -u postgres psql -c "CREATE DATABASE wanderwise_db;"
```

### "PostGIS extension not found"
```bash
sudo apt install postgresql-12-postgis-3
```

### "Permission denied"
```bash
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE wanderwise_db TO wanderwise_user;"
```

### "Module not found" errors
```bash
source venv/bin/activate
pip install -r backend/requirements.txt
```

---

## 💡 Pro Tips

1. **Keep venv activated:** All Python commands need venv active
2. **Check logs:** PostgreSQL logs at `/var/log/postgresql/`
3. **Use pgAdmin:** Install pgAdmin4 for GUI database management
4. **Test queries:** Use psql or DBeaver to test SQL queries
5. **IDE setup:** Use VSCode with Python + PostgreSQL extensions

---

**Ready to code?** Start with `backend/app/config.py` and follow the structure in `CLAUDE.md`!
