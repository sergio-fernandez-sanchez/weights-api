# Weights API

REST API for personal body tracking built with FastAPI and PostgreSQL. Manages daily weight logs, training phases (bulk, cut, maintenance), nutritionist body composition reports, calorie targets, gym performance tracking and AI report generation. Includes JWT authentication with multi-user support.

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
| POST | `/phases` | Close current phase and start a new one (optional start date) |
| PATCH | `/phases/active` | Update weight goal and date goal of the active phase |

### Reports
| Method | Route | Description |
|---|---|---|
| GET | `/reports` | Get all nutritionist reports |
| POST | `/reports` | Add a new nutritionist report (optional date) |

### Calories
| Method | Route | Description |
|---|---|---|
| GET | `/calories` | Get full calorie target history |
| GET | `/calories/active` | Get current calorie target |
| POST | `/calories` | Close current target and set a new one |

### Gym
| Method | Route | Description |
|---|---|---|
| GET | `/gym/exercise-types` | Get all available exercise types (global + user custom) |
| POST | `/gym/exercise-types` | Create a custom exercise type |
| GET | `/gym/logs` | Get full gym log history with exercise names |
| GET | `/gym/logs/active` | Get active gym logs (no end date) with exercise names |
| POST | `/gym/logs` | Add a new gym log entry |
| PATCH | `/gym/logs/{log_id}` | Close current log and insert updated one |
| DELETE | `/gym/logs/{log_id}` | Close a gym log (set end date to today) |

### AI Reports
| Method | Route | Description |
|---|---|---|
| GET | `/generate-report` | Generate optimized report for AI analysis (weekly averages for past phases, all records for active phase, calories, gym with strength % per phase) |
| GET | `/generate-report/raw` | Generate full raw data report (all weight records, calories, gym history, nutritionist measurements) |

All endpoints except `/auth/register` and `/auth/login` require a valid JWT token in the `Authorization: Bearer <token>` header.

---

## Project Structure

```
weights-api/
├── core/
│   ├── services.py          # Business logic
│   └── report_generator.py  # AI report text generation (two report types)
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

CREATE TABLE reports (
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
    neck_cm NUMERIC(5,2) NULL,
    chest_cm NUMERIC(5,2) NULL,
    bicep_cm NUMERIC(5,2) NULL,
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

CREATE INDEX idx_weights_user_date ON weights(user_id, date);
CREATE INDEX idx_phases_user_date ON phases(user_id, start_date);
CREATE INDEX idx_reports_user_date ON reports(user_id, date);
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