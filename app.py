from flask import Flask, jsonify, send_file
import os
import concurrent.futures
import zipfile
from datetime import datetime
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
    
    # خفضنا لـ 200 عشان Vercel timeout 10 ثواني
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
            if data:
                filename = f"{key}.txt"
                zipf.writestr(filename, '\n'.join(data))
    
    return jsonify({
        'domain': domain,
        'total_found': len(urls),
        'checked': len(urls_to_check),
        'stats': {k: len(v) for k, v in results.items()},
        'download': f"/download/{os.path.basename(zip_name)}"
    })

@app.route('/download/<filename>')
def download(filename):
    return send_file(f"/tmp/{filename}", as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
