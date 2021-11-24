from bs4 import BeautifulSoup
import requests
import json
import time
import os

directory = "./data"
artists = ["Taylor Swift","Ed sheeran","One direction"]

def scrapArtist(artist):
    """
        input:
            aritst name - string
        description:
            - scrapes lyrics of top 20 songs of the artists from azlyrics.com
            - to avoid getting blocked by the website, a 5 second delay is put between every request
    """
    link = "https://search.azlyrics.com/search.php?q={0}+{1}&w=songs&p=1".format(*artist.lower().split())
    page = requests.get(link).content
    soup = BeautifulSoup(page, "html.parser")
    songs = soup.find_all("a")[35:55]
    
    for song in songs:
        print("_".join(song["href"].split("/")[-2:]))
        _ = requests.get(song["href"]).content
        s_soup = BeautifulSoup(_, "html.parser")
        with open(directory+"/"+"_".join(song["href"].split("/")[-2:]),"w") as f:
            try:
                f.write(str(s_soup))
            except:
                pass
        time.sleep(5)
    

def parsingAZLyrics(path):
    """
        input:
            path of the lyric html
        output:
            processed python dictionary containing artist, title, lyrics
        description:
            - parse scrapped lyric html file using beautiful soup
            - extract artist name, song title, lyrics
    """
    az = {}
    with open(path,"r") as f:
        page = f.read()
    soup = BeautifulSoup(page, "html.parser")

    artists = soup.find_all('title')[0].text.split("|")[0].split("-")
    
    az['artist'] = artists[0].strip()
    az['title'] = artists[1].strip()

    lyrics = soup.find_all("div")[20]

    if lyrics:
        az['lyrics'] = lyrics.get_text(separator=' ')
    else:
        raise Exception('error: Issue with lyrics')

    az['path'] = path.split("/")[-1]
    
    return(az)

def dumpJSON(az):
    """
        input:
            lyric dictionary
        description:
            dump generated lyric json to local filesystem
    """
    path = az["path"].replace('.html','.json')
    file = open("json/"+path, 'w')
    try:
        json.dump(az, file)
    except:
        pass
    file.close()

############################# MAIN #############################

if __name__ == "__main__":

    #scrap lyrics of tap songs from select artists
    for artist in artists:
        scrapArtist(artist)

    #process/parse scrapped lyrics
    for file in os.listdir("data"):
        json_out = parsingAZLyrics("data/"+file)
        dumpJSON(json_out)