# Weights API

REST API for personal body tracking built with FastAPI and PostgreSQL. Manages daily weight logs, training phases (bulk, cut, maintenance) and nutritionist body composition reports. Includes JWT authentication with multi-user support.

Part of the [Weights](https://github.com/sergio-fernandez-sanchez/Weights-Desktop) project ecosystem.

---

## Demo account

A demo account is available with 2+ years of realistic data pre-loaded:

| Field | Value |
|---|---|
| Email | demo@gmail.com |
| Password | 1234 |

Log in at `POST /auth/login` to get a token and explore all endpoints with real data.

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
| POST | `/weights` | Add or update today's weight |

### Phases
| Method | Route | Description |
|---|---|---|
| GET | `/phases` | Get all training phases |
| GET | `/phases/active` | Get the current active phase |
| POST | `/phases` | Close current phase and start a new one |

### Reports
| Method | Route | Description |
|---|---|---|
| GET | `/reports` | Get all nutritionist reports |
| POST | `/reports` | Add a new nutritionist report |

All endpoints except `/auth/register` and `/auth/login` require a valid JWT token in the `Authorization: Bearer <token>` header.

---

## Project Structure

```
weights-api/
├── services.py         # Business logic
├── report_generator.py # AI report text generation
├── db/
│   ├── database.py     # PostgreSQL connection
│   └── queries.py      # SQL queries
├── api/
│   ├── main.py         # FastAPI app and routes
│   ├── auth.py         # JWT authentication
│   └── schemas.py      # Pydantic input/output models
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

CREATE INDEX idx_weights_user_date ON weights(user_id, date);
CREATE INDEX idx_phases_user_date ON phases(user_id, start_date);
CREATE INDEX idx_reports_user_date ON reports(user_id, date);
```

**5. Configure environment variables**
```bash
cp .env.example .env
```
Edit `.env` with your credentials:
```
DB_HOST=localhost
DB_NAME=weights
DB_USER=your_user
DB_PASSWORD=your_password
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
| `bcrypt` | Bcrypt hashing backend |

---

## License

MIT