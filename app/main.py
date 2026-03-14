from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routes import router
from app.config import CORS_ORIGINS


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: pre-embed all schemes for fast RAG queries."""
    print("🚀 Starting Gov AI Agent...")
    try:
        from app.services.rag_service import preload_scheme_embeddings
        preload_scheme_embeddings()
    except Exception as e:
        print(f"⚠️ Could not pre-load embeddings (will use fallback): {e}")
    yield
    print("🛑 Gov AI Agent shutting down.")


app = FastAPI(
    title="Gov AI Agent",
    description="AI-powered Indian government scheme eligibility and application assistant powered by Amazon Nova.",
    version="2.0.0",
    lifespan=lifespan
)

# CORS — configurable via .env
origins = CORS_ORIGINS if CORS_ORIGINS != ["*"] else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def home():
    return {
        "service": "Gov AI Agent",
        "version": "2.0.0",
        "status": "running",
        "powered_by": "Amazon Nova Lite + Titan Embeddings",
        "endpoints": ["/upload", "/apply", "/chat", "/schemes", "/docs"]
    }