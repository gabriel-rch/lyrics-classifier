import requests
import bs4
import re
import json
from tqdm import tqdm


GENRE_LIST = [
    "Country",
    "Forró",
    "Funk",
    "Gospel/Religioso",
    "Heavy Metal",
    "Hip Hop/Rap",
    "K-Pop",
    "MPB",
    "Pagode",
    "Pop",
    "Rock",
    "R&B",
    "Reggaeton",
    "Samba",
    "Sertanejo",
]

SONG_LIMIT = 100


def get_songs_by_genre(genre):
    response = requests.get(f"https://www.letras.mus.br/mais-acessadas/{genre['url']}")
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    songs_info = soup.find("ol", class_="top-list_mus --top")
    songs = [
        {
            "title": song.find("a")["title"],
            "artist": song.find("a").find("span").text,
            "genre": genre["genre"],
            "link": song.find("a")["href"],
        }
        for song in songs_info.find_all("li", limit=SONG_LIMIT)
    ]

    return songs


def get_lyrics(song):
    try:
        response = requests.get(
            f"https://www.letras.mus.br{song['link']}traducao.html", cookies={"translMode": "single"}
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


def main():
    response = requests.get("https://www.letras.mus.br/estilos/")
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    all_genres = soup.find("ul", class_=re.compile("^cnt-list"))

    genres = [
        {"genre": genre.find("a").text, "url": genre.find("a")["href"].split("/")[-2]}
        for genre in all_genres.find_all("li")
        if genre.find("a").text in GENRE_LIST
    ]

    songs = [song for genre in genres for song in get_songs_by_genre(genre)]
    lyrics = []
    for song in tqdm(songs):
        lyrics.append({**song, "lyrics": get_lyrics(song)})

    json.dump(lyrics, open("raw/letras.json", "w", encoding="utf8"), ensure_ascii=False)


if __name__ == "__main__":
    main()
