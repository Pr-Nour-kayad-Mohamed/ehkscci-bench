[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23922885.svg)](https://doi.org/10.5281/zenodo.23922885)

# EHK-SCCI Bench

Prototype Python de recherche pour l’évaluation d’un indice
géométrico-spectral sur des graphes.

Code source : https://github.com/Pr-Nour-kayad-Mohamed/ehkscci-bench

## Objectif

Explorer un diagnostic combinant :

- les écarts de courbure d’Ollivier–Ricci ;
- la diminution du gap du Laplacien normalisé ;
- l’excès d’énergie spectrale haute fréquence.

## Contenu

- Code Python du prototype dans `src/ehkscci/`.
- Tests unitaires dans `tests/`.
- Exécution automatique des tests avec GitHub Actions.

## Prérequis

Python 3.11 ou version ultérieure.

## Installation

Depuis le dossier contenant `pyproject.toml` :

    python -m pip install -e ".[dev]"

## Exécuter les tests

    python -m pytest -v

## Campagnes synthétiques

    ehkscci --help
    ehkscci sweep --n 24 --out results/sweep
    ehkscci noise --n 16 --repeats 12 --out results/noise
    ehkscci cv --n 16 --windows 12 --folds 3 --out results/cv

## Dépôt scientifique associé

https://doi.org/10.5281/zenodo.23907426

Les documents associés peuvent correspondre à différentes campagnes
exploratoires. Leur reproduction exacte par cette version du logiciel
n’est pas établie.

## Citer ce travail

Le logiciel est archivé sur Zenodo : le DOI affiché en tête de ce
document identifie l’archive. Les métadonnées de citation sont
également fournies dans le fichier `CITATION.cff`.

Pour citer une version précise, utilisez le DOI de version indiqué
sur la page Zenodo correspondante.

## Statut et limites

Prototype exploratoire utilisant des paramètres et des échelles
illustratifs. Les tests unitaires vérifient certains comportements
du logiciel ; ils ne constituent pas une validation scientifique.

Aucune garantie de sûreté, d’exactitude numérique ou de robustesse
sur des données réelles n’est revendiquée. Les résultats produits ne
constituent pas une validation empirique de l’indice.

## Auteur

Mohamed Nour Kayad

## Licence

Apache License 2.0 — voir le fichier `LICENSE` et le fichier `NOTICE`.

Copyright 2026 Mohamed Nour Kayad.
