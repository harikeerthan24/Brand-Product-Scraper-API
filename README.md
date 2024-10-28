# Brand Product Scraper API

An API for scraping product information from various brands, including details, images, and videos.

Supported brands include:

- H&M
- Burberry
- Kate Spade
- Uniqlo


### Project Structure

brand_products_scraper
|
|
└── api
    ├── main.py               # The entry point of the FastAPI application, initializing the app and routing.
    ├── models.py             # Contains data models for API requests and responses using Pydantic.
    ├── __init__.py           # Marks the api directory as a Python package for module imports.
    └── endpoints
        ├── burberry_scraper_api.py  # API endpoints for scraping product info from Burberry.
        ├── hm_scraper_api.py        # API endpoints for scraping product info from H&M.
        ├── kate_spade_api.py        # API endpoints for scraping product info from Kate Spade.
        ├── uniqlo_scraper_api.py    # API endpoints for scraping product info from Uniqlo.
        ├── zara_scraper_api.py      # API endpoints for scraping product info from Zara.
        └── __init__.py              # Marks the endpoints directory as a Python package for imports.


