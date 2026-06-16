import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_wayback_urls(domain):
    url = f"http://web.archive.org/cdx/search/cdx?url={domain}/*&output=text&fl=original&collapse=urlkey&limit=3000"
    r = requests.get(url, timeout=30)
    urls = list(set(r.text.splitlines()))
    return urls
