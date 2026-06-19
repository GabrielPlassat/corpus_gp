# Visualisation 3D du corpus — Gabriel Plassat
## Guide d'utilisation pas à pas

---

## Structure du dossier Google Drive

Créer ce dossier dans **Mon Drive** :

```
Mon Drive/
└── corpus_gabriel/
    ├── articles_md/        ← TOUS les .md (TDF + XD + FabMob + autres)
    ├── articles_docx/      ← MetaNotes et articles Word
    └── papiers_pdf/        ← mémoire IMT, papiers, synthèses
```

### Que mettre dans articles_md/ ?

Tous les fichiers .md, quelle que soit leur origine :
- Articles du blog TDF exportés en .md
- Articles du blog XD (xd.ademe.fr)
- Articles FabMob
- Articles divers

**Le script détecte automatiquement la source** (TDF / XD / FabMob)
en lisant l'URL dans le front matter ou dans le contenu du fichier.
Pas besoin de les trier dans des sous-dossiers.

### Formats de fichier .md reconnus

Le script gère deux formats de front matter :

**Format XD/simple :**
```yaml
---
source: https://xd.ademe.fr/blog/nom-article
date: 2023-10-24
tags: tag1, tag2
---
Contenu de l'article...
```

**Format FabMob/TDF :**
```yaml
---
title: "Titre de l'article"
date: "2019-09-05T10:31:36.000Z"
categories:
  - innovation
tags:
author: "Gabriel Plassat"
---
Contenu de l'article...
```

Les deux fonctionnent sans modification.

---

## Étape 1 — Monter Google Drive dans Colab

```python
from google.colab import drive
drive.mount('/content/drive')
```

Après cette cellule, ton Drive est accessible à `/content/drive/MyDrive/`.

---

## Étape 2 — Adapter le chemin (une seule ligne)

Dans le script, Cellule 3 :

```python
# Changer uniquement le nom du dossier si différent de corpus_gabriel
BASE_PATH = "/content/drive/MyDrive/corpus_gabriel/"
```

Si tu appelles ton dossier autrement, par exemple `plassat_2026` :
```python
BASE_PATH = "/content/drive/MyDrive/plassat_2026/"
```

C'est la **seule modification nécessaire**.

---

## Étape 3 — Installer les dépendances (Cellule 1)

```python
!pip install scikit-learn python-docx PyMuPDF pandas plotly -q
```

---

## Étape 4 — Vérifier que Colab voit tes fichiers

Avant de lancer le script complet, tester avec cette mini-cellule :

```python
import os
BASE_PATH = "/content/drive/MyDrive/corpus_gabriel/"

print("articles_md/ :")
files = os.listdir(BASE_PATH + "articles_md/")
print(f"  {len(files)} fichiers")
for f in files[:5]:
    print(f"  · {f}")
```

Si tu vois la liste → OK, lancer le script complet.
Si erreur FileNotFoundError → vérifier l'orthographe du dossier.

---

## Étape 5 — Lancer et télécharger le JSON

Exécuter toutes les cellules dans l'ordre.

À la fin, télécharger le fichier produit :

```python
from google.colab import files
files.download("articles_3d.json")
```

**Durée estimée** : 3-8 minutes selon le volume.

---

## Étape 6 — Lancer l'app Streamlit

**Option A — Streamlit Cloud (recommandé, sans installation)**

1. Créer un repo GitHub avec 3 fichiers :
   - `app_streamlit_3d.py`
   - `articles_3d.json`
   - `requirements.txt` (voir ci-dessous)
2. Aller sur https://share.streamlit.io → connecter le repo → déployer

`requirements.txt` :
```
streamlit>=1.28
plotly>=5.17
pandas>=2.0
```

**Option B — En local**
```bash
pip install streamlit plotly pandas
streamlit run app_streamlit_3d.py
```

---

## Ajuster les labels des clusters

Après le premier lancement, la Cellule 9 affiche 6 titres par cluster.
Vérifier que les labels correspondent, et si besoin les corriger dans
la Cellule 3 avant de relancer :

```python
CLUSTER_LABELS = {
    0: "Communs & open source",       # ajuster si KMeans a fait autrement
    1: "Transition & wicked problems",
    2: "Véhicules intermédiaires / XD",
    3: "Numérique & IA",
    4: "Écosystèmes d'innovation",
    5: "Automobile & industrie",
    6: "Territoires & politique",
    7: "Fiction & prospective",
}
```

---

## Ajouter des documents de synthèse

À tout moment, déposer un nouveau fichier dans :
- `articles_md/` si c'est un .md
- `articles_docx/` si c'est un .docx
- `papiers_pdf/` si c'est un .pdf

Relancer le script Colab → nouveau `articles_3d.json` → Streamlit se met à jour.

---

## Ressources
- Colab : https://colab.research.google.com
- Streamlit Cloud : https://share.streamlit.io
- GitHub : https://github.com
