import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

SEUIL_FROID = 15   # en dessous de 15°C, on estime que les ménages français commencent à chauffer
SEUIL_CHAUD = 27   # Pareillement au dessus de 27°C, on estime qu'ils climatisent



def charger_meteo(raw_dir):
    """Fonction qui permet de charger les données de météo dans n'importe quel notebook (donc dans notre rendu final)"""
    #raw_dir est l'emplacement des données que j'ai importé donc ici ça sera toujours "data/raw/openmeteo"
    frames = []
    for f in sorted(Path(raw_dir).glob("*.json")):
        ville, annee = f.stem.rsplit("_", 1) #C'est comme ça qu'on récupère la ville (dans la colonne ville)
        payload = json.loads(f.read_text(encoding="utf-8"))
        df = pd.DataFrame(payload["hourly"])
        df["time"] = pd.to_datetime(df["time"], utc=True) #Pour l'instant on charge en UTC mais on le corrigera plus tard
        df["ville"] = ville
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def extremum_meteo(meteo, col_met, mode="max", ville=None):
    """ Fonction qui permet de donner la date (et la valeur) des extremums de la dimension métérologique spécifiée dans col_met (pour colonne météo)"""
    if mode not in ("max", "min"):
        raise ValueError("mode doit valoir 'max' ou 'min'") #On veut regarder un extremum c'est un peu superflue dans mon utilisation mais ça me permet de regarder les valeurs que peuvent prendre le mode si j'ai oublié
    
    #Si on spécifie pas la ville on prend tout meteo sinon on prend que les valeurs de la bonne ville
    df = meteo if ville is None else meteo[meteo["ville"] == ville]
    df = df.dropna(subset=[col_met]) #normalement yen a pas mais on sait jamais

    # On récupère l'indice de la ligne où on a l'extremum recherché
    idx = df.groupby("ville")[col_met].agg("idxmax" if mode == "max" else "idxmin")
    res = df.loc[idx, ["ville", "time", col_met]].reset_index(drop=True) #on prend toute la ligne

    # on a pas encore fait le traitement sur le temps donc il est encore en UTC
    if res["time"].dt.tz is not None:
        res["time"] = res["time"].dt.tz_convert("Europe/Paris")
    return res.rename(columns={col_met: "valeur"})








def temp_journ(df):
    """Température moyenne par jour et par ville par jours.""" #On en a besoin car en été on a des nuits ou la température tombe sous les 15 degrés sans qu'il ne fasse froid pour autant
    jour = (
        df.set_index("time")
          .groupby("ville")["temperature_2m"]
          .resample("D").mean() #On récupère les valeurs du jours et on prend leur moyenne
          .rename("temp_moy")
          .reset_index()
    )
    jour["sous_15"] = jour["temp_moy"] < SEUIL_FROID
    jour["sup_27"] = jour["temp_moy"] > SEUIL_CHAUD
    return jour

def preparer_meteo(meteo):
    """ Fonction servant à enrichir et nettoyer (même s'il n'y avait pas bcp à faire) meteo_pur """
    df = meteo.copy()

    # on fait la conversion UTC vers l'heure française
    df["time"] = df["time"].dt.tz_convert("Europe/Paris") #il y avait déjà une fonction pour ça dans panda

    # on retire l'heure qui déborde sur 2026 (31/12/2025 23 h UTC = 01/01/2026 0 h locale)
    df = df[df["time"].dt.year <= 2025].copy()

    df["jour"] = df["time"].dt.date                  # POur garder le jour uniquement on enlève les heures (on se sert la aussi d'une fonctionde panda)

    # Indicateurs horaires (au final on en a rien fait mais ça peut toujours servir en stats descriptives)
    df["sous_15"] = df["temperature_2m"] < SEUIL_FROID
    df["sup_27"] = df["temperature_2m"] > SEUIL_CHAUD

    # On va garder l'écart pour pas perdre de l'info
    df["deg_sous_15"] = (SEUIL_FROID - df["temperature_2m"]).clip(lower=0)
    df["deg_sup_27"] = (df["temperature_2m"] - SEUIL_CHAUD).clip(lower=0)

    # Indicateurs journaliers sur la température
    par_jour = df.groupby(["ville", "jour"])["temperature_2m"]
    df["tmax_jour"] = par_jour.transform("max")
    df["tmoy_jour"] = par_jour.transform("mean")
    df["jour_chaud"] = df["tmax_jour"] > SEUIL_CHAUD
    df["jour_froid"] = df["tmoy_jour"] < SEUIL_FROID
    
    #Indicateur journalier de la vitesse moyenne du vent à 100m 
    df["vent100_moy_jour"] = df.groupby(["ville", "jour"])["wind_speed_100m"].transform("mean")
    df["vent100_max_jour"] = df.groupby(["ville", "jour"])["wind_speed_100m"].transform("max")
    return df

def cumul_mensuel_precipitation(meteo,ville) :
    """ Fonction qui renvoit la précipitation agrégée du mois dans une ville"""
    return (
        meteo[meteo["ville"] == ville]
        .set_index("time")["precipitation"]
        .resample("MS").sum()
    ) 



#On fait l'équivalent pour les températures et la vitesse du vent
def _serie_jour(meteo, ville, colonne): #serie pour serie temporelle
    """fonction qui converti en datetime la dataframe d'intérêt"""
    j = meteo[meteo["ville"] == ville].drop_duplicates("jour") #on a pas peur de perdre de l'info car on travaille sur des moyennes et des max journaliers donc les valeurs sont identiques par jour
    return j.set_index(pd.to_datetime(j["jour"]))[colonne].sort_index()


