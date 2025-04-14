# generate.py generates a new recipe scraper.
import json
import os
import logging
from recipe_scrapers import scrape_me
from apify_client import ApifyClient

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

async def main():
    try:
        # Validate environment variables first
        validate_env_vars()
        
        # Initialize the ApifyClient with error handling
        client = ApifyClient(os.environ['APIFY_TOKEN'])
        
        # Test client connection
        try:
            await client.actor(os.environ['APIFY_ACTOR_ID']).get()
            logger.debug("Successfully connected to Apify")
        except Exception as e:
            logger.error(f"Failed to connect to Apify: {str(e)}")
            raise

        # Get the Actor input
        actor_input = await client.actor(os.environ['APIFY_ACTOR_ID']).get_input() or {}
        logger.debug(f"Apify input received via client: {actor_input}")

        url = actor_input.get("url")
        if not url:
            result = {"error": "No URL provided in input", "apify_input": actor_input}
            await client.key_value_store(os.environ['APIFY_DEFAULT_KEY_VALUE_STORE_ID']).set_record('OUTPUT', result)
            logger.error("No URL provided in input")
            return

        try:
            scraper = scrape_me(url)
            recipe_data = {
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
            try:
                await client.key_value_store(os.environ['APIFY_DEFAULT_KEY_VALUE_STORE_ID']).set_record('OUTPUT', recipe_data)
                logger.debug(f"Successfully saved recipe data for URL: {url}")
            except Exception as e:
                logger.error(f"Failed to save output: {str(e)}")
                raise
        except Exception as e:
            result = {"error": str(e)}
            await client.key_value_store(os.environ['APIFY_DEFAULT_KEY_VALUE_STORE_ID']).set_record('OUTPUT', result)
            logger.error(f"Error during scraping: {str(e)}")
            raise

    except Exception as e:
        error_data = {"error": str(e), "error_type": type(e).__name__}
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        await client.key_value_store(os.environ['APIFY_DEFAULT_KEY_VALUE_STORE_ID']).set_record('OUTPUT', error_data)
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
