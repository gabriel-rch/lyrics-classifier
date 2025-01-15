import requests
import bs4
import random
import time


GENRE_URL = {
    "Country": "browse/style/country.html",
    "Forró": "browse/style/forro.html",
    "Funk": "browse/style/funk-carioca.html",
    "Gospel": "browse/style/gospel.html",
    "Heavy Metal": "browse/style/heavy-metal.html",
    "Hip Hop": "browse/style/hip-hop.html",
    "K-Pop": "browse/style/k-pop-k-rock.html",
    "MPB": "browse/style/mpb.html",
    "Pagode": "browse/style/pagode.html",
    "Pop": "browse/style/pop.html",
    "Rock": "browse/style/rock.html",
    "R&B": "browse/style/r-n-b.html",
    "Reggaeton": "browse/style/reggaeton.html",
    "Samba": "browse/style/samba.html",
    "Sertanejo": "browse/style/sertanejo.html",
}


def make_request(url: str):
    tries = 0

    while True:
        try:
            response = requests.get(url)
            response.encoding = "utf-8"
            return response
        except Exception:
            time.sleep(5)

            tries += 1
            if tries == 5:
                raise Exception("Failed to make request")

            continue


def get_songs(genre: str, limit: int):
    response = make_request(f"https://www.vagalume.com.br/{GENRE_URL[genre]}")
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    container = soup.find("div", class_="moreNamesContainer")
    columns = container.find_all("ul")

    songs = []
    while len(songs) < limit and columns:
        top_column = columns.pop(0)

        artists = []
        for artist_info in top_column.find_all("li"):
            artists.append(
                {
                    "name": artist_info.find("a").text,
                    "link": artist_info.find("a")["href"],
                }
            )

        for artist in artists:
            time.sleep(1)  # Avoid being blocked
            response = make_request(f"https://www.vagalume.com.br{artist['link']}")
            soup = bs4.BeautifulSoup(response.text, "html.parser")

            current_songs = []

            # Top songs
            songs_info = soup.find("ol", id="topMusicList")
            if songs_info:
                for song in songs_info.find_all("li"):
                    title = song.find("a", class_="nameMusic")
                    link = song.find("a", class_="nameMusic")

                    if not title:
                        continue

                    current_songs.extend(
                        [
                            {
                                "title": title.text,
                                "artist": artist["name"],
                                "genre": genre,
                                "link": link["href"],
                            }
                        ]
                    )

            # Songs on the Named Songs list that have already been
            # added to the list of songs
            already_added = set([song["title"] for song in current_songs])

            # Named songs
            songs_info = soup.find("ol", id="alfabetMusicList")
            if songs_info:
                for song in songs_info.find_all("li"):
                    title = song.find("a", class_="nameMusic")
                    link = song.find("a", class_="nameMusic")

                    if not title or title.text in already_added:
                        continue

                    current_songs.extend(
                        [
                            {
                                "title": title.text,
                                "artist": artist["name"],
                                "genre": genre,
                                "link": link["href"],
                            }
                        ]
                    )

            songs.extend(current_songs)

    return random.sample(songs, limit)


def get_lyrics(song: dict):
    original = f"https://www.vagalume.com.br{song['link']}"
    translated = original.replace(".html", "-traducao.html")

    response = make_request(translated)
    if response.status_code != 404:
        # Song has a translation
        soup = bs4.BeautifulSoup(response.text, "html.parser")

        lyrics_pair = soup.find("div", id="lyricsPair")
        if lyrics_pair:
            # The song has the original lyrics and the translation side to side
            translated_block = lyrics_pair.find_all("div", class_="trad")
            return " ".join(
                [
                    " ".join(
                        [
                            line.strip()
                            for line in block.find("p").get_text(separator="\n").split("\n")
                            if line.strip()
                        ]
                    )
                    for block in translated_block
                ][1:] # Exclude song title
            )
        else:
            #the translation is not side to side
            return soup.find("div", id="lyrics").get_text(separator=" ")
    
    # Song has no translation or is already in Portuguese
    # non-Portuguese songs may integrate the database right now,
    # but these songs are removed in the next step
    response = make_request(original)
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    return soup.find("div", id="lyrics").get_text(separator=" ")

