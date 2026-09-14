"""
Dashboard Marketing & Segmentation Client
Projet Segmentation Client & Marketing IA

Ce dashboard lit uniquement des données déjà transformées (jamais les CSV bruts) :
- segments_clients.csv   (M3/M4 - segmentation)
- marketing_kpis.csv     (M5 - performances campagnes)
- strategie_segments.csv (M7 - stratégie par segment)
- churn_model.pkl + predictions_churn.csv (M6 - prédiction churn)
"""

import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
from pathlib import Path

# ============================================================
# CONFIGURATION GÉNÉRALE
# ============================================================
st.set_page_config(
    page_title="Dashboard Marketing IA",
    page_icon="📊",
    layout="wide",
)

DATA_DIR = Path(__file__).parent.parent / "data/processed"
print(f"DATA_DIR = {DATA_DIR.resolve()}")
MODELS_DIR = Path(__file__).parent.parent / "models"
print(f"MODELS_DIR = {MODELS_DIR.resolve()}")

PRIMARY_COLOR = "#2E5C9A"
ACCENT_COLOR = "#C0623D"
PALETTE = ["#2E5C9A", "#C0623D", "#3F8F6B", "#8F6BAE", "#B9A23C"]


# ============================================================
# CHARGEMENT DES DONNÉES (mis en cache pour éviter de recharger
# les fichiers à chaque interaction utilisateur)
# ============================================================
@st.cache_data
def load_segments():
    return pd.read_csv(DATA_DIR / "segments_clients.csv")


@st.cache_data
def load_marketing():
    return pd.read_csv(DATA_DIR / "marketing_kpis.csv")


@st.cache_data
def load_marketing_by_channel():
    return pd.read_csv(DATA_DIR / "marketing_kpis_by_channel.csv")


@st.cache_data
def load_strategie():
    return pd.read_csv(DATA_DIR / "strategie_segments.csv")


@st.cache_data
def load_predictions():
    return pd.read_csv(DATA_DIR / "predictions_churn.csv")


@st.cache_resource
def load_churn_model():
    return joblib.load(MODELS_DIR / "logistic_churn.pkl")


def safe_load(loader, label):
    """Charge un fichier avec gestion d'erreur claire plutôt qu'un crash brut."""
    try:
        return loader()
    except FileNotFoundError:
        st.error(
            f"⚠️ Fichier manquant pour « {label} ». "
            f"Vérifie que les fichiers sont bien dans `dashboard/data/` ou `dashboard/models/`."
        )
        return None
    except Exception as e:
        st.error(f"⚠️ Erreur lors du chargement de « {label} » : {e}")
        return None


segments_df = safe_load(load_segments, "segments clients")
marketing_df = safe_load(load_marketing, "KPIs marketing")
by_channel_df = safe_load(load_marketing_by_channel, "KPIs par canal")
strategie_df = safe_load(load_strategie, "stratégie par segment")
predictions_df = safe_load(load_predictions, "prédictions de churn")
churn_model = safe_load(load_churn_model, "modèle de churn")


# ============================================================
# EN-TÊTE
# ============================================================
st.title("📊 Dashboard Marketing & Segmentation Client")
st.caption(
    "Projet Segmentation Client & Marketing IA — "
    "⚠️ données simulées à des fins de démonstration (le dataset réel fourni contient un "
    "volume insuffisant pour un clustering statistique)."
)

# ============================================================
# NAVIGATION PAR ONGLETS
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs(
    ["🏠 Vue d'ensemble", "🧩 Segmentation", "📈 Marketing", "⚠️ Prédiction churn"]
)

