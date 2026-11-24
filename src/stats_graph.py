import pandas as pd
import matplotlib.pyplot as plt

def moyenne_prod(donnees, ville, col_prod, groupe="ville"):
    """Calcule la production moyenne par jour pour la filière col_prod (en MW)."""
    serie = (donnees[donnees[groupe] == ville]
             .groupby("jour")[col_prod].mean())
    serie.index = pd.to_datetime(serie.index)
    return serie



def donnees_meteo_prod(donnees, ville, col_meteo, col_prod):
    """Une ligne par jour pour une ville : une variable météo et la production moyenne par jour."""
    return (donnees[donnees["ville"] == ville]
            .groupby("jour")
            .agg(meteo=(col_meteo, "first"), prod=(col_prod, "mean"))
            .dropna())


def production_mensuelle(donnees, ville, col_prod, groupe="ville"):
    """Énergie produite par mois (GWh) pour la filière col_prod."""
    mw_moyens = moyenne_prod(donnees, ville, col_prod, groupe)   # MW moyens par jour
    gwh_jour = mw_moyens * 24 / 1000                              # MW x 24 h = MWh, /1000 = GWh
    return gwh_jour.resample("MS").sum()


def corr(pluie,prod,ville) :
    m = pd.concat({"pluie": pluie, "prod": prod}, axis=1).dropna()
    import matplotlib.pyplot as plt

    lags = range(0, 7)
    corr = [m["prod"].corr(m["pluie"].shift(k), method="spearman") for k in lags]

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(list(lags), corr)
    ax.set_title(f"Corrélation entre la production hydraulique et les précipitations décalées, {ville.capitalize()}")
    ax.set_xlabel("Décalage de la pluie (mois)")
    ax.set_ylabel("Corrélation de Spearman")
    plt.show()


def tracer_scatter_pluie_prec(pluie,prod,ville) :
    m = pd.concat({"pluie": pluie, "prod": prod}, axis=1).dropna()
    k = 1   # à remplacer par le décalage trouvé en piste 1
    plt.scatter(m["pluie"].shift(k), m["prod"], s=15)
    plt.xlabel(f"Précipitations du mois M-{k} (mm)")
    plt.ylabel("Production hydraulique (GWh)")
    plt.show()  

def tracer_graph_hydrau_pluie(pluie,prod,ville) :
    m=pd.concat({"pluie": pluie, "prod": prod}, axis=1).dropna()
    fig, ax1 = plt.subplots(figsize=(12, 4))
    ax1.bar(m.index, m["pluie"], width=25, color="lightsteelblue", label="Précipitations")
    ax1.set_ylabel("Précipitations (mm)")
    ax2 = ax1.twinx()
    ax2.plot(m.index, m["prod"], color="tab:blue", marker="o", label="Production hydraulique")
    ax2.set_ylabel("Production hydraulique (GWh)")
    ax1.set_title(f"Précipitations et production hydraulique mensuelles, {ville.capitalize()}")
    plt.show()

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
        g=moyenne_prod(donnees, ville, col_prod="eolien", groupe="ville")
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

def tracer_graphique_hydrau(donnees, ville, col_prod="hydraulique", groupe="ville") :
        g=moyenne_prod(donnees, ville, col_prod, groupe="ville")
        g.index = pd.to_datetime(g.index)
        fig, ax = plt.subplots(figsize=(13, 4))
        ax.plot(g.index, g.values, linewidth=0.6, alpha=0.5, color="tab:blue",
            label="Moyenne journalière")
        ax.plot(g.index, g.rolling(30, center=True).mean(), linewidth=1.8, color="tab:red",
            label="Moyenne mobile 30 jours")
        ax.set_title(f"Production hydraulique journalière, région de {ville.capitalize()} (2021-2025)")
        ax.set_xlabel("Date")
        ax.set_ylabel("Production hydraulique moyenne (MW)")
        ax.legend(loc="upper left")
        plt.show()

def tracer_hydrau_mois(donnees, ville, col_prod="hydraulique"):
    """Production hydraulique mensuelle (GWh) de la région représentée par une ville."""
    prod = production_mensuelle(donnees, ville, col_prod)

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.bar(prod.index, prod.values, width=25, color="tab:blue")
    ax.set_title(f"Production hydraulique mensuelle, région de {ville.capitalize()} (2021-2025)")
    ax.set_xlabel("Mois")
    ax.set_ylabel("Production hydraulique (GWh)")
    plt.show()