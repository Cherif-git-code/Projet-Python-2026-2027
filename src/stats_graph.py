import pandas as pd
import matplotlib.pyplot as plt

def moyenne_eolien(donnees, ville, col_prod="eolien", groupe="ville"):
    """Production éolienne journalière moyenne (MW) de la région représentée par une ville."""
    return (donnees[donnees[groupe] == ville]
         .groupby("jour")[col_prod].mean())

  

def donnees_meteo_prod(donnees, ville, col_meteo, col_prod):
    """Une ligne par jour pour une ville : une variable météo et la production moyenne."""
    return (donnees[donnees["ville"] == ville]
            .groupby("jour")
            .agg(meteo=(col_meteo, "first"), prod=(col_prod, "mean"))
            .dropna())


def tracer_scatter_vent_eolien(donnees, ville, col_vent="vent100_moy_jour", col_prod="eolien"):
    """Nuage de points : vent moyen journalier / production éolienne journalière."""
    g = donnees_meteo_prod(donnees, ville, col_meteo=col_vent, col_prod=col_prod)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(g["meteo"], g["prod"], s=10, alpha=0.35)
    ax.set_title(f"Vent moyen journalier à 100 m et production éolienne, région de {ville.capitalize()}")
    ax.set_xlabel("Vitesse moyenne du vent à 100 m (km/h)")
    ax.set_ylabel("Production éolienne journalière moyenne (MW)")
    plt.show()



def tracer_graphique_eolien(donnees, ville, col_prod="eolien", groupe="ville") :
        g=moyenne_eolien(donnees, ville, col_prod="eolien", groupe="ville")
        g.index = pd.to_datetime(g.index)
        fig, ax = plt.subplots(figsize=(13, 4))
        ax.plot(g.index, g.values, linewidth=0.6, alpha=0.5, color="tab:blue",
            label="Moyenne journalière")
        ax.plot(g.index, g.rolling(30, center=True).mean(), linewidth=1.8, color="tab:red",
            label="Moyenne mobile 30 jours")
        ax.set_title(f"Production éolienne journalière, région de {ville.capitalize()} (2021-2025)")
        ax.set_xlabel("Date")
        ax.set_ylabel("Production éolienne moyenne (MW)")
        ax.legend(loc="upper left")
        plt.show()