# Day 12 Lab — Mission Answers

**Student:** Nguyễn Thanh Phúc  
**Date:** 2026-06-12  
**Repo:** https://github.com/ntphuc149/oidoioi

---

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found in `develop/app.py`

1. **API key hardcode trong code** — `OPENAI_API_KEY = "sk-hardcoded-fake-key-never-do-this"` và `DATABASE_URL` chứa password. Nếu push lên GitHub thì key bị lộ ngay lập tức.

2. **Không có health check endpoint** — Platform (Railway, Render, K8s) không có cách nào biết agent còn sống hay đã crash để tự động restart.

3. **Dùng `print()` thay vì proper logging** — Đặc biệt nghiêm trọng khi in ra cả secret: `print(f"[DEBUG] Using key: {OPENAI_API_KEY}")`. Không có log level, không có structured format, không thể search/filter.

4. **`host="localhost"` cố định** — Container không thể nhận traffic từ bên ngoài vì chỉ bind localhost. Phải dùng `host="0.0.0.0"`.

5. **Port cứng `port=8000`** — Cloud platforms inject PORT qua environment variable. Nếu cứng port sẽ không chạy được trên Render/Railway.

6. **`reload=True` trong production** — Debug reload mode tiêu tốn tài nguyên và không an toàn trong môi trường production.

### Exercise 1.2: Chạy basic version

```bash
cd 01-localhost-vs-production/develop
python app.py
curl -X POST "http://localhost:8000/ask?question=hello"
# Response: {"answer": "Tôi là AI agent..."}
```

App chạy được nhưng **không production-ready** — lộ secrets trong log, không có health check, sẽ fail khi deploy lên cloud.

### Exercise 1.3: Comparison table

| Feature | Basic (develop) | Advanced (production) | Tại sao quan trọng? |
|---------|-----------------|----------------------|---------------------|
| **Config** | Hardcode trong code (`OPENAI_API_KEY = "sk-..."`) | Đọc từ env vars (`os.getenv("OPENAI_API_KEY")`) | Tách config khỏi code — deploy nhiều môi trường khác nhau, không lộ secrets trên GitHub |
| **Health check** | Không có | `GET /health` trả về status, uptime, version | Platform biết khi nào container bị crash để restart tự động. Không có health check = downtime không được phát hiện |
| **Logging** | `print(f"[DEBUG] ...")` in cả secret ra stdout | Structured JSON logging với log level | JSON logs dễ parse, search, alert. Không in secrets. Có thể filter theo level (INFO/ERROR) |
| **Shutdown** | Đột ngột khi nhận Ctrl+C | Handle SIGTERM, chờ requests đang xử lý hoàn thành | Graceful shutdown tránh drop requests giữa chừng — quan trọng khi platform restart container |
| **Host binding** | `host="localhost"` | `host="0.0.0.0"` | `localhost` chỉ nhận traffic trong container. `0.0.0.0` nhận từ mọi nơi — bắt buộc trong Docker |
| **Port** | `port=8000` cố định | `int(os.getenv("PORT", 8000))` | Cloud platforms inject PORT qua env var. Cứng port sẽ fail trên Render/Railway |
| **Debug mode** | `reload=True` luôn bật | `reload=settings.debug` (false trong production) | Debug mode chậm hơn, không an toàn, tiêu tốn tài nguyên |

---

## Part 2: Docker Containerization

### Exercise 2.1: Dockerfile questions

1. **Base image là gì?**  
   `python:3.11` — full Python distribution (~1GB). Bao gồm toàn bộ Python runtime, pip, và build tools.

2. **Working directory là gì?**  
   `/app` — thư mục làm việc bên trong container. Tất cả lệnh COPY, RUN, CMD đều chạy từ đây.

3. **Tại sao COPY requirements.txt trước khi COPY code?**  
   Docker build theo từng layer và cache lại. Nếu `requirements.txt` không thay đổi, Docker dùng cached layer — không cần `pip install` lại. Chỉ khi requirements thay đổi mới rebuild. Giúp build nhanh hơn nhiều.

4. **CMD vs ENTRYPOINT khác nhau thế nào?**  
   - `CMD`: lệnh mặc định, **có thể bị override** khi chạy `docker run <image> <command-khac>`
   - `ENTRYPOINT`: lệnh cố định, **không bị override** — chỉ append thêm arguments
   - Dùng `ENTRYPOINT` khi muốn container luôn chạy một binary cụ thể. Dùng `CMD` khi muốn có default nhưng cho phép override.

