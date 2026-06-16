import requests
import urllib3
from urllib.parse import urlparse, parse_qs

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_wayback_urls(domain):
    url = f"http://web.archive.org/cdx/search/cdx?url={domain}/*&output=text&fl=original&collapse=urlkey&limit=3000"
    r = requests.get(url, timeout=30)
    urls = list(set(r.text.splitlines()))
    return urls

def check_url(url):
    result = {'url': url, 'status': 0, 'type': 'other', 'params': []}
    
    if url.endswith('.js'): 
        result['type'] = 'js'
    elif url.endswith('.json'): 
        result['type'] = 'json'
    elif '?' in url and '=' in url:
        result['type'] = 'param'
        result['params'] = list(parse_qs(urlparse(url).query).keys())
    
    try:
        r = requests.get(url, timeout=5, verify=False, allow_redirects=False)
        result['status'] = r.status_code
    except:
        result['status'] = 'Error'
    
    return result
