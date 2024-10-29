#File: hm_scraper_api.py

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel # data validation 
from fastapi.responses import JSONResponse
from typing import List, Optional 
import httpx # async HTTP client 
import asyncio # managing async code 


router = APIRouter()

# configuration model 
class HMScraperConfig(BaseModel):
    
    base_url: str = "https://api.hm.com/search-services/v1/en_US/listing/resultpage"
    page_size: int = 20 # no of products we need 
    max_pages: int = 1  # total no pages 
    category_page_ids: List[str] = [
        "/men/shop-by-product/tshirts-tank-tops",
        "/men/shop-by-product/shirts",
        "/men/shop-by-product/jeans",
        "/men/shop-by-product/hoodies-sweatshirts",
        "/men/shop-by-product/accessories",
        "/men/shop-by-product/shorts",
        "/men/shop-by-product/pants",
]

    custom_headers: dict = {
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "origin": "https://www2.hm.com",
        "pragma": "no-cache",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "x-customer-key": "51afcce2-2d8a-42fa-8498-916ded45651f",
        "x-session-key": "51afcce2-2d8a-42fa-8498-916ded45651f"
    }

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------


MAIN_CATEGORIES = ["men", "women"]
PRODUCT_TYPES = ["tshirts-tank-tops", "shirts", "jeans", "hoodies-sweatshirts", "accessories", "shorts", "pants" ]

# fetching the products 

# config: HMScraperConfig, category: str, page: int
# type annotations--> [ Python itself will not raise an error by default] 
# its not keyword argue -> its when we call the function 
async def fetch_products(config: HMScraperConfig, category: str, page: int):
    url = f"{config.base_url}?page={page}&pageId={category}&page-size={config.page_size}&categoryId=&filters=&touchPoint=DESKTOP&skipStockCheck=false"
    
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=config.custom_headers)
        response.raise_for_status()
        raw_data = response.json() # getting the data 

        # Ensure the data structure is as expected
        product_list = raw_data.get('plpList', {}).get('productList', [])
        
        filtered_products = []
        for product in product_list:
            filtered_data = {
                "id": product.get("id"),
                "product_name": product.get("productName"),
                "brand": product.get("brandName"),
                "product_url": config.base_url + product.get("url"),
                "price": {
                    "current_price": product["prices"][0].get("price"),
                    "formatted_price": product["prices"][0].get("formattedPrice").strip()
                },
                "availability": product["availability"].get("stockState"),
                "colors": [
                    {
                        "color_name": swatch.get("colorName"),
                        "color_code": swatch.get("colorCode"),
                        "product_image": swatch.get("productImage")
                    } for swatch in product.get("swatches", [])
                ],
                "product_markers": [marker.get("text") for marker in product.get("productMarkers", [])],
                "images": [img.get("url") for img in product.get("images", [])],
                "model_image": product.get("modelImage")
            }
            filtered_products.append(filtered_data)
        
        return filtered_products

@router.post("/scrape/hm")
async def scrape_hm(
    main_categories: List[str] = Query(["men"], description="Main categories to scrape [ men, women ] \n You can select the both two . \n Empty is not allowed need to select atleast one "),
    product_types: List[str] = Query(["shorts"], description="Product types to scrape [tshirts-tank-tops, shirts, jeans, hoodies-sweatshirts, accessories, shorts, pants ] \n You can select the multiple types . \n Empty is not allowed need to select atleast one"),
    page_size: int = Query(20, description="Number of products per page (max 72)"),
    max_pages: Optional[int] = Query(None),
    limit: int = Query(100, description="Number of products to return in the response (max 1000)")
):
    
    """
    Scrape product data from the H&M website.

    This endpoint scrapes products for the specified main categories and product types, fetching
    a configurable number of pages and products per page.

    Args:
        main_categories (List[str]): Main categories to scrape (e.g., 'men', 'women').
        product_types (List[str]): Specific product types to scrape.
        page_size (int): Number of products per page.
        max_pages (Optional[int]): Maximum number of pages to scrape.

    Returns:
        JSONResponse: Contains a message, a list of scraped products, and optional file paths to saved JSON files.
    """

     # Ensure at least one main category and one product type are selected
    if not main_categories:
        raise HTTPException(status_code=400, detail="At least one main category must be selected.")
    if not product_types:
        raise HTTPException(status_code=400, detail="At least one product type must be selected.")

    if page_size > 72:
        raise HTTPException(status_code=400, detail="Product limit is 72 per page")
    
    if not set(main_categories).issubset(set(MAIN_CATEGORIES)):
        raise HTTPException(status_code=400, detail=f"Invalid main categories. Allowed values are: {', '.join(MAIN_CATEGORIES)}")
    
    if not set(product_types).issubset(set(PRODUCT_TYPES)):
        raise HTTPException(status_code=400, detail=f"Invalid product types. Allowed values are: {', '.join(PRODUCT_TYPES)}")
    
    # configuration 
    config = HMScraperConfig(page_size=page_size)
    
    if max_pages:
        config.max_pages = max_pages

    if limit > 1000:
        limit = 1000 # Cap the limit at 1000 to prevent overloading
    
    all_products = []
    
    for main_category in main_categories:
        for product_type in product_types:
            category = f"/{main_category}/product/{product_type}"
            category_products = []
            tasks = [fetch_products(config, category, page) for page in range(1, config.max_pages + 1)]

            results = await asyncio.gather(*tasks)
            for products in results:
                category_products.extend(products)

            if not category_products:
                print(f"No products found for category: {category}")
                continue

            all_products.extend(category_products)
        

     # Prepare the response
    response_data = {
        "message": f"Scraped {len(all_products)} products for H&M",
        "products": all_products[:limit],
        "scraping_config": {
            "main_categories": main_categories,
            "product_types": product_types,
            "page_size": config.page_size,
            "max_pages": config.max_pages,
        }
    }
    
    if not all_products:
        response_data["message"] = "No products found for the specified categories and product types."
    
    return JSONResponse(content=response_data)
    



  