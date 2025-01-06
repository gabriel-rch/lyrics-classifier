import os
import json
import pandas as pd
import itertools


def main():
    data = itertools.chain.from_iterable(
        json.load(open(f"raw/{file}", "r", encoding="utf8"))
        for file in os.listdir("raw")
        if file.endswith(".json")
    )

    df = pd.DataFrame(data)
    df = df.drop(columns=["link"])
    df.to_csv("data/lyrics.csv", index=False)


if __name__ == "__main__":
    main()
