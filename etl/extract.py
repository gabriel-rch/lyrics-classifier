import letras
import vagalume
import json
import argparse
import time
from tqdm import tqdm


def log(level, message):
    print(f"[{level}] {time.strftime('%H:%M:%S', time.localtime())} {message}")


def get_songs(genre, limit, source):
    log("INFO", f"Getting songs from {genre} at {source}")
    if source == "letras":
        return letras.get_songs(genre, limit)
    elif source == "vagalume":
        return vagalume.get_songs(genre, limit)
    else:
        log("ERROR", f"Invalid source: {source}")


def get_lyrics(song, source):
    if source == "letras":
        return letras.get_lyrics(song)
    elif source == "vagalume":
        return vagalume.get_lyrics(song)
    else:
        log("ERROR", f"Invalid source: {source}")


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source", type=str, default="letras", help="Source to get songs and lyrics from"
    )
    parser.add_argument("--limit", type=int, default=100, help="Number of songs to get from each genre")
    return parser.parse_args()


def main():
    genres = [
        "Country",
        "Forró",
        "Funk",
        "Gospel",
        "Heavy Metal",
        "Hip Hop",
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

    args = arg_parser()

    if args.source not in ["letras", "vagalume"]:
        raise ValueError(f"Invalid source: {args.source}")

    if args.limit < 1:
        raise ValueError("Limit must be at least 1")

    songs = [song for genre in genres for song in get_songs(genre, args.limit, args.source)]
    lyrics = []
    for song in tqdm(songs, desc="Getting lyrics", unit="song"):
        lyrics.append({**song, "lyrics": get_lyrics(song, args.source)})

    json.dump(lyrics, open(f"raw/{args.source}.json", "w", encoding="utf8"), ensure_ascii=False)


if __name__ == "__main__":
    main()
