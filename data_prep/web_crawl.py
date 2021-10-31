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
      links.append(link["href"])
  except:
    pass
links = list(set(links[:-3]))

metas = []

# ITERATE ALL THE OPENSOURCE MUSIC SHEET LINK AND GET META DATA OF THE SHEET MUSIC
for link in links:
    page = requests.get(link)
    soup = BeautifulSoup(page.content, "html.parser")
    redirect_url = ""
    for _temp in soup.find_all("link"):
        try:
            if "user" in _temp["href"]:
                redirect_url = _temp["href"]+"/sheetmusic"
        except:
            pass
    
    next = True
    page_index = 1
    while next:
        page = requests.get(redirect_url+"?page="+str(page_index))
        soup = BeautifulSoup(page.content, "html.parser")

        info = soup.find_all("div")[5]["data-content"]
        scores = json.loads(info)["store"]["page"]["data"]["scores"]
        if scores == []:
            break
        metas.extend(scores)

        page_index += 1

print("Songs:",len(metas))

with open("meta.json","w") as f:
    json.dump(metas, f)

# ITERATE THROUGH ALL SHEET MUSIC AND INDEX THE SHEET PDFs AND MUSICXMLs DOWNLOAD LINKs
downloads = []

for meta in metas:
    link = meta["_links"]["self"]["href"]
    page = requests.get(link)
    soup = BeautifulSoup(page.content, "html.parser")
    try:
        info = json.loads(soup.find_all("div")[1]["data-content"])
    except:
        downloads.append({"score":meta["title"], "download":["link broken"]})
        print("Pass")
        continue
    d = []
    for dlink in info["store"]["page"]["data"]["type_download_list"]:
        if "pdf" in dlink["type"] or "mxl" in dlink["type"]:
            d.append(dlink["url"].replace("signin","index")+"&h=17341863356683520131")
    song_d = {"score":meta["title"], "download": d}
    downloads.append(song_d)

with open("download.json","w") as f:
    json.dump(downloads, f)    