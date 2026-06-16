from flask import Flask, jsonify, send_file, render_template
import os
import asyncio
import aiohttp
import zipfile
from datetime import datetime
from scanner import get_wayback_urls, check_urls_async

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan/<domain>')
def scan(domain):
    urls = get_wayback_urls(domain)

    # نزود العدد للسرعة القصوى
    urls_to_check = urls[:1000]

    # تشغيل async
    results = asyncio.run(check_urls_async(urls_to_check))

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

application = app
