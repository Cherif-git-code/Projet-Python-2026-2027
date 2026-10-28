# Exploration de la source électricité (ODRÉ / éCO2mix)

## 1. La source
- Producteur : RTE, données éCO2mix.
- Portail : ODRÉ, Open Data Réseaux Énergies (https://opendata.reseaux-energies.fr/).
- Accès : API publique et gratuite, sans compte ni clé.
- Licence : données ouvertes, citer la source (« RTE, éCO2mix, via ODRÉ »). À vérifier sur la page du jeu.
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

## 5. Questions ouvertes
- S'arrêter au 31/12/2025 (définitives uniquement) ou garder 2026 ?
- Valeurs manquantes : où et quand ?
- Utiliser le taux de charge pour neutraliser la hausse du parc installé ?
- Enregistrement : CSV ou Parquet ?
- Données brutes sur GitHub (100 Mo max par fichier) ou dans le `.gitignore` ?

## 6. Conclusion
La source couvre tout le côté électricité. Elle ne contient aucune donnée météo :
il faut une deuxième source (Open-Meteo et/ou les jeux météo d'ODRÉ).
