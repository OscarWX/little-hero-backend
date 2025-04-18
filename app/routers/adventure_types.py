from fastapi import APIRouter
from typing import List, Dict, Any

from app.schemas.book import AdventureType

# Create a router for adventure types
router = APIRouter(prefix="/api/adventure-types", tags=["adventure-types"])


@router.get("", response_model=List[Dict[str, Any]])
async def list_adventure_types():
    """
    List all available adventure types.
    
    Returns:
        List[Dict[str, Any]]: List of adventure types with id, name, description, and image URL
    """
    adventure_types = []
    
    for adventure in AdventureType:
        adventure_data = {
            "id": adventure.value,
            "name": adventure.value.replace("_", " ").title(),
            "description": get_adventure_description(adventure),
            "image_url": f"/static/images/adventures/{adventure.value}.jpg"
        }
        adventure_types.append(adventure_data)
    
    return adventure_types


def get_adventure_description(adventure_type: AdventureType) -> str:
    """
    Get a description for an adventure type.
    
    Args:
        adventure_type: The adventure type
        
    Returns:
        str: Description of the adventure
    """
    descriptions = {
        AdventureType.FANTASY: "Embark on a magical journey through enchanted lands with dragons, wizards, and mystical creatures.",
        AdventureType.SUPERHERO: "Discover your child's inner superhero as they save the day with their amazing powers.",
        AdventureType.SPACE: "Blast off into space for an intergalactic adventure among the stars, planets, and alien worlds.",
        AdventureType.UNDERWATER: "Dive deep beneath the waves to explore coral reefs, sunken ships, and meet fascinating sea creatures.",
        AdventureType.FAIRY_TALE: "Experience classic fairy tale magic with princesses, knights, castles, and enchanted forests.",
        AdventureType.JUNGLE: "Venture into the wild jungle to discover exotic animals, ancient temples, and hidden treasures."
    }
    
    return descriptions.get(adventure_type, "An exciting adventure awaits!") 