### Exercise 2.2: Build và run

```bash
# Build từ project root
docker build -f 02-docker/develop/Dockerfile -t my-agent:develop .

# Run container
docker run -p 8000:8000 my-agent:develop

# Test
curl -X POST "http://localhost:8000/ask?question=What is Docker?"
# Response: {"answer": "Container là cách đóng gói app..."}
```

**Image size:** ~1.1 GB (dùng `python:3.11` full image)

### Exercise 2.3: Multi-stage build

**Stage 1 (builder):** Dùng `python:3.11-slim`, cài tất cả dependencies vào `--user` directory. Có đầy đủ build tools (gcc, etc.) để compile các package có C extensions.

**Stage 2 (runtime):** Dùng `python:3.11-slim`, chỉ copy thư mục `.local` (packages đã install) từ builder sang. Không có build tools, không có pip cache → image nhỏ hơn nhiều.

**Tại sao image nhỏ hơn?**
- Không có build tools (gcc, make, etc.) trong final image
- Không có pip cache
- Không có source code của packages
- Chỉ giữ lại những gì cần để chạy

**So sánh kích thước:**
```
my-agent:develop    ~1.1 GB   (python:3.11 full)
my-agent:production ~180 MB   (python:3.11-slim + multi-stage)
```
Giảm ~84% dung lượng — kéo image nhanh hơn, bảo mật hơn (ít attack surface).

### Exercise 2.4: Docker Compose stack

**Architecture diagram:**

```
Client (browser/curl)
        │
        ▼
  Nginx :80 (Load Balancer)
        │
   ┌────┴────┐
   ▼         ▼
Agent:8000  Agent:8000  (có thể scale)
        │
        ▼
   Redis:6379 (shared state)
```

**Services được start:**
- `agent` — FastAPI app (có thể scale `--scale agent=3`)
- `redis` — In-memory store cho session, rate limiting
- `nginx` — Reverse proxy và load balancer, expose port 80

**Cách communicate:** Các services dùng Docker internal network, gọi nhau qua service name (e.g., `redis://redis:6379`). Chỉ Nginx expose port ra ngoài.

---

## Part 3: Cloud Deployment

### Exercise 3.1: Deploy Railway

Không thực hiện Railway vì không có `npm`/Node.js. Đã deploy lên **Render** thay thế (Exercise 3.2).

### Exercise 3.2: Deploy Render

**Steps thực hiện:**
1. Push code lên GitHub repo `ntphuc149/oidoioi`
2. Vào Render Dashboard → New → Web Service
3. Connect repo `oidoioi`
4. Set Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Set Environment Variable: `AGENT_API_KEY=my-secret-key-2024`
6. Deploy thành công!

**Public URL:** https://oidoioi.onrender.com

**Test kết quả:**
```bash
# Health check
curl https://oidoioi.onrender.com/health
# {"status":"ok","version":"1.0.0","environment":"development",...}

# Không có key → 401
curl -X POST "https://oidoioi.onrender.com/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"hello"}'
# {"detail":"Invalid or missing API key..."}

# Có key → 200
curl -X POST "https://oidoioi.onrender.com/ask" \
  -H "X-API-Key: my-secret-key-2024" \
  -H "Content-Type: application/json" \
  -d '{"question":"what is machine learning?"}'
# {"question":"...","answer":"Machine Learning là...","model":"mock-llm",...}
```

**So sánh `render.yaml` vs `railway.toml`:**

| | render.yaml | railway.toml |
|--|--|--|
| Format | YAML | TOML |
| Scope | Khai báo toàn bộ infrastructure (services, env vars, Redis add-on) | Chỉ config build/deploy |
| Redis | Khai báo Redis service trong cùng file | Config riêng qua dashboard |
| Auto-deploy | `autoDeploy: true` | Tự động theo mặc định |
| Region | Chọn được (`singapore`) | Tự động |

### Exercise 3.3: GCP Cloud Run CI/CD (Optional)

Đọc `cloudbuild.yaml` — pipeline gồm 4 bước tuần tự:
1. **Test** — chạy `pytest tests/`
2. **Build** — `docker build` với layer cache từ registry
3. **Push** — push image lên Google Container Registry với tag `$COMMIT_SHA`
4. **Deploy** — `gcloud run deploy` với image mới, zero-downtime

Điểm nổi bật: dùng `$COMMIT_SHA` để tag image → dễ rollback về bất kỳ commit nào. Secrets lấy từ **Secret Manager** thay vì env var thông thường → an toàn hơn.

