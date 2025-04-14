# generate.py generates a new recipe scraper.
import json
import os
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
    actor_input = {}
    input_path = os.environ.get('APIFY_INPUT_PATH', '/apify/input.json')
    if os.path.exists(input_path):
        with open(input_path, 'r') as f:
            actor_input = json.load(f)
    print("DEBUG: Apify input:", actor_input)

    url = actor_input.get("url")
    
    if not url:
        result = {"error": "No URL provided in input"}
        write_apify_output(result)
        return

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
    except Exception as e:
        write_apify_output({"error": str(e)})

if __name__ == "__main__":
    main()

