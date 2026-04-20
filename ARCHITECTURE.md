# insurancereportservice — Architecture

## Purpose

FastAPI backend. Handles auth, RBAC, scheduled news scraping, job queue processing, MCP client calls, and REST API for the UI.

## Directory Structure

```
insurancereportservice/
├── app/
│   ├── main.py              # FastAPI app factory
│   ├── config.py            # Settings (pydantic-settings)
│   ├── database.py          # SQLAlchemy engine + session
│   ├── models/              # ORM models
│   │   ├── user.py
│   │   ├── article.py
│   │   ├── incident.py
│   │   ├── sentiment.py
│   │   └── rival_ad.py
│   ├── schemas/             # Pydantic request/response schemas
│   │   ├── auth.py
│   │   ├── article.py
│   │   ├── incident.py
│   │   ├── sentiment.py
│   │   └── rival_ad.py
│   ├── routers/             # FastAPI routers
│   │   ├── auth.py
│   │   ├── articles.py
│   │   ├── incidents.py
│   │   ├── sentiments.py
│   │   ├── rival_ads.py
│   │   └── admin.py
│   ├── services/
│   │   ├── scraper.py       # RSS + HTTP scraper per source
│   │   ├── scheduler.py     # APScheduler cron jobs
│   │   ├── mcp_client.py    # HTTP client calling MCP server
│   │   └── worker.py        # RQ worker job handler
│   └── middleware/
│       └── auth.py          # JWT decode + RBAC dependency
├── alembic/
│   ├── env.py
│   └── versions/
├── alembic.ini
├── requirements.txt
├── Dockerfile
└── ARCHITECTURE.md
```

## Auth Flow

```
POST /auth/login  (email + password)
  → bcrypt verify
  → return access_token (JWT 15min) + set refresh_token cookie (7d)

POST /auth/refresh
  → read httpOnly refresh_token cookie
  → return new access_token

All protected routes: Authorization: Bearer <access_token>
  → JWTBearer dependency decodes token, injects user + role
```

## Scheduler

APScheduler runs inside the FastAPI process on startup. Each news source has a dedicated cron job (every 30 minutes). On trigger: fetch → parse → enqueue to Redis (rq).

## Worker

RQ workers process jobs: call MCP tools → write results to PostgreSQL.
