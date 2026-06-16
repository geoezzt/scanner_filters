from flask import Flask, jsonify
import os
import concurrent.futures
from scanner import get_wayback_urls, check_url

app = Flask(__name__)

@app.route('/')
def index():
    return "Step 1 OK"

@app.route('/scan/<domain>')
def scan(domain):
    urls = get_wayback_urls(domain)
    
    results = {
        '200': [], '403': [], '5xx': [], '302': [],
        'params': [], 'js': [], 'json': [], 'other': []
    }
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        for res in executor.map(check_url, urls[:500]):
            status = res['status']
            url = res['url']
            
            if status == 200: results['200'].append(url)
            elif status == 403: results['403'].append(url)
            elif status in [500, 502, 503]: results['5xx'].append(url)
            elif status in [301, 302, 307]: results['302'].append(url)
            else: results['other'].append(url)
            
            if res['type'] == 'param': 
                results['params'].append(f"{url} | {res['params']}")
            elif res['type'] == 'js': 
                results['js'].append(url)
            elif res['type'] == 'json': 
                results['json'].append(url)
    
    return jsonify({
        'domain': domain,
        'total': len(urls),
        'stats': {k: len(v) for k, v in results.items()}
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
