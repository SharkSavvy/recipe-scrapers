# generate.py generates a new recipe scraper.
import json
import os
import sys
from recipe_scrapers import scrape_me

def write_apify_output(data):
    output_path = os.environ.get('APIFY_OUTPUT_PATH', '/apify/output.json')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"DEBUG: Wrote output to {output_path}")
    with open(output_path, 'r') as f:
        print("DEBUG: Output file contents:", f.read())

def main():
    # Try to get input from multiple sources
    actor_input = {}
    
    # 1. Try reading from stdin first (direct API input)
    if not sys.stdin.isatty():
        try:
            stdin_data = sys.stdin.read()
            print("DEBUG: Received stdin data:", stdin_data)
            actor_input = json.loads(stdin_data)
        except Exception as e:
            print("DEBUG: Failed to parse stdin:", e)
    
    # 2. Fall back to input file if stdin was empty
    if not actor_input:
        input_path = os.environ.get('APIFY_INPUT_PATH', '/apify/input.json')
        if os.path.exists(input_path):
            with open(input_path, 'r') as f:
                actor_input = json.load(f)
    
    print("DEBUG: Final Apify input:", actor_input)

    # Extract URL and validate
    url = actor_input.get("url")
    if not url:
        result = {"error": "No URL provided in input"}
        write_apify_output(result)
        print("DEBUG: No URL found in input")
        return

    print("DEBUG: Processing URL:", url)

    try:
        scraper = scrape_me(url)
        recipe_data = {
            "title": scraper.title(),
            "ingredients": scraper.ingredients(),
            "instructions": scraper.instructions(),
            "total_time": scraper.total_time(),
            "yields": scraper.yields(),
            "url": url
        }
        write_apify_output(recipe_data)
        print("DEBUG: Successfully scraped recipe")
    except Exception as e:
        error_msg = {"error": str(e)}
        write_apify_output(error_msg)
        print("DEBUG: Scraping failed:", str(e))

if __name__ == "__main__":
    main()

