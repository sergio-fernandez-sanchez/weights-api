# Weights API

REST API for personal body tracking built with FastAPI and PostgreSQL. Manages daily weight logs, training phases (bulk, cut, maintenance), bioimpedance reports, DEXA reports, body measurements, calorie targets, gym performance tracking, user profiles, weekly lifestyle reports and AI report generation. Includes JWT authentication with multi-user support.

Deployed on Railway. Automatically pauses at 23:00 and resumes at 8:00 (Spain time) to stay within the free tier.

Part of the [Weights Client](https://github.com/sergio-fernandez-sanchez/weights-client) project ecosystem.

---

## Demo account

| Field | Value |
|---|---|
| Email | demo@gmail.com |
| Password | 1234 |

---

## Endpoints

### Auth
| Method | Route | Description |
|---|---|---|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and get a JWT token |

### Weights
| Method | Route | Description |
|---|---|---|
| GET | `/weights` | Get all weight records |
| GET | `/weights/last` | Get the most recent weight record |
| GET | `/weights/with-phase` | Get all weights with their phase type |
| POST | `/weights` | Add or update today's weight |

### Phases
| Method | Route | Description |
|---|---|---|
| GET | `/phases` | Get all training phases |
| GET | `/phases/active` | Get the current active phase |
| POST | `/phases` | Close current phase (end_date = start - 1 day) and start a new one |
| PATCH | `/phases/active` | Update weight goal and date goal of the active phase |

### Bioimpedance Reports
| Method | Route | Description |
|---|---|---|
| GET | `/bioimpedance-reports` | Get all bioimpedance reports |
| POST | `/bioimpedance-reports` | Add a new bioimpedance report (optional date) |

### DEXA Reports
| Method | Route | Description |
|---|---|---|
| GET | `/dexa-reports` | Get all DEXA reports |
| POST | `/dexa-reports` | Add a new DEXA report (optional date) |

### Body Measurements
| Method | Route | Description |
|---|---|---|
| GET | `/body-measurements` | Get all body measurements |
| POST | `/body-measurements` | Add a new body measurement (optional date) |

### Calories
| Method | Route | Description |
|---|---|---|
| GET | `/calories` | Get full calorie target history |
| GET | `/calories/active` | Get current calorie target |
| POST | `/calories` | Close current target (end_date = yesterday) and set a new one |

### Gym
| Method | Route | Description |
|---|---|---|
| GET | `/gym/exercise-types` | Get all available exercise types (global + user custom) |
| POST | `/gym/exercise-types` | Create a custom exercise type |
| GET | `/gym/logs` | Get full gym log history with exercise names |
| GET | `/gym/logs/active` | Get active gym logs (no end date) with exercise names |
| POST | `/gym/logs` | Add a new gym log entry |
| PATCH | `/gym/logs/{log_id}` | Close current log (end_date = yesterday) and insert updated one |
| DELETE | `/gym/logs/{log_id}` | Close a gym log (end_date = yesterday) |

### Profile
| Method | Route | Description |
|---|---|---|
| GET | `/profile` | Get user personal data |
| PATCH | `/profile` | Create or update user personal data |

### Weekly Reports
| Method | Route | Description |
|---|---|---|
| GET | `/weekly-reports` | Get all weekly lifestyle reports |
| GET | `/weekly-reports/{week_start}` | Get weekly report for a specific week (YYYY-MM-DD, must be a Monday) |
| PATCH | `/weekly-reports` | Create or update a weekly report |

### AI Reports
| Method | Route | Description |
|---|---|---|
| GET | `/generate-report` | Generate optimized JSON report for AI analysis (notes, profile, phases, weekly blocks, gym history, reports) |
| GET | `/generate-report/raw` | Generate full raw JSON data (all records unprocessed, separated by section) |

All endpoints except `/auth/register` and `/auth/login` require a valid JWT token in the `Authorization: Bearer <token>` header.

---

## Project Structure

```
weights-api/
├── core/
│   ├── services.py          # Business logic
│   └── report_generator.py  # AI report JSON generation (two report types)
├── db/
│   ├── database.py          # PostgreSQL connection
│   └── queries.py           # SQL queries
├── api/
│   ├── main.py              # FastAPI app and routes
│   ├── auth.py              # JWT authentication
│   └── schemas.py           # Pydantic input/output models
├── .github/
│   └── workflows/
│       └── schedule.yml     # Auto pause/resume Railway service
├── Procfile                 # Railway start command
└── requirements.txt
```

---

## Installation

**1. Clone the repository**
```bash
git clone https://github.com/sergio-fernandez-sanchez/weights-api.git
cd weights-api
```

**2. Create and activate a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Create a PostgreSQL database and tables**
```bash
psql postgres
CREATE DATABASE weights;
\q
psql weights
```

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE weights (
    id SERIAL PRIMARY KEY,
    date DATE,
    weight NUMERIC(5,2),
    user_id INTEGER REFERENCES users(id)
);

CREATE TABLE phases (
    id SERIAL PRIMARY KEY,
    start_date DATE NOT NULL,
    end_date DATE NULL,
    phase_type VARCHAR(50) NOT NULL,
    weight_goal NUMERIC(5,2) NULL,
    date_goal DATE NULL,
    user_id INTEGER REFERENCES users(id)
);

CREATE TABLE bioimpedance_reports (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    body_fat_pct NUMERIC(5,2) NULL,
    skeletal_muscle_mass NUMERIC(5,2) NULL,
    fat_free_mass NUMERIC(5,2) NULL,
    visceral_fat_index NUMERIC(5,2) NULL,
    muscle_quality NUMERIC(5,2) NULL,
    trunk_fat_kg NUMERIC(5,2) NULL,
    trunk_fat_pct NUMERIC(5,2) NULL,
    total_body_water NUMERIC(5,2) NULL,
    user_id INTEGER REFERENCES users(id)
);

CREATE TABLE dexa_reports (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    fat_mass_kg NUMERIC(5,2) NULL,
    lean_mass_kg NUMERIC(5,2) NULL,
    body_fat_pct NUMERIC(5,2) NULL,
    muscle_mass_kg NUMERIC(5,2) NULL,
    bone_mineral_density NUMERIC(5,3) NULL,
    visceral_fat_kg NUMERIC(5,2) NULL,
    user_id INTEGER REFERENCES users(id)
);

CREATE TABLE body_measurements (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    neck_cm NUMERIC(5,2) NULL,
    shoulders_cm NUMERIC(5,2) NULL,
    chest_cm NUMERIC(5,2) NULL,
    bicep_cm NUMERIC(5,2) NULL,
    waist_cm NUMERIC(5,2) NULL,
    hip_cm NUMERIC(5,2) NULL,
    thigh_cm NUMERIC(5,2) NULL,
    user_id INTEGER REFERENCES users(id)
);

CREATE TABLE calories (
    id SERIAL PRIMARY KEY,
    start_date DATE NOT NULL,
    end_date DATE NULL,
    calories INTEGER NOT NULL,
    user_id INTEGER REFERENCES users(id)
);

CREATE TABLE exercise_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    user_id INTEGER NULL REFERENCES users(id)
);

