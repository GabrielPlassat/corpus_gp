"""
STREAMLIT — Visualisation 3D du corpus Gabriel Plassat
=======================================================
Usage :
  1. Placer ce fichier (app.py) dans un dossier avec articles_3d.json
  2. streamlit run app.py
     OU déployer sur https://share.streamlit.io

Dépendances :
  pip install streamlit plotly pandas
"""

import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ── Configuration de la page ─────────────────────────────────────────────────

st.set_page_config(
    page_title="Corpus Gabriel Plassat — 25 ans de production intellectuelle",
    page_icon="🗺️",
    layout="wide",
)

# ── Chargement des données ────────────────────────────────────────────────────

@st.cache_data
def load_data():
    with open("articles_3d.json", encoding="utf-8") as f:
        records = json.load(f)
    df = pd.DataFrame(records)
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("❌ Fichier 'articles_3d.json' introuvable. Lancer d'abord le script Colab.")
    st.stop()

# ── Sidebar : filtres ─────────────────────────────────────────────────────────

st.sidebar.title("Filtres")

sources_all = sorted(df["source"].unique().tolist())
sources_sel = st.sidebar.multiselect(
    "Sources",
    options=sources_all,
    default=sources_all,
)

clusters_all = sorted(df["cluster_label"].unique().tolist())
clusters_sel = st.sidebar.multiselect(
    "Thèmes",
    options=clusters_all,
    default=clusters_all,
)

year_min = int(df["year"].min())
year_max = int(df["year"].max())
year_range = st.sidebar.slider(
    "Période",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max),
)

search_q = st.sidebar.text_input("Rechercher dans les titres", "")

# ── Filtrage ──────────────────────────────────────────────────────────────────

mask = (
    df["source"].isin(sources_sel) &
    df["cluster_label"].isin(clusters_sel) &
    df["year"].between(year_range[0], year_range[1])
)
if search_q:
    mask &= df["title"].str.contains(search_q, case=False, na=False)

df_f = df[mask]

# ── En-tête ───────────────────────────────────────────────────────────────────

col_h1, col_h2, col_h3, col_h4 = st.columns(4)
col_h1.metric("Articles affichés", len(df_f))
col_h2.metric("Total corpus", len(df))
col_h3.metric("Sources", df_f["source"].nunique())
col_h4.metric("Thèmes", df_f["cluster_label"].nunique())

st.markdown("---")

# ── Titre + description ───────────────────────────────────────────────────────

st.markdown(
    """
    ## Carte 3D du corpus — Gabriel Plassat (2000 – 2026)

    **Axes :**
    - **X → Temps** (année de publication)
    - **Y → Abstraction** (0 = terrain/opérationnel · 10 = théorique/prospectif)
    - **Z → Thème** (cluster calculé par TF-IDF + KMeans)

    *Tourner, zoomer, survoler un point pour voir le titre. Cliquer ouvre l'article.*
    """
)

# ── Mode couleur : source ou thème ───────────────────────────────────────────

color_mode = st.radio(
    "Colorier par :",
    ["Thème (cluster)", "Source"],
    horizontal=True,
)

# ── Construction du graphe 3D ─────────────────────────────────────────────────

COLOR_SOURCE = {
    "TDF":             "#185FA5",
    "XD":              "#BA7517",
    "FabMob":          "#1D9E75",
    "MetaNote/Article":"#D85A30",
    "PDF/Papier":      "#7F77DD",
}

