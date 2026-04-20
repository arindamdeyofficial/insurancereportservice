from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.database import Base, engine
from app.models import User, Article, Incident, Sentiment, RivalAd, Website  # noqa
from app.routers import auth, incidents, sentiments, rival_ads, admin, websites, scrape, analytics
from app.services.scheduler import start_scheduler, stop_scheduler
from app.services.kafka_consumer import start_consumer, stop_consumer
from app.services.clickhouse_client import init_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    init_tables()
    start_scheduler()
    start_consumer()
    yield
    stop_consumer()
    stop_scheduler()


app = FastAPI(title="Insurance Report Service", lifespan=lifespan)

# Prometheus metrics at /metrics
Instrumentator().instrument(app).expose(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,       prefix="/api")
app.include_router(incidents.router,  prefix="/api")
app.include_router(sentiments.router, prefix="/api")
app.include_router(rival_ads.router,  prefix="/api")
app.include_router(admin.router,      prefix="/api")
app.include_router(websites.router,   prefix="/api")
app.include_router(scrape.router,     prefix="/api")
app.include_router(analytics.router,  prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
