from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
import httpx
import json

class Alternative(BaseModel):
    label: str
    url: str
    image: str

class NormalizedProduct(BaseModel):
    id: str
    title: str
    brand: str
    url: str
    price: str
    alternatives: List[Alternative]
    images: List[str]

router = APIRouter()

class BurberryScraperConfig(BaseModel):
    base_url: str = "https://us.burberry.com/web-api/pages/products"
    location: str = "/cat1350556/cat1350564/cat7170024"
    offset: int = 1
    is_new_product_card: str = "true"
    language: str = "en"
    country: str = "US"
    custom_headers: dict = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    }

async def fetch_products(config: BurberryScraperConfig, limit: int) -> List[NormalizedProduct]:
    url = f"{config.base_url}?location={config.location}&offset={config.offset}&limit={limit}&isNewProductCard={config.is_new_product_card}&language={config.language}&country={config.country}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=config.custom_headers)
            response.raise_for_status()
            raw_data = response.json()
            product_list = raw_data.get('data', {}).get('products', [])

            # Initialize an empty list to store normalized products
            normalized_products = []

            for product in product_list:
                items = product.get('items', [])

                for item in items:
                    # Map Burberry-specific fields to the normalized structure
                    normalized_product = NormalizedProduct(
                        id=item.get('id', 'No ID'),
                        title=item.get("content", {}).get("title", "No title"),
                        brand='Burberry',
                        url=f"https://us.burberry.com{item.get('url', '')}",
                        price=item.get("price", {}).get("current", {}).get("formatted", "No price"),
                        alternatives=[
                            Alternative(
                                label=alt.get("label", "No label"),
                                url=f"https://us.burberry.com{alt.get('url', '')}",
                                image=alt.get("image", "No image")
                            ) for alt in item.get("alternatives", {}).get("colors", [])
                        ],
                        images=[]
                    )

                    for img in item.get('medias', []):
                        if "sources" in img:
                            for source in img["sources"]:
                                if "srcSet" in source and isinstance(source["srcSet"], str):
                                    urls = source["srcSet"].split(", ") if source["srcSet"] else []
                                    for url in urls:
                                        if "(min-width:1920px)" in source.get("media", ""):
                                            normalized_product.images.append(url)

                    normalized_products.append(normalized_product)

            return normalized_products

        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Error fetching products: {str(e)}")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error parsing response: {str(e)}")

@router.post("/scrape/burberry", description="Scrape products from Burberry website \n The Burberry consists of the many products it wont have based on the categories, so you can get the products based on the different categories up to 1000 products as a limit")
async def scrape_burberry(
    limit: int = Query(..., ge=1, le=1000, description="Number of products to fetch (max 1000)")
):
    config = BurberryScraperConfig()
    products = await fetch_products(config, limit)

    response_data = {
        "message": f"Successfully scraped {len(products)} products from Burberry",
        "products": [product.dict() for product in products]  # Convert to dict
    }

    return JSONResponse(content=response_data)
