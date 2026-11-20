import pandas as pd
import matplotlib.pyplot as plt
import io
import requests

url = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-regional-cons-def/exports/csv"
params = {
    "select": "code_insee_region,libelle_region,date_heure,consommation,nucleaire",
    "where": 'libelle_region="Île-de-France" and date_heure>="2020-01-01"'}
reponse=requests.get(url,params=params)
print(reponse.status_code)
donnee_cons_regio=pd.read_csv(io.StringIO(reponse.text),sep=';')

region_conso=donnee_cons_regio.loc[:,['libelle_region','consommation']]

calcul_moy_region_conso=region_conso.groupby("libelle_region")['consommation'].mean().reset_index()
calcul_moy_region_conso=calcul_moy_region_conso.rename(columns={calcul_moy_region_conso.columns[1]:'Conso-moyenne_MW'})
X=calcul_moy_region_conso['libelle_region']
Y=calcul_moy_region_conso['Conso-moyenne_MW']

#----------historgamme consommation électricité par rapport au région

# plt.bar(X,Y, color='grey')
# plt.xticks(rotation=45,ha='right')
# plt.xlabel(xlabel='les régions')
# plt.ylabel(ylabel='consommation moyenne')
# plt.title('consomation moyenne par région')

# plt.show()

# ----------------------Précis sur les régions et les horaires en filtrant hiver et été
conso_heure_region=donnee_cons_regio.loc[:,['libelle_region','date_heure','consommation']]
conso_heure_region['date_heure']=pd.to_datetime(conso_heure_region['date_heure']).dt.tz_convert("Europe/Paris")
conso_heure_region['mois']=conso_heure_region["date_heure"].dt.month 
conso_heure_region['jours']=conso_heure_region["date_heure"].dt.day
conso_heure_region["heure"]=conso_heure_region["date_heure"].dt.hour

saisons={"Hiver":[12,1,2],"Printemps":[3,4,5],
                  'Eté':[6,7,8], 'Automne':[9,10,11]}
mois_vers_saison = {}
for saison, liste_mois in saisons.items():
    for mois in liste_mois:
        mois_vers_saison[mois] = saison


conso_heure_region["saison"]=conso_heure_region["mois"].map(mois_vers_saison)
conso_calcul_saison=conso_heure_region.groupby("saison")['consommation'].mean().reset_index()
X=conso_calcul_saison['saison']
Y=conso_calcul_saison['consommation']
plt.bar(X,Y)
plt.xlabel(xlabel='Saisons')
plt.ylabel(ylabel='consommation')
plt.title('Diagramme en baton mettant en relation la consommation en Ile de france en fonction des saisons')

