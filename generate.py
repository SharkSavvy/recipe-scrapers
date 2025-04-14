# generate.py generates a new recipe scraper.
import json
import os
import logging
from recipe_scrapers import scrape_me
from apify_client import ApifyClient
from tenacity import retry, stop_after_attempt, wait_exponential

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Validate environment variables
required_env_vars = [
    'APIFY_TOKEN',
    'APIFY_ACTOR_ID',
    'APIFY_DEFAULT_KEY_VALUE_STORE_ID'
]

def validate_env_vars():
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def test_apify_connection(client):
    """Test Apify connectivity with retry logic"""
    await client.actor(os.environ['APIFY_ACTOR_ID']).get()
    return True

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def fetch_recipe_data(url):
    """Fetch recipe data with retry logic"""
    scraper = scrape_me(url)
    return {
        "title": scraper.title(),
        "ingredients": scraper.ingredients(),
        "instructions": scraper.instructions(),
        "total_time": scraper.total_time(),
        "yields": scraper.yields(),
        "image": scraper.image(),
        "host": scraper.host(),
        "author": scraper.author(),
        "description": scraper.description(),
        "nutrients": scraper.nutrients() if hasattr(scraper, "nutrients") else None,
        "url": url
    }

async def main():
    try:
        validate_env_vars()
        logger.debug("Environment variables validated successfully")
        
        # Log Apify configuration
        logger.debug(f"Using Actor ID: {os.environ['APIFY_ACTOR_ID']}")
        logger.debug(f"Using KV Store ID: {os.environ['APIFY_DEFAULT_KEY_VALUE_STORE_ID']}")
        
        client = ApifyClient(os.environ['APIFY_TOKEN'])
        
        # Test connection with retry logic
        if await test_apify_connection(client):
            logger.info("Apify connection test successful")
        
        # Detailed input logging
        actor_input = await client.actor(os.environ['APIFY_ACTOR_ID']).get_input() or {}
        logger.debug(f"Raw actor input: {json.dumps(actor_input, indent=2)}")

        url = actor_input.get("url")
        logger.debug(f"Extracted URL: {url}")

        if not url:
            logger.error("URL validation failed - no URL provided")
            result = {"error": "No URL provided in input", "apify_input": actor_input}
            await client.key_value_store(os.environ['APIFY_DEFAULT_KEY_VALUE_STORE_ID']).set_record('OUTPUT', result)
            logger.error("No URL provided in input")
            return

        try:
            logger.debug(f"Starting recipe scrape for URL: {url}")
            scraper = scrape_me(url)
            
            # Log individual scraping steps
            logger.debug("Extracting title...")
            title = scraper.title()
            logger.debug(f"Title extracted: {title}")
            
            logger.debug("Extracting ingredients...")
            ingredients = scraper.ingredients()
            logger.debug(f"Ingredients extracted: {len(ingredients)} items")
            
            recipe_data = {
                "title": title,
                "ingredients": ingredients,
                "instructions": scraper.instructions(),
                "total_time": scraper.total_time(),
                "yields": scraper.yields(),
                "image": scraper.image(),
                "host": scraper.host(),
                "author": scraper.author(),
                "description": scraper.description(),
                "nutrients": scraper.nutrients() if hasattr(scraper, "nutrients") else None,
                "url": url
            }
            
            logger.debug(f"Complete recipe data: {json.dumps(recipe_data, indent=2)}")
            
            # Log API interaction
            logger.debug("Attempting to save to Apify KV store...")
            await client.key_value_store(os.environ['APIFY_DEFAULT_KEY_VALUE_STORE_ID']).set_record('OUTPUT', recipe_data)
            logger.debug("Save to KV store successful")
            
        except Exception as e:
            logger.exception("Detailed scraping error:")
            result = {"error": str(e)}
            await client.key_value_store(os.environ['APIFY_DEFAULT_KEY_VALUE_STORE_ID']).set_record('OUTPUT', result)
            raise

    except Exception as e:
        logger.exception("Detailed fatal error:")
        error_data = {"error": str(e), "error_type": type(e).__name__}
        await client.key_value_store(os.environ['APIFY_DEFAULT_KEY_VALUE_STORE_ID']).set_record('OUTPUT', error_data)
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
