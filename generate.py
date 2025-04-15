import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from recipe_scrapers import scrape_me

class RecipeHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Read request body
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        
        url = data.get('url')
        if not url:
            self.send_error(400, "No URL provided")
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
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(recipe_data).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

def run():
    port = int(os.environ.get('ACTOR_WEB_SERVER_PORT', 4321))
    server = HTTPServer(('', port), RecipeHandler)
    print(f'Starting server on port {port}...')
    server.serve_forever()

if __name__ == '__main__':
    run()
