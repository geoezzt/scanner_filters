from flask import Flask
import os
from scanner import get_wayback_urls

app = Flask(__name__)

@app.route('/')
def index():
    return "Step 1 OK"

@app.route('/scan/<domain>')
def scan(domain):
    urls = get_wayback_urls(domain)
    return f"Found {len(urls)} URLs"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
