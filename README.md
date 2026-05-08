# Weights API

REST API for personal body tracking built with FastAPI and PostgreSQL. Manages daily weight logs, training phases (bulk, cut, maintenance) and nutritionist body composition reports.

Part of the [Weights](https://github.com/sergio-fernandez-sanchez/Weights-Desktop) project ecosystem.

---

## Endpoints

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

---

## Project Structure

```
weights-api/
├── services.py         # Business logic
├── report_generator.py # AI report text generation
├── migrate.py          # One-time CSV to PostgreSQL migration script
├── db/
│   ├── database.py     # PostgreSQL connection
│   └── queries.py      # SQL queries
├── api/
│   ├── main.py         # FastAPI app and routes
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

**4. Create a PostgreSQL database**
```bash
psql postgres
CREATE DATABASE weights;
\q
```

**5. Create the tables**
```bash
psql weights
```
```sql
CREATE TABLE weights (
    id SERIAL PRIMARY KEY,
    date DATE,
    weight NUMERIC(5,2)
);

CREATE TABLE phases (
    id SERIAL PRIMARY KEY,
    start_date DATE NOT NULL,
    end_date DATE NULL,
    phase_type VARCHAR(50) NOT NULL,
    weight_goal NUMERIC(5,2) NULL,
    date_goal DATE NULL
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
    thigh_cm NUMERIC(5,2) NULL
);
```

**6. Configure environment variables**
```bash
cp .env.example .env
```
Edit `.env` with your database credentials:
```
DB_HOST=localhost
DB_NAME=weights
DB_USER=your_user
DB_PASSWORD=your_password
```

**7. (Optional) Migrate existing CSV data**
```bash
python3 migrate.py
```

**8. Run the server**
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

---

## License

MIT