import requests
import bs4
import time


GENRE_URL = {
    "Country": "mais-acessadas/country",
    "Forró": "mais-acessadas/forro",
    "Funk": "mais-acessadas/funk",
    "Gospel": "mais-acessadas/gospelreligioso",
    "Heavy Metal": "mais-acessadas/heavy-metal",
    "Hip Hop": "mais-acessadas/hip-hop-rap",
    "K-Pop": "mais-acessadas/k-pop",
    "MPB": "mais-acessadas/mpb",
    "Pagode": "mais-acessadas/pagode",
    "Pop": "mais-acessadas/pop",
    "Rock": "mais-acessadas/rock",
    "R&B": "mais-acessadas/rb",
    "Reggaeton": "mais-acessadas/reggaeton",
    "Samba": "mais-acessadas/samba",
    "Sertanejo": "mais-acessadas/sertanejo",
}


def make_request(url: str):
    tries = 0
    while True:
        try:
            response = requests.get(url, cookies={"translMode": "single"})
            if response.status_code != 200:
                raise Exception(f"Failed to make request. Status code: {response.status_code}")
            return response
        except Exception:
            time.sleep(5)
            tries += 1
            if tries == 5:
                raise Exception("Failed to make request")
            continue


def get_songs(genre: str, limit: int):
    response = make_request(f"https://www.letras.mus.br/{GENRE_URL[genre]}/")
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    songs_info = soup.find("ol", class_="top-list_mus --top")
    songs = [
        {
            "title": song.find("a")["title"],
            "artist": song.find("a").find("span").text,
            "genre": genre,
            "link": song.find("a")["href"],
        }
        for song in songs_info.find_all("li", limit=limit)
    ]

    return songs


def get_lyrics(song: dict):
    try:
        response = make_request(
            f"https://www.letras.mus.br{song['link']}traducao.html"
        )
    except Exception as e:
        print(f"Failed to get lyrics for {song['title']} by {song['artist']}: {e}")
        return None

    soup = bs4.BeautifulSoup(response.text, "html.parser")

    translated_lyrics = soup.find("div", class_="translation-single")
    original_lyrics = soup.find("div", class_="lyric-original")
    lyrics = translated_lyrics or original_lyrics
    if not lyrics:
        return None

    verses = [
        " ".join([line.strip() for line in p.get_text(separator="\n").split("\n") if line.strip()])
        for p in lyrics.find_all("p")
    ]

    return " ".join(verses)
