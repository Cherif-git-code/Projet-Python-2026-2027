import json
from pathlib import Path
import pandas as pd

def charger_meteo(raw_dir):
    #Fonction qui permet de charger les données de météo dans n'importe quel notebook
    frames = []
    for f in sorted(Path(raw_dir).glob("*.json")):
        ville, annee = f.stem.rsplit("_", 1)
        payload = json.loads(f.read_text(encoding="utf-8"))
        df = pd.DataFrame(payload["hourly"])
        df["time"] = pd.to_datetime(df["time"], utc=True)
        df["ville"] = ville
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


