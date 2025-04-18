from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.routers import users, books, adventure_types
from app.database.init_db import init_db, configure_storage

# Create FastAPI application
app = FastAPI(
    title="Little Hero Backend API",
    description="API for the Little Hero platform",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Mount static files directory
static_dir = os.path.join(os.getcwd(), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include routers
app.include_router(users.router)
app.include_router(books.router)
app.include_router(adventure_types.router)


# Add root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to Little Hero Backend API"}


# Add health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and storage when the application starts."""
    await init_db()
    await configure_storage() 