# Weights API

REST API for personal body tracking built with FastAPI. Manages daily weight logs, training phases (bulk, cut, maintenance) and nutritionist body composition reports.

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
├── core/               # Business logic
│   ├── csv_utils.py    # Generic CSV read/write
│   ├── weights.py      # Weight logic
│   ├── phases.py       # Phase logic
│   └── reports.py      # Report logic
├── data/               # CSV databases (gitignored)
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

**4. Run the server**
```bash
uvicorn api.main:app --reload
```

The API will be available at `http://localhost:8000`.
Interactive docs at `http://localhost:8000/docs`.

---

## Data

All data is stored locally in CSV files inside `data/`. The folder is gitignored — when cloning the repo you need to create it manually and add your own CSV files.

---

## Dependencies

| Package | Purpose |
|---|---|
| `fastapi` | Web framework |
| `uvicorn` | ASGI server |

---

## License

MIT