---

## Part 4: API Security

### Exercise 4.1: API Key Authentication

**API key được check ở đâu?**  
Trong `verify_api_key()` function dùng FastAPI `Security` dependency. Header `X-API-Key` được extract và so sánh với `AGENT_API_KEY` từ environment.

```python
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    if not api_key or api_key != API_KEY:
        raise HTTPException(status_code=401, detail="...")
    return api_key
```

**Điều gì xảy ra nếu sai key?**  
- Không có key → HTTP 401 "Missing API key"
- Sai key → HTTP 403 "Invalid API key"

**Làm sao rotate key?**  
Chỉ cần thay giá trị `AGENT_API_KEY` trong environment variable và restart service. Code không cần thay đổi vì key đọc từ env var.

**Test kết quả:**
```bash
# Không có key → 401
curl http://localhost:8000/ask -X POST -d '{"question":"hello"}'
# {"detail":"Missing API key..."}

# Có key đúng → 200
curl http://localhost:8000/ask -X POST \
  -H "X-API-Key: my-secret-key" \
  -d '{"question":"hello"}'
# {"question":"hello","answer":"..."}
```

### Exercise 4.2: JWT Authentication

**JWT Flow:**
1. Client gửi `POST /auth/token` với username/password
2. Server verify credentials → tạo JWT token (signed, expires 60 phút)
3. Client lưu token, gửi kèm mọi request: `Authorization: Bearer <token>`
4. Server verify signature và expiry của token

**Test kết quả:**
```bash
# Lấy token
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username":"student","password":"demo123"}'
# {"access_token":"eyJhbG...","expires_in_minutes":60}

# Dùng token
curl -X POST "http://localhost:8000/ask" \
  -H "Authorization: Bearer eyJhbG..." \
  -d '{"question":"hello"}'
# {"answer":"...","usage":{"requests_remaining":9}}
```

### Exercise 4.3: Rate Limiting

**Algorithm được dùng:** Sliding Window — giữ deque các timestamp requests trong 60 giây gần nhất. Khi request mới đến, xóa các entry cũ > 60s, đếm số entry còn lại.

**Limit:** 10 requests/minute per user (configurable qua `RATE_LIMIT_PER_MINUTE`)

**Admin bypass:** Role-based — admin dùng `rate_limiter_admin` với limit cao hơn (100 req/min).

**Kết quả khi hit limit:**
```bash
# Request thứ 11 trở đi → 429
{"detail":"Rate limit exceeded: 10 req/min. Retry after 60s."}
# Headers: Retry-After: 60
```

### Exercise 4.4: Cost Guard Implementation

```python
def check_budget(user_id: str, estimated_cost: float) -> bool:
    """
    Mỗi user có budget $10/tháng.
    Track spending trong Redis, reset đầu tháng.
    """
    month_key = datetime.now().strftime("%Y-%m")
    key = f"budget:{user_id}:{month_key}"

    current = float(r.get(key) or 0)
    if current + estimated_cost > 10:
        return False  # Vượt budget

    r.incrbyfloat(key, estimated_cost)
    r.expire(key, 32 * 24 * 3600)  # TTL 32 ngày
    return True
```

**Logic:** Dùng Redis key `budget:{user_id}:{YYYY-MM}` để track theo tháng. Tự động expire sau 32 ngày. Ước tính cost dựa trên số tokens (input + output).

---

## Part 5: Scaling & Reliability

### Exercise 5.1: Health Checks

**Implementation:**

```python
@app.get("/health")
def health():
    """Liveness probe — container còn sống không?"""
    return {
        "status": "ok",
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "version": "1.0.0",
    }

@app.get("/ready")
def ready():
    """Readiness probe — sẵn sàng nhận traffic chưa?"""
    if not _is_ready:
        raise HTTPException(503, "Not ready")
    return {"ready": True}
```

**Sự khác biệt:**
- `/health` (liveness): Process còn sống không? → Platform restart nếu fail
- `/ready` (readiness): Đã load xong, sẵn sàng nhận request chưa? → Load balancer không route traffic nếu fail

**Test kết quả:**
```bash
curl http://localhost:8000/health
# {"status":"ok","uptime_seconds":88.5,"version":"1.0.0",...}

curl http://localhost:8000/ready
# {"ready":true,"in_flight_requests":1}
```

### Exercise 5.2: Graceful Shutdown

