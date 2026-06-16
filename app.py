from flask import Flask, jsonify, send_file, render_template
import os
import concurrent.futures
import zipfile
from datetime import datetime
from scanner import get_wayback_urls, check_url

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan/<domain>')
def scan(domain):
    urls = get_wayback_urls(domain)
    
    results = {
        '200': [], '403': [], '5xx': [], '302': [],
        'params': [], 'js': [], 'json': [], 'other': []
    }
    
    # 200 بس عشان Vercel timeout
    urls_to_check = urls[:200]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for res in executor.map(check_url, urls_to_check):
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
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_name = f"/tmp/{domain}_{timestamp}.zip"
    
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for key, data in results.items():
            if data