# ------------------------------------------------------------
# TAB 1 — VUE D'ENSEMBLE
# ------------------------------------------------------------
with tab1:
    st.subheader("Indicateurs clés")

    if segments_df is not None and marketing_df is not None:
        total_clients = segments_df["Customer_ID"].nunique()
        total_revenue = segments_df["monetary_total"].sum()
        avg_basket = segments_df["avg_basket_value"].mean()
        avg_conversion = marketing_df["Conversion_Rate"].mean() * 100

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Clients totaux", f"{total_clients:,}")
        col2.metric("Chiffre d'affaires total", f"{total_revenue:,.0f} €")
        col3.metric("Panier moyen", f"{avg_basket:,.2f} €")
        col4.metric("Taux de conversion moyen", f"{avg_conversion:.1f} %")

        st.divider()

        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("**Répartition des clients par segment**")
            cluster_counts = segments_df["cluster"].value_counts().sort_index()
            fig = px.pie(
                names=[f"Segment {c}" for c in cluster_counts.index],
                values=cluster_counts.values,
                color_discrete_sequence=PALETTE,
                hole=0.4,
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_right:
            st.markdown("**ROI moyen par canal marketing**")
            if by_channel_df is not None:
                fig = px.bar(
                    by_channel_df.sort_values("Avg_ROI_Percent", ascending=False),
                    x="Channel", y="Avg_ROI_Percent",
                    color="Channel", color_discrete_sequence=PALETTE,
                    labels={"Avg_ROI_Percent": "ROI moyen (%)", "Channel": "Canal"},
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Charge les données pour afficher les indicateurs.")

# ------------------------------------------------------------
# TAB 2 — SEGMENTATION
# ------------------------------------------------------------
with tab2:
    st.subheader("Segmentation client (M3 / M4)")

    if segments_df is not None:
        clusters_disponibles = sorted(segments_df["cluster"].unique())
        selected_clusters = st.multiselect(
            "Filtrer par segment",
            options=clusters_disponibles,
            default=clusters_disponibles,
            format_func=lambda c: f"Segment {c}",
        )

        filtered = segments_df[segments_df["cluster"].isin(selected_clusters)]

        col_left, col_right = st.columns([2, 1])

        with col_left:
            st.markdown("**Positionnement des clients (Fréquence vs Montant total)**")
            fig = px.scatter(
                filtered,
                x="purchase_frequency", y="monetary_total",
                color=filtered["cluster"].astype(str),
                hover_data=["Customer_ID", "Age", "recency_days"],
                labels={
                    "purchase_frequency": "Fréquence d'achat",
                    "monetary_total": "Montant total dépensé (€)",
                    "color": "Segment",
                },
                color_discrete_sequence=PALETTE,
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_right:
            st.markdown("**Taille des segments filtrés**")
            st.dataframe(
                filtered["cluster"].value_counts().sort_index().rename("Nb clients"),
                use_container_width=True,
            )

        st.divider()
        st.markdown("**Profils moyens par segment**")
        profile_cols = ["Age", "recency_days", "purchase_frequency", "monetary_total", "avg_basket_value"]
        profile_cols = [c for c in profile_cols if c in segments_df.columns]
        profile = segments_df.groupby("cluster")[profile_cols].mean().round(1)
        st.dataframe(profile, use_container_width=True)

        if strategie_df is not None:
            st.divider()
            st.markdown("**Personas et stratégie associée (M7)**")
            st.dataframe(
                strategie_df[["Cluster", "Persona", "Nb_clients", "Canal_prioritaire", "Message_recommande"]],
                use_container_width=True,
                hide_index=True,
            )
    else:
        st.info("Charge `segments_clients.csv` pour afficher la segmentation.")

# ------------------------------------------------------------
# TAB 3 — MARKETING
# ------------------------------------------------------------
with tab3:
    st.subheader("Performances des campagnes marketing (M5 / M7)")

    if marketing_df is not None:
        channels_disponibles = sorted(marketing_df["Channel"].unique())
        selected_channels = st.multiselect(
            "Filtrer par canal", options=channels_disponibles, default=channels_disponibles
        )

        filtered_mkt = marketing_df[marketing_df["Channel"].isin(selected_channels)]

        col1, col2, col3 = st.columns(3)
        col1.metric("Budget total", f"{filtered_mkt['Budget'].sum():,.0f} €")
        col2.metric("Conversions totales", f"{filtered_mkt['Conversions'].sum():,}")
        col3.metric("ROI moyen", f"{filtered_mkt['ROI_Percent'].mean():.1f} %")

        st.divider()

        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("**CPA moyen par canal**")
            if by_channel_df is not None:
                fig = px.bar(
                    by_channel_df, x="Channel", y="Avg_CPA",
                    color="Channel", color_discrete_sequence=PALETTE,
                    labels={"Avg_CPA": "CPA moyen (€)", "Channel": "Canal"},
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

        with col_right:
            st.markdown("**Taux de conversion moyen par canal**")
            if by_channel_df is not None:
                fig = px.bar(
                    by_channel_df, x="Channel", y="Avg_Conversion_Rate",
                    color="Channel", color_discrete_sequence=PALETTE,
                    labels={"Avg_Conversion_Rate": "Taux de conversion moyen", "Channel": "Canal"},
                )
                fig.update_layout(showlegend=False, yaxis_tickformat=".0%")
                st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.markdown("**Détail des campagnes**")
        st.dataframe(
            filtered_mkt.sort_values("ROI_Percent", ascending=False),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Charge `marketing_kpis.csv` pour afficher les performances marketing.")

# ------------------------------------------------------------
# TAB 4 — PRÉDICTION CHURN
# ------------------------------------------------------------
with tab4:
    st.subheader("Prédiction de churn (M6)")

    if predictions_df is not None:
        risk_options = predictions_df["risk_level"].unique().tolist()
        selected_risk = st.multiselect(
            "Filtrer par niveau de risque", options=risk_options, default=risk_options
        )

        filtered_pred = predictions_df[predictions_df["risk_level"].isin(selected_risk)]

        col1, col2, col3 = st.columns(3)
        col1.metric("Clients analysés", f"{len(filtered_pred):,}")
        col2.metric(
            "Clients à risque élevé",
            f"{(filtered_pred['risk_level'] == 'Élevé').sum():,}",
        )
        col3.metric(
            "Probabilité moyenne de churn",
            f"{filtered_pred['churn_probability'].mean() * 100:.1f} %",
        )

        st.divider()
        st.markdown("**Distribution des probabilités de churn**")
        fig = px.histogram(
            filtered_pred, x="churn_probability", nbins=20,
            color_discrete_sequence=[PRIMARY_COLOR],
            labels={"churn_probability": "Probabilité de churn"},
        )
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.markdown("**Clients à surveiller en priorité**")
        st.dataframe(
            filtered_pred.sort_values("churn_probability", ascending=False)[
                ["Customer_ID", "Name", "cluster", "purchase_frequency",
                 "monetary_total", "churn_probability", "risk_level"]
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Charge `predictions_churn.csv` pour afficher les prédictions de churn.")

# ============================================================
# PIED DE PAGE
# ============================================================
st.divider()
st.caption(
    "Dashboard généré pour le projet pédagogique Segmentation Client & Marketing IA — "
    "données de démonstration, dernière mise à jour du pipeline : voir le rapport final (M9)."
)