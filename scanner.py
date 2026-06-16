import requests
import asyncio
import aiohttp

def get_wayback_urls(domain):
    url = f"http://web.archive.org/cdx/search/cdx?url={domain}/*&output=json&fl=original&collapse=urlkey"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        return [item[0] for item in data[1:]]
    except:
        return []

async def check_url(session, url):
    try:
        async with session.get(url, timeout=3, allow_redirects=False) as r:
            status = r.status
    except:
        status = 0

    url_type = 'other'
    params = ''

    if '?' in url:
        url_type = 'param'
        params = url.split('?')[1]
    elif url.endswith('.js'):
        url_type = 'js'
    elif url.endswith('.json'):
        url_type = 'json'

    return {'url': url, 'status': status, 'type': url_type, 'params': params}

async def check_urls_async(urls):
    results = {
        '200': [], '403': [], '5xx': [], '302': [],
        'params': [], 'js': [], 'json': [], 'other': []
    }

    # 100 request في نفس الوقت = سرعة صاروخ
    connector = aiohttp.TCPConnector(limit=100, ssl=False)
    timeout = aiohttp.ClientTimeout(total=5)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [check_url(session, url) for url in urls]
        responses = await asyncio.gather(*tasks)

    for res in responses:
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

    return results
