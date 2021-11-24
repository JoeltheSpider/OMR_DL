from bs4 import BeautifulSoup
import requests
import json
import time
import os

# INSERT YOUR PATH TO lyrics_collection DIRECTORY:
directory = "./data"
artists = ["taylor swift", "Ed sheeran",""]

def scrap_artist(artist):
    link = "https://search.azlyrics.com/search.php?q={0}+{1}&w=songs&p=1".format(*artist.lower().split())
    page = requests.get(link).content
    soup = BeautifulSoup(page, "html.parser")
    songs = soup.find_all("a")[35:55]
    
    for song in songs:
        print("_".join(song["href"].split("/")[-2:]))
        _ = requests.get(song["href"]).content
        s_soup = BeautifulSoup(_, "html.parser")
        with open(directory+"/"+"_".join(song["href"].split("/")[-2:]),"w") as f:
            f.write(str(s_soup))
        time.sleep(5)
    

def parsingAZLyrics(path):
    # Scraping function with Beautiful soup method
    # Extract artist and title through itemprop tag
    # Remove all </br> tag from html page
    # Extract the text of the songs from id tag
    # Extract the URL from class = fb-like
    # Store all this information for every song in a dictionary. One dict for every song.
    az = {}
    with open(path,"r") as f:
        page = f.read()
    soup = BeautifulSoup(page, "html.parser")

    artists = soup.find_all('title')[0].text.split("|")[0].split("-")
    # print(artists)
    az['artist'] = artists[0].strip()
    az['title'] = artists[1].strip()

    lyrics = soup.find_all("div")[20]

    if lyrics:
        az['lyrics'] = lyrics.get_text(separator=' ')
    else:
        raise Exception('COPYRIGHT!')

    az['path'] = path.split("/")[-1]
    
    return(az)

def dumpJSON(az):
    #Generate one file JSON given the path of the file and the dictionary (az)
    path = az["path"].replace('.html','.json')
    file = open("json/"+path, 'w')
    try:
        json.dump(az, file)
    except:
        pass
    file.close()

# _ = parsingAZLyrics("data/taylorswift_alltoowell.html")
# dumpJSON(_)
# print(_)

# main

#for artist in artists:
#    scrap_artist(artists)

for file in os.listdir("data"):
    json_out = parsingAZLyrics("data/"+file)
    dumpJSON(json_out)