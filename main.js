const Apify = require('apify');
const { execSync } = require('child_process');

Apify.main(async () => {
    const input = await Apify.getInput();
    console.log('Received input:', input);

    if (!input?.url) {
        throw new Error('URL is required in input');
    }

    try {
        // Run Python script and capture output
        const pythonScript = `
import json
from recipe_scrapers import scrape_me

try:
    scraper = scrape_me("${input.url}")
    print(json.dumps({
        "title": scraper.title(),
        "ingredients": scraper.ingredients(),
        "instructions": scraper.instructions(),
        "total_time": scraper.total_time(),
        "yields": scraper.yields(),
        "image": scraper.image(),
        "url": "${input.url}"
    }))
except Exception as e:
    print(json.dumps({"error": str(e)}))
`;
        const result = execSync(`python3 -c '${pythonScript}'`, { encoding: 'utf8' });
        const recipe = JSON.parse(result);
        
        if (recipe.error) {
            throw new Error(recipe.error);
        }

        await Apify.pushData(recipe);
        console.log('Successfully scraped recipe:', recipe.title);
    } catch (err) {
        console.error('Scraping failed:', err);
        throw err;
    }
});
