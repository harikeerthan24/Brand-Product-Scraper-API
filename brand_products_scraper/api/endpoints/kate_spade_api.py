from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, validator
from typing import List, Dict, Any, Optional
import httpx
import asyncio
from enum import Enum

router = APIRouter()

class KateSpadeCategory(str, Enum):
    """
    Enum for valid Kate Spade categories
    """
    NEW = 'new'
    HANDBAGS = 'handbags'
    WALLETS = 'wallets'
    JEWELLERY = 'jewellery'
    WATCHES = 'watches'
    SHOES = 'shoes'
    CLOTHING = 'clothing'
    ACCESSORIES = 'accessories'

class KateSpadeConfig(BaseModel):
    """
    Configuration model for Kate Spade scraper API with improved validation.
    """
    base_url: str = "https://www.katespade.com/api/get-shop"
    base_website_url: str = "https://www.katespade.com"
    max_pages: int = 5  # Fixed to 5 pages maximum
    custom_headers: dict = {
        'x-sid': 'd2f7bd04-f23b-4079-82a6-0301de9d52f3',
        'sec-ch-ua-platform': '"Windows"',
        'Referer': 'https://www.katespade.com/shop/new/view-all?page=5',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="130", "Brave";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform-version': '"15.0.0"',
        'Cookie': 'your_cookie_data_here'
    }

async def fetch_products(config: KateSpadeConfig, category: str, page: int) -> List[Dict[str, Any]]:
    """
    Fetches product data from a specific category and page with error handling and filtering.
    """
    url = f"{config.base_url}/{category}/view-all?__v__=IbxvmORzlo8O3ckg_HYmW&page={page}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=config.custom_headers, follow_redirects=True)
            response.raise_for_status()

            data = response.json()
            page_data = data.get('pageData', {})
            products = page_data.get('products', [])
            
            filtered_products = []
            
            for product in products:
                relative_url = product.get("url", "")
                absolute_url = f"{config.base_website_url}{relative_url}" if relative_url else ""
                
                product_data = {
                    "name": product.get("name", ""),
                    "price": product.get("prices", {}),
                    "url": absolute_url,
                    "color_variants": []
                }
                
                for color in product.get("colors", []):
                    color_relative_url = color.get("url", "")
                    color_absolute_url = f"{config.base_website_url}{color_relative_url}" if color_relative_url else ""
                    
                    color_variant = {
                        "color_name": color.get("text", ""),
                        "variant_url": color_absolute_url,
                        "images": []
                    }
                    
                    media = color.get("media", {})
                    full_media = media.get("full", [])
                    
                    color_variant["images"] = [
                        f"{config.base_website_url}{item.get('src')}" if item.get('src') and not item.get('src').startswith('http') else item.get('src')
                        for item in full_media if item.get('src')
                    ]
                    
                    product_data["color_variants"].append(color_variant)
                
                filtered_products.append(product_data)
            
            return filtered_products
            
    except httpx.RequestError as e:
        print(f"An error occurred while fetching products: {str(e)}")
        return []
    except ValueError as e:
        print(f"Error parsing JSON response: {str(e)}")
        return []
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return []

@router.post("/scrape/katespade")
async def scrape_kate_spade(
    categories: List[KateSpadeCategory] = Query(..., description="Categories to scrape (comma-separated)"),
    pages: Optional[int] = Query(5, ge=1, le=5, description="Number of pages to scrape (max 5)")
):
    """
    Scrapes product data for specified categories up to 5 pages per category.
    
    Args:
        categories: List of categories to scrape (e.g., new,handbags,wallets)
        pages: Number of pages to scrape per category (default: 5, max: 5)
    """
    config = KateSpadeConfig()
    config.max_pages = pages  # Set the page limit from user input
    all_products = []
    
    try:
        for category in categories:
            tasks = [fetch_products(config, category.value, page) for page in range(1, config.max_pages + 1)]
            results = await asyncio.gather(*tasks)
            
            category_products = []
            for page_products in results:
                category_products.extend(page_products)
            
            if not category_products:
                print(f"No products found for category: {category}")
            else:
                all_products.extend(category_products)
        
        return {
            "message": "Scraping completed",
            "categories_scraped": [cat.value for cat in categories],
            "pages_per_category": pages,
            "total_products": len(all_products),
            "products": all_products
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during scraping: {str(e)}"
        )