# generate.py generates a new recipe scraper.
import json
import os
from recipe_scrapers import scrape_me

def get_apify_input():
    input_path = os.environ.get('APIFY_INPUT_PATH', '/apify/input.json')
    if os.path.exists(input_path):
        with open(input_path, 'r') as f:
            return json.load(f)
    return {}

def write_apify_output(data):
    output_path = os.environ.get('APIFY_OUTPUT_PATH', '/apify/output.json')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    apify_input = get_apify_input()
    url = apify_input.get("url")
    if not url:
        result = {"error": "No URL provided in input"}
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
        write_apify_output(recipe_data)
        print(recipe_data)
    except Exception as e:
        result = {"error": str(e)}
        write_apify_output(result)
        print(result)

if __name__ == "__main__":
    main()

