#from Selenium import webdriver  
#import time  
#from Selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import requests
import json

# START FROM BASE URL
URL = "https://openscore.cc/"
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")

links = []
for link in soup.findAll('a'):
  try:
    if "musescore" in link["href"]:
      links.append(link)
  except:
    pass
links = list(set(links))

metas = []

# ITERATE ALL THE OPENSOURCE MUSIC SHEET LINK AND GET META DATA OF THE SHEET MUSIC
for link in links:
    page = requests.get(link)
    soup = BeautifulSoup(page.content, "html.parser")
    redirect_url = ""
    for _temp in soup.find_all("link"):
        try:
            if "user" in _temp["href"]:
                redirect_url = _temp["href"]
        except:
            pass
    
    page = requests.get(redirect_url)
    soup = BeautifulSoup(page.content, "html.parser")

    for info in soup.find_all("div")[5]["data-content"]:
        metas.extend(json.loads(info)["store"]["page"]["data"]["last_scores"])

with open("meta.json","w") as f:
    json.dumps(metas, f)

# ITERATE THROUGH ALL SHEET MUSIC AND INDEX THE SHEET PDFs AND MUSICXMLs DOWNLOAD LINKs
downloads = []

for meta in metas:
    link = meta["_links"]["self"]["href"]
    page = requests.get(link)
    soup = BeautifulSoup(page.content, "html.parser")
    info = json.loads(soup.find_all("div")[1]["data-content"])

    d = []
    for dlink in info["store"]["page"]["data"]["type_download_list"]:
        if "pdf" in dlink or "mxl" in dlink["type"]:
            d.append(dlink["url"].replace("signin","index")+"&h=17341863356683520131")
    song_d = {"score":meta["title"], "download": d}
    downloads.append(song_d)

with open("download.json","w") as f:
    json.dumps(downloads, f)    