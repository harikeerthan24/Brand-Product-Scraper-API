from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import httpx
import json
import os

router = APIRouter()

class BurberryScraperConfig(BaseModel):
    base_url: str = "https://us.burberry.com/web-api/pages/products"
    location: str = "/cat1350556/cat1350564/cat7170024"
    offset: int = 1  # Changed from 1 to 0 as most APIs start with 0
    is_new_product_card: str = "true"
    language: str = "en"
    country: str = "US"
    custom_headers: dict = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    }

async def fetch_products(config: BurberryScraperConfig, limit: int) -> List[dict]:
    url = f"{config.base_url}?location={config.location}&offset={config.offset}&limit={limit}&isNewProductCard={config.is_new_product_card}&language={config.language}&country={config.country}"
    async with httpx.AsyncClient() as client:  # Added timeout
        try:
            response = await client.get(url, headers=config.custom_headers)
            response.raise_for_status()
            raw_data = response.json()
            # Extract the products list from the raw_data
            product_list = raw_data.get('data', {}).get('products', [])

            # Initialize an empty list to store filtered products
            filtered_products = []

            # Loop through the product_list and get the 'items' part
            for product in product_list:
                items = product.get('items', [])

                # Loop through each item and filter the required data
                for item in items:
                    filtered_data = {
                        "id": item.get('id', 'No ID'),
                        "title": item.get("content", {}).get("title", "No title"),
                        "label": item.get("content", {}).get("label", "No label"),
                        "url": f"https://us.burberry.com{item.get('url', '')}",  # Fixed URL construction
                        "price": item.get("price", {}).get("current", {}).get("formatted", "No price"),
                        "alternatives": [],
                        "images": []
                    }

                    # Extract alternatives
                    alternatives = item.get("alternatives", {}).get("colors", [])
                    for alternative in alternatives:
                        alt_data = {
                            "label": alternative.get("label", "No label"),
                            "url": f"https://us.burberry.com{alternative.get('url', '')}",  # Fixed URL construction
                            "image": alternative.get("image", "No image")
                        }
                        filtered_data["alternatives"].append(alt_data)

                    # Extract images
                    images = item.get('medias', [])
                    for img in images:
                        for source in img.get("sources", []):
                            if source.get("media") == "(min-width:1920px)":
                                src_sets = source.get("srcSet", "").split(", ")
                                if len(src_sets) > 1:
                                    high_quality_image = src_sets[1].split(" ")[0]
                                    if high_quality_image and high_quality_image not in filtered_data['images']:  # Avoid duplicates
                                        filtered_data['images'].append(high_quality_image)

                    # Append the filtered data to the list of filtered products
                    filtered_products.append(filtered_data)

            # Return or process the filtered_products list
            return filtered_products

        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Error fetching products: {str(e)}")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error parsing response: {str(e)}")

@router.post("/scrape/burberry")
async def scrape_burberry(
    limit: int = Query(..., ge=1, le=1000, description="Number of products to fetch (max 1000)")
):
    if limit > 1000:
        raise HTTPException(status_code=400, detail="Limit cannot exceed 1000 products")
    

    config = BurberryScraperConfig()
    products = await fetch_products(config, limit)

    response_data = {
        "message": f"Successfully scraped {len(products)} products from Burberry",
        "products": products
    }
    
    return JSONResponse(content=response_data)

