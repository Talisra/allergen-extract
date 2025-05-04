from pydantic import BaseModel
from validators import url as validate_url 
from scraper import BSoupRecipeScraper
from ai_client import AzureAIClient
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
from functools import lru_cache

app = FastAPI(title="Allergen Extractor API")

@lru_cache(maxsize=1)
def get_scraper() -> BSoupRecipeScraper:
    return BSoupRecipeScraper()

@lru_cache(maxsize=1)
def get_ai_client() -> AzureAIClient:
    return AzureAIClient()

app.mount("/static", StaticFiles(directory="public", html=True), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return FileResponse("public/index.html")

class UrlRequest(BaseModel):
    url: str
    description: str = "Recipe URL to analyze for allergens"
    example: dict = {
        "url": "https://www.allrecipes.com/recipe/46822/indian-chicken-curry-ii/"
    }

@app.post("/extract-allergens", 
          summary="Extract allergens from recipe URL",
          response_description="Dictionary with allergens and original content")
async def extract_allergens(request: UrlRequest, scraper: BSoupRecipeScraper = Depends(get_scraper), ai_client: AzureAIClient = Depends(get_ai_client)):
    """
    Process a recipe URL and return extracted allergens and content.
    
    - **url**: Valid recipe URL from supported sites
    - Returns: JSON with status, original content, and detected allergens
    """
    try:
        if not validate_url(request.url):
            raise ValueError("Invalid URL format")

        scraper = BSoupRecipeScraper()
        ai_client = AzureAIClient()
        scraped_data = scraper.scrape("https://www.allrecipes.com/recipe/46822/indian-chicken-curry-ii/")

        ai_result = ai_client.extract_allergens(scraped_data['ingredients'])

        return {
            "status": "success",
            "url": request.url,
            "result": {
                "original_content": scraped_data['original_content'],
                "ingredients": scraped_data['ingredients'],
                "allergens": ai_result.allergens
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing URL: {str(e)}"
        )

# To run: uvicorn server:app --reload
