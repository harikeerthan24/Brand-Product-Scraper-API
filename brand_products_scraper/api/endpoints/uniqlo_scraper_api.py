from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import httpx
import asyncio
from enum import Enum

router = APIRouter()

class UniqloGender(str, Enum):
    """
    Enum for valid Uniqlo gender categories
    """
    MEN = "men"
    WOMEN = "women"

class UniqloConfig(BaseModel):
    """
    Configuration model for Uniqlo API with validation
    """
    base_url: str = "https://www.uniqlo.com/us/api/commerce/v5/en/recommendations/products"
    item_id: str = "E469410-000"
    max_limit: int = 500
    custom_headers: dict = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'x-fr-clientid': 'uq.us.web-spa',
        'referer': 'https://www.uniqlo.com'
    }

async def fetch_products(config: UniqloConfig, gender: str, limit: int) -> Dict[str, Any]:
    """
    Fetches product recommendations from Uniqlo with error handling
    """
    params = {
        "schema": "association_view",
        "genders": gender,
        "itemIds": config.item_id,
        "isAreaAvailable": "false",
        "limit": limit,
        "temperatureSensitive": "false",
        "imageRatio": "3x4",
        "httpFailure": "true"
    }
    
    try:
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                config.base_url,
                params=params,
                headers=config.custom_headers,
                follow_redirects=True
            )
            response.raise_for_status()
            data = response.json()
            items = data.get('result', {}).get('items', [])

            # Process each item and extract the necessary details
            extracted_items = []
            for item in items:
                # Extract name and gender category
                name = item.get('name', '')
                gender_category = item.get('genderCategory', '')

                # Extract image URLs
                image_urls = [img["image"] for img in item.get("images", {}).get("main", {}).values()]

                # Extract video URLs if they exist in the "sub" section
                video_urls = [sub_item["video"] for sub_item in item.get("images", {}).get("sub", []) if "video" in sub_item]

                # Extract base price
                prices = item.get("prices", {})
                base_price = prices.get("base", {}).get("value")

                # Extract sizes
                sizes = [size.get('name', '') for size in item.get('sizes', [])]

                # Extract rating
                rating = item.get('rating', '')

                # Compile extracted data into a dictionary
                extracted_data = {
                    'name': name,
                    'gender_category': gender_category,
                    'image_urls': image_urls,
                    'video_urls': video_urls,
                    'base_price': base_price,
                    'sizes': sizes,
                    'rating': rating
                }

                # Add the extracted data to the list of items
                extracted_items.append(extracted_data)

            # Return the extracted items
            return extracted_items


    except httpx.RequestError as e:
        print(f"An error occurred while fetching products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching data from Uniqlo: {str(e)}"
        )
    except ValueError as e:
        print(f"Error parsing JSON response: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing Uniqlo response: {str(e)}"
        )
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )

@router.get("/scrape/uniqlo", description= "Get product recommendations from Uniqlo for specified gender categories. ", response_model=Dict[str, Any])
async def scrape_uniqlo(
    genders: List[UniqloGender] = Query(..., description="Gender categories to fetch (comma-separated)"),
    page_limit: Optional[int] = Query(500, ge=1, le=500, description="Number of products to return (max 500)")
):
    """
    Get product recommendations from Uniqlo for specified gender categories.
    
    Args:
        genders: List of gender categories to fetch (e.g., men,women,kids)
        page_limit: Number of products to return per gender (default: 1000, max: 1000)
    """
    config = UniqloConfig()
    all_products = {}
    
    try:
        tasks = [fetch_products(config, gender.value, page_limit) for gender in genders]
        results = await asyncio.gather(*tasks)
        
        for gender, result in zip(genders, results):
            all_products[gender.value] = result
        
        return {
            "message": "Data fetched successfully",
            "categories_fetched": [gender.value for gender in genders],
            "products_per_category": page_limit,
            "data": all_products
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching recommendations: {str(e)}"
        )