def build_figure(df_plot, color_mode):
    fig = go.Figure()

    if color_mode == "Source":
        groups = df_plot.groupby("source")
        for source, grp in groups:
            color = COLOR_SOURCE.get(source, "#888780")
            hover = [
                f"<b>{row.title[:70]}</b><br>"
                f"📅 {row.date[:7]}  |  🏷 {row.cluster_label}<br>"
                f"📂 {row.source}"
                for _, row in grp.iterrows()
            ]
            fig.add_trace(go.Scatter3d(
                x=grp["x"], y=grp["y"], z=grp["z"],
                mode="markers",
                name=source,
                marker=dict(
                    size=grp["size"].clip(3, 16),
                    color=color,
                    opacity=0.72,
                    line=dict(width=0),
                ),
                text=hover,
                hovertemplate="%{text}<extra></extra>",
                customdata=grp["url"].tolist(),
            ))

    else:  # Thème
        groups = df_plot.groupby("cluster_label")
        for label, grp in groups:
            color = grp["color"].iloc[0]
            hover = [
                f"<b>{row.title[:70]}</b><br>"
                f"📅 {row.date[:7]}  |  📂 {row.source}<br>"
                f"🏷 {row.cluster_label}"
                for _, row in grp.iterrows()
            ]
            fig.add_trace(go.Scatter3d(
                x=grp["x"], y=grp["y"], z=grp["z"],
                mode="markers",
                name=label,
                marker=dict(
                    size=grp["size"].clip(3, 16),
                    color=color,
                    opacity=0.72,
                    line=dict(width=0),
                ),
                text=hover,
                hovertemplate="%{text}<extra></extra>",
                customdata=grp["url"].tolist(),
            ))

    fig.update_layout(
        height=680,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        scene=dict(
            xaxis=dict(
                title="Temps →",
                tickvals=[i * 10 / (2026 - 2000) for i in range(0, 27, 5)],
                ticktext=[str(2000 + i * 5) for i in range(0, 6)],
                backgroundcolor="rgba(0,0,0,0)",
                gridcolor="rgba(128,128,128,0.15)",
                showbackground=True,
            ),
            yaxis=dict(
                title="Abstraction →",
                tickvals=[0, 2.5, 5, 7.5, 10],
                ticktext=["Terrain", "", "Mixte", "", "Théorique"],
                backgroundcolor="rgba(0,0,0,0)",
                gridcolor="rgba(128,128,128,0.15)",
                showbackground=True,
            ),
            zaxis=dict(
                title="Thème →",
                backgroundcolor="rgba(0,0,0,0)",
                gridcolor="rgba(128,128,128,0.15)",
                showbackground=True,
            ),
            camera=dict(eye=dict(x=1.5, y=1.5, z=0.8)),
        ),
        legend=dict(
            x=0.01, y=0.99,
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="rgba(0,0,0,0.1)",
            borderwidth=1,
            font=dict(size=12),
        ),
        uirevision="stable",   # conserve la rotation entre re-renders
    )
    return fig

fig = build_figure(df_f, color_mode)
st.plotly_chart(fig, use_container_width=True)

# ── Note sur les URL cliquables ───────────────────────────────────────────────

st.caption(
    "💡 Survolez un point pour voir le titre et la source. "
    "Les axes X et Z sont normalisés (0–10). "
    "La taille des points est proportionnelle à la longueur du texte."
)

# ── Tableau des articles filtrés ──────────────────────────────────────────────

st.markdown("---")
with st.expander(f"📋 Liste des articles filtrés ({len(df_f)})", expanded=False):
    display_cols = ["title", "date", "source", "cluster_label", "year"]
    display_cols = [c for c in display_cols if c in df_f.columns]
    st.dataframe(
        df_f[display_cols].sort_values("date", ascending=False),
        use_container_width=True,
        height=400,
    )

# ── Statistiques rapides ──────────────────────────────────────────────────────

st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Répartition par thème")
    theme_counts = df_f.groupby("cluster_label").size().sort_values(ascending=True)
    st.bar_chart(theme_counts)

with col2:
    st.markdown("#### Production par année")
    year_counts = df_f.groupby("year").size()
    st.bar_chart(year_counts)

# ── Footer ────────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    "<small>Corpus Gabriel Plassat · transportsdufutur.ademe.fr · xd.ademe.fr · fabmob.io · 2000–2026</small>",
    unsafe_allow_html=True,
)
