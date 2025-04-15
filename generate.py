import json
import os
from recipe_scrapers import scrape_me

def write_apify_output(data):
    output_path = '/apify/output.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(data, f)

def main():
    # Read input from Apify
    try:
        with open('/apify/input.json', 'r') as f:
            input_data = json.load(f)
            url = input_data.get('url')
    except:
        write_apify_output({"error": "Failed to read input"})
        return

    if not url:
        write_apify_output({"error": "No URL provided"})
        return

    try:
        scraper = scrape_me(url)
        recipe = {
            "title": scraper.title(),
            "total_time": scraper.total_time(),
            "yields": scraper.yields(),
            "ingredients": scraper.ingredients(),
            "instructions": scraper.instructions(),
            "image": scraper.image(),
            "url": url
        }
        write_apify_output(recipe)
    except Exception as e:
        write_apify_output({"error": str(e)})

if __name__ == "__main__":
    main()
