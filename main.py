# Import necessary modules from FastAPI framework
from fastapi import FastAPI, HTTPException
# Import BaseModel from pydantic for data validation and serialization
from pydantic import BaseModel
# Import types for type hinting
from typing import Dict, List, Optional

# Initialize FastAPI application instance with a title
app = FastAPI(title="Little Hero Backend API")

# Define a Hero data model for API
class Hero(BaseModel):
    id: Optional[int] = None
    name: str
    power: str
    description: Optional[str] = None

# In-memory database for heroes
heroes_db = [
    Hero(id=1, name="Super Swift", power="Super Speed", description="Can run faster than light"),
    Hero(id=2, name="Mighty Mind", power="Telepathy", description="Can read and control minds"),
    Hero(id=3, name="Flame Fury", power="Fire Control", description="Can create and manipulate fire")
]

# Define root endpoint (/) that returns a welcome message
@app.get("/")
async def root():
    return {"message": "Welcome to Little Hero Backend API"}

# Define health check endpoint that can be used to verify API is running
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Get all heroes endpoint
@app.get("/heroes", response_model=List[Hero])
async def get_heroes():
    return heroes_db

# Get a specific hero by ID
@app.get("/heroes/{hero_id}", response_model=Hero)
async def get_hero(hero_id: int):
    for hero in heroes_db:
        if hero.id == hero_id:
            return hero
    raise HTTPException(status_code=404, detail="Hero not found")

# Add a new hero
@app.post("/heroes", response_model=Hero)
async def create_hero(hero: Hero):
    # Generate a new ID
    max_id = max([h.id for h in heroes_db], default=0)
    hero.id = max_id + 1
    heroes_db.append(hero)
    return hero

# This block only executes when the file is run directly (not imported)
if __name__ == "__main__":
    # Import uvicorn server
    import uvicorn
    # Start the uvicorn server with the FastAPI app
    # host="0.0.0.0" makes the server accessible from other devices on the network
    # port=8000 is the default port for web servers
    uvicorn.run(app, host="0.0.0.0", port=8000) 