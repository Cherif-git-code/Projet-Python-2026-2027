# Projet-Python-2026-2027
Repo du groupe d'CHERIF Hugo et de SADJI Benjamin pour le projet de python

# Dans quelle mesure les conditions météorologiques expliquent-elles la consommation et la production d'électricité en France ?

Avec près de 28 % d'énergies renouvelables dans sa production d'électricité en 2024\* (hydraulique, éolien, solaire), la France est particulièrement exposée aux aléas météorologiques, du côté de l'offre autant que de la demande : la pluie alimente les barrages, le vent fait tourner les éoliennes, le soleil alimente le photovoltaïque, et les besoins en chauffage dépendent fortement de la température. A cette aune, nous avons choisi d'étudier ce phénomène à travers ce projet python.

\* Bilan électrique annuel 2024, RTE.

## Notre démarche

Si cette problématique est complexe et dépasse largement le cadre de ce projet, nous avons donc choisi d'y répondre par quelques hypothèses simples, que nous tenterons de confirmer ou d'infirmer à l'aide d'une analyse de données.

**Consommation**  Nous nous attendons, à l'échelle annuelle, à une hausse de la consommation d'électricité lorsque les températures descendent en dessous d'un certain seuil (15 degrés), en raison du chauffage, mais également lorsqu'elles dépassent un autre seuil (30 degrés), à cause de la climatisation.

**Production**  Nous chercherons à vérifier quatre hypothèses :

1. La production éolienne augmente avec la vitesse du vent.
2. La production solaire suit l'ensoleillement : nulle la nuit, maximale vers midi et en été.
3. La production hydraulique dépend des précipitations, avec un décalage dans le temps.
4. La production nucléaire est peu sensible à la météo, sauf lors des canicules (limitations dues à la température des cours d'eau).

## Limitations et choix de modélisation

- Nos données sont limitées à la période 2021-2025, afin de travailler sur une période récente tout en excluant les confinements (2020), qui auraient ajouté du bruit aux données.
- Nous approchons la météo de chaque région par celle de sa plus grande ville. Cette hypothèse est forte, notamment pour l'éolien, dont la ressource peut varier fortement à l'échelle d'une région.

## Sources et API utilisées

Deux API complémentaires ont été mobilisées :

- **éCO2mix (ODRE - Open Data Réseau Énergies)** : production et consommation d'électricité en France.
- **Open-Meteo** : données météorologiques détaillées (température, précipitations, vitesse du vent...) sur l'ensemble du territoire.

## Fichiers et organisation

- `data/` : jeux de données utilisés, leur mode de téléchargement et les transformations qui leur ont été appliquées.
- `Rendu_final.ipynb` : notebook retraçant l'ensemble du déroulé du projet, de la collecte des données à l'analyse des hypothèses.





