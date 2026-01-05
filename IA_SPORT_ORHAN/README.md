# Analyse Automatique de Tactiques de Handball (IA & Sport)

[cite_start]Ce projet a été réalisé dans le cadre du Master Informatique (module IA & Sport). [cite_start]Il vise à identifier automatiquement des schémas tactiques complexes (Yugo, Yago, Espagnole, etc.) à partir de données de tracking de joueurs de handball, en utilisant une approche hybride mêlant règles géométriques et alignement temporel[cite: 2, 5].

## 📋 Objectifs

[cite_start]L'objectif principal est de détecter des tactiques connues à l'avance en analysant[cite: 5]:
* Les **positions des joueurs** (attaquants et défenseurs).
* La **géométrie des actions** (intervalles, croisements).
* [cite_start]La **temporalité** des séquences via l'algorithme DTW (Dynamic Time Warping)[cite: 17].

## 🛠️ Méthodologie Technique

Le programme (`hand_tactics2.py`) implémente les concepts suivants :

1.  [cite_start]**Modélisation des Tactiques** : Chaque tactique est définie par une séquence d'étapes comportant des conditions de proximité, de position absolue sur le terrain et de détection d'intervalles[cite: 7].
2.  [cite_start]**Alignement Temporel (DTW)** : Utilisation de la bibliothèque `tslearn` pour calculer la similarité entre les mouvements réels des joueurs clés et un modèle théorique de distance[cite: 18].
3.  [cite_start]**Validation Hybride** : Une tactique est validée si elle respecte les étapes géométriques (ex: croisé, bloc) et si le score DTW est cohérent[cite: 24].

## 📊 Résultats Principaux : France vs République Tchèque

L'analyse a été menée sur **70 séquences d'attaque** de l'équipe de France. Voici la synthèse des performances par famille tactique détectée (données issues de l'exécution du script) :

| Famille Tactique | Nb Séquences | % Efficacité Tactique* | % Efficacité But** | Qualité DTW Moyenne |
| :--- | :---: | :---: | :---: | :---: |
| **Yugo** (Droit/Gauche) | 13 | 38.5% | 23.1% | 7001.7 |
| **Yago** | 5 | 60.0% | 40.0% | 6278.6 |
| **Espagnole_Ailier** | 4 | 50.0% | 50.0% | 11846.9 |
| **Entree_ALG_2Pivots** | 6 | 16.7% | 0.0% | 8004.2 |

> **Notes :**
> * ***% Eff. Tactique** : Pourcentage de séquences aboutissant à une situation favorable (But, Penalty, Exclusion, Faute).
> * ***% Eff. But** : Pourcentage de séquences aboutissant réellement à un but marqué.

### Observations
* La tactique **Yago** semble être la plus efficace sur ce match (60% de réussite tactique et le meilleur score DTW moyen, indiquant une exécution très propre).
* La **Yugo** est la tactique la plus fréquemment détectée (13 occurrences) mais avec une efficacité moindre face à la défense adverse.
* L'**Entrée d'Ailier en 2e Pivot** a été tentée 6 fois mais n'a abouti à aucun but lors des séquences détectées.

## 🚀 Installation et Utilisation

### Prérequis
IMPORTANT : il faut télécharger le dossier data_handball qui est trop lourd pour le dépôt git
Le projet nécessite **Python 3.x** et les bibliothèques suivantes (voir `hand_tactics2.py`) :
* `numpy`
* `pandas`
* [cite_start]`tslearn` (pour le calcul DTW) [cite: 18]

```bash
pip install numpy pandas tslearn

python3 hand_tactics2.py

python3 visualisation.py
