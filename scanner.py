import requests

def get_wayback_urls(domain):
    url = f"http://web.archive.org/cdx/search/cdx?url={domain}/*&output=json&fl=original&collapse=urlkey"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        return [item[0] for item in data[1:]]
    except:
        return []

def check_url(url):
    try:
        r = requests.get(url, timeout=5, allow_redirects=False)
        status = r.status_code
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
