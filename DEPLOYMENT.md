# Deployment Information

## Public URL

https://oidoioi.onrender.com

## Platform

**Render** (Free tier, region: Oregon US West)

- Auto-deploy khi push lên `main` branch
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## CI/CD Pipeline

**GitHub Actions** — chạy tự động khi push lên `main`:

1. **Lint** — `flake8` kiểm tra syntax errors và undefined names
2. **Test** — `pytest` chạy 12 unit tests
3. **Auto-deploy** — Render tự deploy sau khi CI pass

Xem workflow: https://github.com/ntphuc149/oidoioi/actions

---

## Test Commands

### Health Check
```bash
curl https://oidoioi.onrender.com/health
```
Expected:
```json
{
  "status": "ok",
  "version": "1.0.0",
  "environment": "production",
  "uptime_seconds": 42.1,
  "total_requests": 5,
  "timestamp": "2026-06-12T10:00:00+00:00"
}
```

### Readiness Check
```bash
curl https://oidoioi.onrender.com/ready
```
Expected:
```json
{"ready": true}
```

### Authentication Required (no key → 401)
```bash
curl -X POST "https://oidoioi.onrender.com/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "hello"}'
```
Expected:
```json
{"detail": "Invalid or missing API key. Include header: X-API-Key: <your-key>"}
```

### Ask with API Key
```bash
curl -X POST "https://oidoioi.onrender.com/ask" \
  -H "X-API-Key: my-secret-key-2024" \
  -H "Content-Type: application/json" \
  -d '{"question": "what is machine learning?"}'
```
Expected:
```json
{
  "question": "what is machine learning?",
  "answer": "Machine Learning là một nhánh của AI...",
  "model": "mock-llm",
  "timestamp": "2026-06-12T10:00:00+00:00"
}
```

### Ask about Deep Learning
```bash
curl -X POST "https://oidoioi.onrender.com/ask" \
  -H "X-API-Key: my-secret-key-2024" \
  -H "Content-Type: application/json" \
  -d '{"question": "explain deep learning"}'
```

### Ask about Transformer
```bash
curl -X POST "https://oidoioi.onrender.com/ask" \
  -H "X-API-Key: my-secret-key-2024" \
  -H "Content-Type: application/json" \
  -d '{"question": "what is transformer?"}'
```

### Metrics (protected)
```bash
curl "https://oidoioi.onrender.com/metrics" \
  -H "X-API-Key: my-secret-key-2024"
```
Expected:
```json
{
  "uptime_seconds": 120.5,
  "total_requests": 10,
  "error_count": 0,
  "daily_cost_usd": 0.000024,
  "daily_budget_usd": 10.0
}
```

---

## Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `ENVIRONMENT` | `production` | Runtime environment |
| `APP_NAME` | `AI/ML Q&A Agent` | App display name |
| `APP_VERSION` | `1.0.0` | App version |
| `AGENT_API_KEY` | *(set in dashboard)* | API key for authentication |
| `RATE_LIMIT_PER_MINUTE` | `10` | Max requests per minute per user |
| `DAILY_BUDGET_USD` | `10.0` | Daily spending limit in USD |
| `LLM_MODEL` | `mock-llm` | LLM model name (mock for now) |

> `AGENT_API_KEY` được set trực tiếp trên Render Dashboard — không commit vào code.

---

## Local Development

```bash
# Clone repo
git clone https://github.com/ntphuc149/oidoioi.git
cd oidoioi

# Setup environment
cp .env.example .env
# Sửa AGENT_API_KEY trong .env

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Run tests
pytest tests/ -v
```

## Docker

```bash
# Build image
docker build -t aiml-qa-agent .

# Run with docker-compose (agent + Redis)
docker compose up

# Test
curl http://localhost:8000/health
```

---

## Repository Structure

```
oidoioi/
├── app/
│   ├── main.py          # FastAPI app — auth, rate limit, cost guard
│   └── config.py        # 12-Factor config từ environment variables
├── utils/
│   └── mock_llm.py      # Mock LLM với AI/ML topic responses
├── tests/
│   └── test_main.py     # 12 unit tests
├── .github/
│   └── workflows/
│       └── ci.yml       # GitHub Actions — lint + test
├── Dockerfile            # Multi-stage build (~180MB)
├── docker-compose.yml    # Agent + Redis stack
├── render.yaml           # Render deployment config
├── requirements.txt
├── .env.example
└── .dockerignore
```
