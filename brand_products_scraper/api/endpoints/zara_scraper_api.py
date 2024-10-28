# File: api/zara_scraper_api.py

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import httpx
import json
import os

router = APIRouter()

class ZaraScraperConfig(BaseModel):
    base_url: str = "https://www.zara.com/us/en/products-details"
    custom_headers: dict = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

async def fetch_zara_product(config: ZaraScraperConfig, product_id: int):
    url = f"{config.base_url}?productIds={product_id}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=config.custom_headers)
        response.raise_for_status()
        return response.json()

@router.post("/scrape/zara")
async def scrape_zara(
    product_id: int = Query(..., description="Zara product ID to scrape"),
):
    config = ZaraScraperConfig()
    
    try:
        product_data = await fetch_zara_product(config, product_id)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Failed to fetch product data: {str(e)}")
    
    
    # Prepare the response
    response_data = {
        "message": f"Scraped product data for Zara product ID: {product_id}",
        "product_data": product_data
    }
    
    
    return JSONResponse(content=response_data)

