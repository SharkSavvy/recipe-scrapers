import { Actor } from 'apify';
import { execSync } from 'child_process';

await Actor.init();

try {
    // Get input
    const input = await Actor.getInput();
    console.log('Input:', input);

    if (!input?.url) {
        throw new Error('URL is required in input');
    }

    // Run Python script with proper escaping
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

    await Actor.pushData(recipe);
    console.log('Successfully scraped recipe:', recipe.title);

} catch (err) {
    console.error('Error:', err);
    throw err;
} finally {
    await Actor.exit();
}