```python
def handle_sigterm(signum, frame):
    logger.info("Received SIGTERM — starting graceful shutdown")
    # uvicorn bắt SIGTERM và gọi lifespan shutdown tự động

signal.signal(signal.SIGTERM, handle_sigterm)
```

**Trong lifespan shutdown:**
```python
# Đánh dấu không ready (load balancer stop routing)
_is_ready = False
# Chờ in-flight requests hoàn thành (max 30s)
while _in_flight_requests > 0 and elapsed < 30:
    time.sleep(1)
```

**Tại sao quan trọng:** Khi platform muốn restart container (deploy mới, scale down), nó gửi SIGTERM trước. Graceful shutdown cho phép hoàn thành các request đang xử lý thay vì drop đột ngột.

### Exercise 5.3: Stateless Design

**Vấn đề với stateful (in-memory):**
```
User gửi request 1 → Instance A (lưu history trong memory)
User gửi request 2 → Instance B (KHÔNG có history → mất context!)
```

**Giải pháp — lưu state trong Redis:**
```python
def save_session(session_id: str, data: dict):
    _redis.setex(f"session:{session_id}", 3600, json.dumps(data))

def load_session(session_id: str) -> dict:
    data = _redis.get(f"session:{session_id}")
    return json.loads(data) if data else {}
```

**Test multi-turn conversation:**
```bash
# Turn 1 — tạo session
curl -X POST "http://localhost:8000/chat" \
  -d '{"question":"hello"}'
# {"session_id":"eb5a3975-...","turn":1,"served_by":"instance-e4f2ee"}

# Turn 2 — cùng session, có thể served by instance khác
curl -X POST "http://localhost:8000/chat" \
  -d '{"question":"what is docker?","session_id":"eb5a3975-..."}'
# {"session_id":"eb5a3975-...","turn":2,"served_by":"instance-e4f2ee"}
```

History vẫn liên tục dù bất kỳ instance nào serve request.

### Exercise 5.4: Load Balancing

```bash
docker compose up --scale agent=3
```

**Quan sát:**
- 3 agent instances start, mỗi cái có `INSTANCE_ID` khác nhau
- Nginx nhận traffic port 80, phân tán round-robin đến 3 instances
- `served_by` trong response thay đổi giữa các requests
- Nếu kill 1 instance, Nginx tự route sang 2 instances còn lại

### Exercise 5.5: Test Stateless

```bash
python test_stateless.py
```

Kết quả: Conversation history vẫn còn sau khi một instance bị kill, vì state lưu trong Redis chứ không phải memory của instance.

---

## Part 6: Final Project

**Repo:** https://github.com/ntphuc149/oidoioi  
**Public URL:** https://oidoioi.onrender.com  
**Topic:** AI/ML Q&A Agent

### Checklist hoàn thành

**Functional:**
- [x] REST API `POST /ask` trả lời câu hỏi về AI/ML
- [x] Input validation với Pydantic
- [x] Error handling trả về HTTP status codes chuẩn

**Non-functional:**
- [x] Multi-stage Dockerfile (`python:3.11-slim`, ~180MB)
- [x] Config từ environment variables (`.env` + `python-dotenv`)
- [x] API Key authentication (`X-API-Key` header)
- [x] Rate limiting (10 req/min, sliding window)
- [x] Cost guard ($10/day budget)
- [x] Health check `GET /health`
- [x] Readiness check `GET /ready`
- [x] Graceful shutdown (SIGTERM handler)
- [x] Structured JSON logging
- [x] No hardcoded secrets
- [x] `docker-compose.yml` với agent + Redis
- [x] Deploy lên Render với public URL
- [x] CI/CD với GitHub Actions (lint + 12 unit tests)
- [x] Auto-deploy khi push lên `main`

### Architecture

```
GitHub push
    │
    ▼
GitHub Actions CI
├── flake8 lint
└── pytest (12 tests)
    │
    ▼ (auto-deploy on pass)
Render.com
    │
    ▼
FastAPI App (uvicorn)
├── POST /ask  ← X-API-Key required
├── GET /health
├── GET /ready
└── GET /metrics
```

### Test commands

```bash
# Health
curl https://oidoioi.onrender.com/health

# Auth required
curl -X POST "https://oidoioi.onrender.com/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"hello"}'
# → 401

# With key
curl -X POST "https://oidoioi.onrender.com/ask" \
  -H "X-API-Key: my-secret-key-2024" \
  -H "Content-Type: application/json" \
  -d '{"question":"what is machine learning?"}'
# → {"answer":"Machine Learning là..."}
```