def temperature_moyenne_jour(meteo, ville):
    """Température moyenne de chaque jour (°C)."""
    return _serie_jour(meteo, ville, "tmoy_jour")


def temperature_max_jour(meteo, ville):
    """Température maximale de chaque jour (°C)."""
    return _serie_jour(meteo, ville, "tmax_jour")

def vent_moyen_jour(meteo, ville):
    """Vitesse moyenne du vent à 100 m pour chaque jour en km/h."""
    return _serie_jour(meteo, ville, "vent100_moy_jour")

def vent_max_jour(meteo, ville):
    """Vitesse maximum du vent à 100 m pour chaque jour en km/h."""
    return _serie_jour(meteo, ville, "vent100_max_jour")

def precipitation_jour(meteo,ville) :
    return _serie_jour(meteo, ville, "precipitation")


















#Fonctions utilisées pour plot les fonctions précédentes, ( leur différence est principalement des titres )


def tracer_cumul_mensuel_precipitation(meteo, ville):
    pluie= cumul_mensuel_precipitation(meteo,ville)
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.bar(pluie.index, pluie.values, width=25)
    ax.set_title(f"Précipitations mensuelles cumulées à {ville.capitalize()} (2021-2025)")
    ax.set_xlabel("Mois")
    ax.set_ylabel("Précipitations en mm")
    plt.show()

def tracer_temperature_moyenne_jour(meteo, ville):
    tmoy = temperature_moyenne_jour(meteo, ville)
    fig, ax = plt.subplots(figsize=(13, 4))
    ax.plot(tmoy.index, tmoy.values, linewidth=0.8, color="tab:blue", label="Température moyenne")
    ax.axhline(SEUIL_FROID, color="tab:cyan", linestyle="--", label=f"Seuil de froid ({SEUIL_FROID} °C, sur la moyenne)")
    ax.axhline(SEUIL_CHAUD, color="tab:red", linestyle="--", label=f"Seuil de chaleur ({SEUIL_CHAUD} °C, sur le maximum)")
    ax.set_title(f"Températures moyennes journalières à {ville.capitalize()} (2021-2025)")
    ax.set_xlabel("Date"); ax.set_ylabel("Température (°C)")
    ax.legend(loc="upper left")
    plt.show()

def tracer_temperature_max_jour(meteo,ville) :
    tmax = temperature_max_jour(meteo, ville)
    fig, ax = plt.subplots(figsize=(13, 4))
    ax.plot(tmax.index, tmax.values, linewidth=0.8, color="tab:orange", label="Température maximale")
    ax.axhline(SEUIL_FROID, color="tab:cyan", linestyle="--", label=f"Seuil de froid ({SEUIL_FROID} °C, sur la moyenne)")
    ax.axhline(SEUIL_CHAUD, color="tab:red", linestyle="--", label=f"Seuil de chaleur ({SEUIL_CHAUD} °C, sur le maximum)")
    ax.set_title(f"Températures maximales journalières à {ville.capitalize()} (2021-2025)")
    ax.set_xlabel("Date"); ax.set_ylabel("Température (°C)")
    ax.legend(loc="upper left")
    plt.show()

def tracer_vent_moyen_jour(meteo, ville):
    vent = vent_moyen_jour(meteo, ville)

    fig, ax = plt.subplots(figsize=(13, 4))
    ax.plot(vent.index, vent.values, linewidth=0.8, color="tab:green", label="Vent moyen journalier à 100 m")
    ax.plot(vent.index, vent.rolling(30, center=True).mean(), linewidth=1.8, color="tab:red", 
            label="Moyenne mobile 30 jours") #Pour rendre plus lisible
    ax.axhline(vent.mean(), color="gray", linestyle="--", label=f"Moyenne 2021-2025 ({vent.mean():.1f} km/h)")
    ax.set_title(f"Vitesse moyenne journalière du vent à 100 m à {ville.capitalize()} (2021-2025)")
    ax.set_xlabel("Date"); ax.set_ylabel("Vitesse du vent (km/h)")
    ax.legend(loc="upper left")
    plt.show()

def tracer_vent_max_jour(meteo, ville):
    vent = vent_max_jour(meteo, ville)

    fig, ax = plt.subplots(figsize=(13, 4))
    ax.plot(vent.index, vent.values, linewidth=0.8, color="tab:green", label="Vent max journalier à 100 m")
    ax.plot(vent.index, vent.rolling(30, center=True).mean(), linewidth=1.8, color="tab:red",
            label="Moyenne mobile 30 jours")
    ax.axhline(vent.mean(), color="gray", linestyle="--", label=f"Moyenne 2021-2025 ({vent.mean():.1f} km/h)")
    ax.set_title(f"Vitesse max journalière du vent à 100 m à {ville.capitalize()} (2021-2025)")
    ax.set_xlabel("Date"); ax.set_ylabel("Vitesse du vent (km/h)")
    ax.legend(loc="upper left")
    plt.show()

def tracer_precipitation_jour(meteo, ville):
    pluie = precipitation_jour(meteo,ville)

    fig, ax = plt.subplots(figsize=(13, 4))
    ax.plot(pluie.index, pluie.values, linewidth=0.8, color="tab:green", label="precipitation journalière")
    ax.plot(pluie.index, pluie.rolling(30, center=True).mean(), linewidth=1.8, color="tab:red",
            label="Moyenne mobile 30 jours")
    ax.axhline(pluie.mean(), color="gray", linestyle="--", label=f"Moyenne 2021-2025 ({pluie.mean():.1f} mm)")
    ax.set_title(f"Precipitation journalière à {ville.capitalize()} (2021-2025)")
    ax.set_xlabel("Date"); ax.set_ylabel("precipitation (mm)")
    ax.legend(loc="upper left")
    plt.show()