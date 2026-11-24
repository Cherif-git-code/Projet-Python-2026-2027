# Exploration de la source électricité (ODRÉ / éCO2mix)

## 1. La source
- Producteur : RTE, données éCO2mix.
- Portail : ODRÉ, Open Data Réseaux Énergies (https://opendata.reseaux-energies.fr/).
- Accès : API publique et gratuite, sans compte ni clé.
- Licence : Licence Ouverte v2.0 (Etalab), réutilisation libre à condition de citer la source
  (« RTE, éCO2mix, via ODRÉ »). Dernière mise à jour du jeu : 07/10/2026.

- Jeu utilisé : `eco2mix-regional-cons-def` (historique régional).
  - Autres jeux : `eco2mix-national-cons-def` (France, quart d'heure),
    `eco2mix-regional-tr` / `eco2mix-national-tr` (temps réel, non vérifiés).
- Période : données définitives 2013 → 31/12/2025, consolidées 2026 → fin août 2026.
  La colonne `nature` indique le type de chaque ligne.

## 2. Comment y accéder
- Adresse de base : https://odre.opendatasoft.com/api/explore/v2.1/ (API Opendatasoft v2.1)
- Points d'accès (`catalog/datasets/<id>/...`) :
  - `<id>` : description (colonnes, types, unités)
  - `<id>/records` : 100 lignes maximum, pour tester
  - `<id>/exports/csv` : export complet, pour la collecte
  - `<id>/exports` : formats disponibles (csv, json, parquet, xlsx…)
  - `<id>/facets` : valeurs possibles (régions, nature, années)
- Paramètres : `select` (colonnes), `where` (filtre, conditions reliées par `and`),
  `order_by` (tri), `limit` (nombre de lignes).
- Méthode : `requests.get(url, params=...)` puis
  `pd.read_csv(io.StringIO(reponse.text), sep=";")`.

## 3. Contenu
- Identifiants : `code_insee_region`, `libelle_region` (12 régions).
- Temps : `date` et `heure` (texte, heure française), `date_heure` (UTC, +00:00).
- Puissances en MW : consommation, nucleaire, eolien, solaire, hydraulique,
  thermique, bioenergies, pompage, ech_physiques (négatif = la région exporte).
- Taux en % : `tco_<filière>` (taux de couverture), `tch_<filière>` (taux de charge).
- Pas de temps : une demi-heure, soit 48 lignes par jour et par région.
- Volumes : jeu complet ≈ 2,9 M lignes ; toutes régions depuis 2020 : 1 402 536 ;
  Nouvelle-Aquitaine depuis 2020 : 116 878.
- Codes INSEE : ARA 84, BFC 27, Bretagne 53, CVL 24, Grand Est 44, HdF 32,
  Île-de-France 11, Normandie 28, Nouvelle-Aquitaine 75, Occitanie 76,
  Pays de la Loire 52, PACA 93.

## 4. Pièges et solutions
- `date_heure` en UTC → `pd.to_datetime` puis `.dt.tz_convert("Europe/Paris")`
- `date_heure` arrive en texte → `pd.to_datetime`
- `eolien` stocké en texte → conversion en nombre au nettoyage
- Accents et apostrophes dans les noms de régions → filtrer par code INSEE
- MW ≠ MWh → énergie = puissance × 0,5 h par ligne
- Sans `select` ni `where`, tout le jeu est téléchargé → toujours filtrer
- Retéléchargement long → enregistrer une fois dans `data/raw/`
- Colonne parasite `column_30` → à ignorer

## 5. Choix retenus
- Période : du 01/01/2021 au 31/12/2025, données définitives uniquement (2020 écarté à cause des confinements, 2026 parce que les données ne sont que consolidées).
- Valeurs manquantes : les « - » de la colonne `eolien` deviennent des valeurs manquantes, la dernière demi-heure du 31/12/2025 est vide, et l'heure du passage à l'heure d'hiver (octobre) est absente chaque année. Après passage à l'heure et jointure avec la météo, il ne reste aucune valeur manquante.
- Pas de temps : passage de la demi-heure à l'heure (moyenne des deux demi-heures, car ce sont des puissances en MW), pour correspondre aux données météo horaires.
- Format : Parquet, plus léger et plus rapide à lire que le CSV, et qui conserve les types des colonnes.
- Stockage : les données brutes sont versionnées sur GitHub (environ 10 Mo, sous la limite de 100 Mo), pour que le notebook tourne sans retélécharger.
- Taux de charge : non utilisé. Il permettrait de neutraliser la hausse du parc installé (solaire notamment), c'est une piste d'amélioration.


## 6. Conclusion
La source couvre tout le côté électricité. Elle ne contient aucune donnée météo :
il faut une deuxième source (Open-Meteo et/ou les jeux météo d'ODRÉ).
