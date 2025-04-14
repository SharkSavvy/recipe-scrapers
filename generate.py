# generate.py generates a new recipe scraper.
import json
import os
from recipe_scrapers import scrape_me
from apify_client import ApifyClient # Import ApifyClient

# Remove get_apify_input as we'll use the client

def write_apify_output(data):
    output_path = os.environ.get('APIFY_OUTPUT_PATH', '/apify/output.json')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"DEBUG: Wrote output to {output_path}")
    # Print the contents of the output file for debugging
    with open(output_path, 'r') as f:
        print("DEBUG: Output file contents:", f.read())

async def main(): # Make main async for ApifyClient
    # Initialize the ApifyClient
    client = ApifyClient(os.environ.get('APIFY_TOKEN')) # Assumes APIFY_TOKEN env var is set

    # Get the Actor input
    actor_input = await client.actor(os.environ.get('APIFY_ACTOR_ID')).get_input() or {}
    print("DEBUG: Apify input received via client:", actor_input)

    url = actor_input.get("url")
    if not url:
        result = {"error": "No URL provided in input", "apify_input": actor_input}
        write_apify_output(result)
        print(result)
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
        # Use client to set output instead of writing file directly
        await client.key_value_store(os.environ.get('APIFY_DEFAULT_KEY_VALUE_STORE_ID')).set_record('OUTPUT', recipe_data)
        print("DEBUG: Set output via client:", recipe_data)
    except Exception as e:
        result = {"error": str(e)}
        # Use client to set output
        await client.key_value_store(os.environ.get('APIFY_DEFAULT_KEY_VALUE_STORE_ID')).set_record('OUTPUT', result)
        print("DEBUG: Set error output via client:", result)

if __name__ == "__main__":
    # Run the async main function
    import asyncio
    asyncio.run(main())

