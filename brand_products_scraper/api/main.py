# File: api/main.py

"""
 This is the main part of the api which controlls all the api routers
"""

from fastapi import FastAPI
from endpoints.hm_scraper_api import router as hm_router
from endpoints.burberry_scraper_api import router as burberry_router
# from endpoints.zara_scraper_api import router as zara_router
from endpoints.kate_spade_api import router as kate_spade_router
from endpoints.uniqlo_scraper_api import router as uniqlo_router
from endpoints.nike_scraper_api import router as nike_router

app = FastAPI(
    title="Brand Products Scraper API",
    description="API for scraping product data from different brands",
)


app.include_router(hm_router,tags=["H&M"]) # HM 
app.include_router(burberry_router,tags=["Burberry"]) # Burberry
# app.include_router(zara_router, tags=["Zara"])  # Zara 
app.include_router(kate_spade_router , tags=["Kate Spade"]) # Kate_Spade
app.include_router(uniqlo_router, tags=["Uniqlo"]) # Uniqlo
app.include_router(nike_router, tags=["Nike"]) # Nike



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 
