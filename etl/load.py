import os
import hopsworks
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

project = hopsworks.login(api_key_value=os.environ.get("HOPSWORKS_KEY"))
fs = project.get_feature_store()

feature_group = fs.create_feature_group(
    name="lyrics",
    version=1,
    description="A feature group containing lyrics for songs in different genres",
    primary_key=["id"],
    online_enabled=True,
)

df = pd.read_csv("lyrics.csv")
df["id"] = df.index

feature_group.insert(df)
