# Import necessary modules from FastAPI framework
from fastapi import FastAPI, HTTPException
# Import BaseModel from pydantic for data validation and serialization
from pydantic import BaseModel
# Import types for type hinting
from typing import Dict, List, Optional

# Initialize FastAPI application instance with a title
app = FastAPI(title="Backend API")

# Define root endpoint (/) that returns a welcome message
@app.get("/")
async def root():
    return {"message": "Welcome to the Backend API"}

# Define health check endpoint that can be used to verify API is running
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# This block only executes when the file is run directly (not imported)
if __name__ == "__main__":
    # Import uvicorn server
    import uvicorn
    # Start the uvicorn server with the FastAPI app
    # host="0.0.0.0" makes the server accessible from other devices on the network
    # port=8000 is the default port for web servers
    uvicorn.run(app, host="0.0.0.0", port=8000) 