CREATE TABLE gym_logs (
    id SERIAL PRIMARY KEY,
    start_date DATE NOT NULL,
    end_date DATE NULL,
    exercise_type_id INTEGER REFERENCES exercise_types(id),
    weight NUMERIC(5,2) NULL,
    reps INTEGER NULL,
    user_id INTEGER REFERENCES users(id)
);

CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id),
    name VARCHAR(100),
    birth_date DATE,
    sex VARCHAR(10),
    height_cm NUMERIC(5,1),
    allergies TEXT,
    supplements TEXT
);

CREATE TABLE weekly_reports (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    week_start DATE NOT NULL,
    training_days INTEGER,
    avg_daily_steps INTEGER,
    alcohol_drinks NUMERIC(5,1),
    cigarettes_per_day NUMERIC(5,1),
    avg_water_liters NUMERIC(5,2),
    notes TEXT,
    UNIQUE(user_id, week_start)
);

CREATE INDEX idx_weights_user_date ON weights(user_id, date);
CREATE INDEX idx_phases_user_date ON phases(user_id, start_date);
CREATE INDEX idx_bioimpedance_user_date ON bioimpedance_reports(user_id, date);
CREATE INDEX idx_dexa_user_date ON dexa_reports(user_id, date);
CREATE INDEX idx_body_measurements_user_date ON body_measurements(user_id, date);
CREATE INDEX idx_calories_user_date ON calories(user_id, start_date);
CREATE INDEX idx_gym_logs_user ON gym_logs(user_id, start_date);
```

**5. Configure environment variables**
```bash
cp .env.example .env
```
Edit `.env`:
```
DB_HOST=localhost
DB_NAME=weights
DB_USER=your_user
DB_PASSWORD=your_password
DB_PORT=5432
JWT_SECRET=your_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
```

**6. Run the server**
```bash
uvicorn api.main:app --reload
```

API available at `http://localhost:8000`.
Interactive docs at `http://localhost:8000/docs`.

---

## Dependencies

| Package | Purpose |
|---|---|
| `fastapi` | Web framework |
| `uvicorn` | ASGI server |
| `psycopg2-binary` | PostgreSQL driver |
| `python-dotenv` | Environment variables |
| `PyJWT` | JWT token generation and verification |
| `passlib` | Password hashing |
| `bcrypt==4.0.1` | Bcrypt hashing backend |

---

## License

MIT