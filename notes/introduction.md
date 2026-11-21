# Introduction (premier jet)

## Question
Dans quelle mesure les conditions météorologiques expliquent-elles
la consommation et la production d'électricité en France ?

## Contexte
- Pourquoi la France est particulièrement sensible au froid (chauffage électrique) : [chiffres à trouver]
- Place des renouvelables (éolien, solaire), dont la production dépend de la météo : [chiffres à trouver]
- Sources : Bilan électrique RTE, [...]

## Hypothèses

### Consommation
1. La consommation d'électricité augmente lors des températures extrêmes :
   avec le chauffage quand il fait froid, avec la climatisation quand il fait chaud.
   L'effet du froid devrait être nettement plus fort que celui de la chaleur,
   car le chauffage électrique est beaucoup plus répandu que la climatisation en France.
   Il apparaîtrait sous un seuil de température d'environ [15 °C ?].
2. La consommation atteint son maximum en soirée (entre [17 h] et [1 h]).
   Ce pic serait plus marqué en hiver, avec le chauffage et l'éclairage, puisque la nuit tombe plus tôt.

### Production (propositions à valider)
3. La production éolienne augmente avec la vitesse du vent.
4. La production solaire suit l'ensoleillement : nulle la nuit, maximale vers midi et en été.
5. La production hydraulique dépend des précipitations, avec un décalage dans le temps.
6. La production nucléaire est peu sensible à la météo, sauf lors des canicules
   (limitation à cause de la température des cours d'eau).

## Périmètre et justification
- Échelle : régionale, parce que les régions ne sont pas exposées de la même manière
  au climat (climat méditerranéen au Sud, plus continental au Nord-Est) et n'ont pas
  le même parc de production (solaire plus présent au Sud, éolien au Nord).
- Période : de 2020 à [2025 / 2026].
  - 2020 est à étudier à part : les confinements et la hausse des arrêts de travail
    ont entraîné une consommation électrique inhabituelle.
  - 2022 est aussi atypique : crise énergétique, hausse des prix, appels à la sobriété,
    et une partie du parc nucléaire à l'arrêt.
  - La période après le Covid est intéressante : le télétravail a pu déplacer
    une partie de la consommation des bureaux vers les logements, et le développement
    du numérique (dont l'IA) pourrait faire évoluer la demande. [À vérifier avec des sources.]
- Pas de temps : [demi-heure, puis agrégation à l'heure pour la fusion avec la météo ?]
- Saisons : convention météorologique (décembre-janvier-février = hiver, etc.),
  parce que [simple à coder, saisons de même durée, correspond aux mois les plus froids
  et les plus chauds].
