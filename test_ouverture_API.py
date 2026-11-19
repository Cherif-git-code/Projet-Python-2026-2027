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
