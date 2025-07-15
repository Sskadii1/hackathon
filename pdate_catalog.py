import requests
from bs4 import BeautifulSoup

def search_kb_download_link(kbid):
    url = f"https://www.catalog.update.microsoft.com/Search.aspx?q={kbid}"
    headers = {"User-Agent": "Mozilla/5.0"}
    session = requests.Session()
    r = session.get(url, headers=headers)
    if r.status_code != 200:
        return None
    
    soup = BeautifulSoup(r.text, 'html.parser')
    links = soup.find_all("a")
    for a in links:
        if "download" in a.get("onclick", "").lower():
            onclick = a["onclick"]
            start = onclick.find("('") + 2
            end = onclick.find("')", start)
            detail_url = "https://www.catalog.update.microsoft.com/" + onclick[start:end]
            return extract_msu_url(detail_url)
    return None

def extract_msu_url(detail_url):
    r = requests.get(detail_url)
    soup = BeautifulSoup(r.text, "html.parser")
    anchors = soup.select("a")
    for a in anchors:
        href = a.get("href", "")
        if href.endswith(".msu"):
            return href
    return None
