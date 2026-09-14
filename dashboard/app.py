import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import base64
from pathlib import Path
from datetime import datetime, timedelta

ICONS = {
    "logo": '<svg viewBox="0 0 24 24" fill="currentColor"><rect x="3" y="3" width="8" height="8" rx="1.5"/><rect x="13" y="3" width="8" height="5" rx="1.5"/><rect x="13" y="10" width="8" height="11" rx="1.5"/><rect x="3" y="13" width="8" height="8" rx="1.5"/></svg>',
    "revenue": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v10M9.3 9.3c0-1.4 1.2-2 2.7-2s2.7.7 2.7 2-1.2 1.7-2.7 2c-1.5.3-2.7.8-2.7 2.2s1.2 2 2.7 2 2.7-.6 2.7-2"/></svg>',
    "customers": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="8" r="3.2"/><path d="M3.3 20c0-3.1 2.6-5.3 5.7-5.3s5.7 2.2 5.7 5.3"/><circle cx="17.3" cy="9" r="2.3"/><path d="M15.3 20c0-2.4 1.5-4.2 3.7-4.2"/></svg>',
    "roi": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4.7"/><circle cx="12" cy="12" r="0.7" fill="currentColor" stroke="none"/></svg>',
    "churn": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3.5 21 19.5H3z"/><path d="M12 9.5v5"/><circle cx="12" cy="17" r="0.7" fill="currentColor" stroke="none"/></svg>',
    "tab_sales": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20V10M9.5 20V6M15 20v-8M20 20V3"/></svg>',
    "tab_campaigns": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 10v4h3l6 4V6l-6 4z"/><path d="M15 9a4 4 0 0 1 0 6"/><path d="M18 7a7 7 0 0 1 0 10"/></svg>',
    "tab_clusters": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="6" r="2.3"/><circle cx="18" cy="6" r="2.3"/><circle cx="6" cy="18" r="2.3"/><circle cx="18" cy="18" r="2.3"/><circle cx="12" cy="12" r="2.6" fill="currentColor" stroke="none"/><path d="M8 7.5 10.4 10.4M16 7.5 13.6 10.4M8 16.5 10.4 13.6M16 16.5 13.6 13.6"/></svg>',
    "tab_ai": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="7" y="7" width="10" height="10" rx="1.5"/><path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6 8 8M16 16l2.4 2.4M18.4 5.6 16 8M8 16l-2.4 2.4"/></svg>',
    "download": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4v11"/><path d="M7 11l5 5 5-5"/><path d="M4 20h16"/></svg>',
}

def svg_icon(name, size=20, color="#2E5C9A"):

    return f'<span style="display:inline-flex;color:{color};width:{size}px;height:{size}px;vertical-align:middle;">{ICONS[name]}</span>'


def format_ar(value):
    return f"{value:,.2f} Ar"


def svg_favicon(name, color="#6ECFF6"):

    svg = ICONS[name].replace("currentColor", color)
    if not svg.startswith("<svg xmlns"):
        svg = svg.replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{b64}"


def section_title(text, icon_name, size=17, icon_size=15):
   
    st.markdown(
        f'<div class="section-title">'
        f'<span class="section-title-icon">{svg_icon(icon_name, icon_size)}</span>'
        f'<span style="font-size:{size}px;">{text}</span></div>',
        unsafe_allow_html=True
    )



def style_chart(fig, **layout_kwargs):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#111111', family='Inter, Segoe UI, sans-serif'),
        legend=dict(
            font=dict(color='#111111'),
            title_font=dict(color='#111111'),
            bgcolor='rgba(255,255,255,0.82)',
            bordercolor='#111111',
            borderwidth=1
        ),
        hoverlabel=dict(font=dict(color="#111111")),
        **layout_kwargs
    )
    fig.update_xaxes(
        gridcolor='#B8B8B8',
        zerolinecolor='#111111',
        linecolor='#111111',
        tickfont=dict(color='#111111'),
        title_font=dict(color='#111111')
    )
    fig.update_yaxes(
        gridcolor="#B8B8B8",
        zerolinecolor='#111111',
        linecolor='#111111',
        tickfont=dict(color='#111111'),
        title_font=dict(color='#111111')
    )
    return fig


# 1. PAGE CONFIGURATION & CUSTOM STYLING

st.set_page_config(
    page_title="AI Marketing Analytics Dashboard",
    page_icon=svg_favicon("logo"),
    layout="wide",
    initial_sidebar_state="expanded"
)

#THEME LIGHT SKY-BLUE COMBINE

CSS_THEME = """
<style>
    :root {
        --bg-page: #EEF0F4;
        --bg-card: #FFFFFF;
        --border-color: transparent;
        --accent: #8B5CF6;
        --accent-soft: rgba(139, 92, 246, 0.14);
        --warning: #F5A524;
        --warning-soft: rgba(245, 165, 36, 0.14);
        --text-main: #111111;
        --text-muted: #444444;
        --shadow-sm: 0 1px 2px rgba(18, 92, 124, 0.14), 0 1px 3px rgba(139, 92, 246, 0.18);
        --shadow-md: 0 6px 14px rgba(18, 92, 124, 0.16), 0 2px 6px rgba(139, 92, 246, 0.22);
    }
 
    /* Fond et typographie globale */
 
    .stApp {
        background-color: var(--bg-page);
        color: var(--text-main);
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    h1, h2, h3, h4, .stMarkdown p { font-family: 'Inter', 'Segoe UI', sans-serif; }

    header[data-testid="stHeader"] {
    background: transparent;
    box-shadow: none;
    }
    div[data-testid="stToolbar"] {
        right: 1rem;
    }

 
    /* Réduit l'espace mort en haut de page */
    .block-container { padding-top: 1.6rem; padding-bottom: 2rem; }
 
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #230B62 !important;
        border-right: 1px solid transparent;
    }
    section[data-testid="stSidebar"] .block-container { padding-top: 1.6rem; }
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .brand-name,
    section[data-testid="stSidebar"] .brand-sub,
    section[data-testid="stSidebar"] .section-title {
        color: #F8F4FF !important;
    }
    section[data-testid="stSidebar"] .stRadio,
    section[data-testid="stSidebar"] .stSelectbox,
    section[data-testid="stSidebar"] .stMultiSelect {
        color: #F8F4FF !important;
    }
    section[data-testid="stSidebar"] hr { border-color: transparent; margin: 1.1rem 0; }
    .main hr { border-color: transparent; margin: 1.5rem 0; }

    section[data-testid="stSidebar"] .block-container {
        background: rgba(139, 92, 246, 0.08);
        border-radius: 16px;
    }

    /* État normal */
    section[data-testid="stSidebar"] div[data-testid="stButton"] button {
        background: rgba(255, 255, 255, 0.01) !important;
        color: #E9E7FF !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        box-shadow: none !important;
        transition: background 0.15s ease, border-color 0.15s ease;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button p,
    section[data-testid="stSidebar"] div[data-testid="stButton"] button span,
    section[data-testid="stSidebar"] div[data-testid="stButton"] button div {
        color: #E9E7FF !important;
    }

    /* État survol (hover) */
    section[data-testid="stSidebar"] div[data-testid="stButton"] button:hover {
        background: rgba(255, 255, 255, 0.14) !important;
        border-color: rgba(255, 255, 255, 0.14) !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button:hover span {
    section[data-testid="stSidebar"] div[data-testid="stButton"] button:hover p,
        color: #FFFFFF !important;
    }

    /* Neutralise le contour rouge par défaut de Streamlit au clic/focus */
    section[data-testid="stSidebar"] div[data-testid="stButton"] button:focus,
    section[data-testid="stSidebar"] div[data-testid="stButton"] button:active {
        box-shadow: none !important;
        outline: none !important;
        border-color: none !important;
    }

    /* État sélectionné (onglet actif, kind="primary") */
    section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"] {
        background: #4F46E5 !important;
        border: 1px solid #4F46E5 !important;
        box-shadow: 0 2px 8px rgba(79, 70, 229, 0.4) !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"] p,
    section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"] span {
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"]:hover {
        background: #6259EA !important;
        border-color: #6259EA !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button {
        justify-content: flex-start !important;
        text-align: left !important;
        padding-left: 1rem !important;
    }
 
    /* Étiquette "eyebrow" au-dessus des titres de filtre */
    .filter-label {
        font-size: 0.72rem;
        font-weight: 700;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin: 1rem 0 0.35rem 0;
    }
 
    /* En-tête principal */
    .header-bar {
        background: #230B62;
        border: 1px solid transparent;
        border-radius: 14px;
        padding: 1.5rem 1.8rem;
        margin-bottom: 1.4rem;
        box-shadow: var(--shadow-sm);
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .header-badge {
        width: 46px;
        height: 46px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    .header-title {
        font-size: 1.45rem;
        font-weight: 900;
        margin: 0;
        color: #F8F4FF;
        letter-spacing: -0.01em;
    }
    .header-subtitle {
        font-size: 0.88rem;
        color: #F8F4FF;
        margin-top: 0.2rem;
    }
 
    /* Cartes KPI */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #2E5C9A;
        border-radius: 10px;
        padding: 1.3rem 1.3rem 1.15rem 1.3rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
        transition: box-shadow 0.15s ease, transform 0.15s ease;
    }
    .kpi-card:hover {
        box-shadow: 0 4px 10px rgba(15, 23, 42, 0.10);
        transform: translateY(-1px);
    }

    .kpi-icon-wrap {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 0.85rem;
        background: #EFF4FA;
    }
    .kpi-icon-wrap.warning { }
    .kpi-card.warning-card {
        border-left-color: #C0623D;
    }
    .kpi-title {
        font-size: 0.74rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .kpi-value {
        font-size: 1.9rem;
        font-weight: 800;
        color: #0F172A;
        margin: 0.3rem 0 0.15rem 0;
        letter-spacing: -0.02em;
    }
    .kpi-sub {
        font-size: 0.78rem;
        font-weight: 600;
        color: #2E5C9A;
    }
 
    /* Navigation par boutons (remplace st.tabs) — même st.columns(4) que les cartes KPI,
       donc alignement garanti. Texte toujours noir, cliqué ou non. */
    div[data-testid="stButton"] button {
        height: 40px;
        border-radius: 8px;
        font-weight: 900;
        font-size: 0.95rem;
        border: 1px solid transparent;
        background: var(--bg-card);
        color: #000000 !important;
        width: 100%;
        white-space: nowrap;
    }
    div[data-testid="stButton"] button:hover {
        color: #000000 !important;
        border-color: #000000;
    }
    div[data-testid="stButton"] button:focus {
        color: #000000 !important;
        box-shadow: none;
    }
    div[data-testid="stButton"] button p,
    div[data-testid="stButton"] button span,
    div[data-testid="stButton"] button div {
        color: #000000 !important;
    }
    div[data-testid="stButton"] button[kind="primary"] {
        background: #EAEEB8 !important;
        box-shadow: var(--shadow-sm);
        border-color: #000000;
    }
 
    /* Cartes de contenu (autour des graphiques) */
    .content-card {
        background: #230B62;
        border: 1px solid transparent;
        border-radius: 14px;
        padding: 1.2rem 1.3rem 0.6rem 1.3rem;
        margin: 1rem 0;
        box-shadow: var(--shadow-sm);
    }
 
    /* Titres de section (icône + texte) */
    .section-title {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        font-weight: 700;
        color: var(--text-main);
        margin: 0 0 0.9rem 0;
    }
    .section-title-icon {
        width: 30px;
        height: 30px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }

    /* Logo de la sidebar */
    .brand-row {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        margin-bottom: 0.3rem;
    }
    .brand-badge {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .brand-name {
        font-weight: 800;
        color: var(--text-main);
        font-size: 1rem;
        letter-spacing: -0.01em;
    }
    .brand-sub {
        font-size: 0.72rem;
        color: var(--text-muted);
        margin-top: -0.15rem;
    }
 
    /* Widgets natifs Streamlit : coins plus doux, cohérents avec les cartes */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"],
    .stDateInput input {
        border-radius: 8px !important;
        border-color: transparent !important;
    }
    .stDataFrame {
        border: none !important;
        border-radius: 0 !important;
        overflow: hidden;
    }
    div[data-testid="stDataFrame"] {
       border: none !important;
       outline: none !important;
       box-shadow: none !important;
       border-radius: 0 !important;
    }   
    div[data-testid="stDataFrame"] .dataframe {
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }
    div[data-testid="stDataFrame"] table, 
    div[data-testid="stDataFrame"] th,
    div[data-testid="stDataFrame"] td {
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }
    .stDownloadButton button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
"""
st.markdown(CSS_THEME, unsafe_allow_html=True)



# DICTIONNAIRE DE DASHBOARD EN FR ET ENG

TEXTS = {
    'FR': {
        'title': "Tableau de Bord",
        'subtitle': "Analyse & Optimisation Marketing basée sur la Segmentation Client",
        'brand_name': "Application",
        'brand_sub': "Analyse & Optimisation Marketing basée sur la Segmentation Client",
        'lang_selector': "Langue / Language",
        'sidebar_filters': "Filtres d'Analyse",
        'date_range': "Période d'analyse",
        'segment_filter': "Segment Client",
        'product_filter': "Catégorie Produit",
        'channel_filter': "Canal Marketing",
        'all': "Tous",
        'tab1': "1. Ventes & Performance",
        'tab2': "2. Campagnes Marketing",
        'tab3': "3. Segmentation Client",
        'tab4': "4. IA Prédictive & Risk Churn",
        'kpi_revenue': "Chiffre d'Affaires Total",
        'kpi_customers': "Clients Actifs",
        'kpi_roi': "ROI Moyen Campagnes",
        'kpi_churn': "Taux de Churn Prédit",
        'kpi_transactions': "Nombre de Transactions",
        'kpi_avg_per_client': "CA Moyen par Client",
        'sales_pending': "Ventes détaillées",
        'feature_importance': "Importance des Variables du Modèle de Churn",
        'feature_importance_pending': "En attente du fichier d'importance des variables (ex. feature_importance.csv) livré par Jean Claude.",
        'budget_vs_conv': "Budget vs Conversions par Campagne",
        'conversion_rate': "Taux de Conversion",
        'sales_trend': "Évolution du Chiffre d'Affaires et Panier Moyen",
        'sales_by_cat': "Répartition des Ventes par Catégorie de Produits",
        'demo_dist': "Distribution Démographique des Clients",
        'funnel': "Entonnoir de Conversion des Campagnes",
        'channel_perf': "Comparatif ROI vs CPA/CPC par Canal Marketing",
        'campaign_table': "Détail des Performances par Campagne",
        'cluster_map': "Cartographie 2D des Clusters Clients",
        'cluster_dist': "Répartition de la Clientèle par Segment",
        'persona_details': "Profil & Fiche Persona du Segment Sélectionné",
        'churn_dist': "Distribution de la Probabilité d'Attrition Client",
        'clv_vs_churn': "Matrice Valeur à Vie (CLV) vs Risk Churn",
        'export_churn': "Exporter la Liste des Clients à Haut Risque",
        'download_btn': "Télécharger le Fichier",
        'notice_segmentation': "Segmentation",
        'notice_churn': "Scores de churn/CLV provisoires",
        'notice_roi': "ROI estimé à partir du panier moyen des ventes",
    },
    'EN': {
        'title': "Dashboard",
        'subtitle': "Marketing Analysis & Optimization Based on Customer Segmentation",
        'brand_name': "Application",
        'brand_sub': "Marketing Analysis & Optimization Based on Customer Segmentation",
        'lang_selector': "Language / Langue",
        'sidebar_filters': "Analysis Filters",
        'date_range': "Date Range",
        'segment_filter': "Customer Segment",
        'product_filter': "Product Category",
        'channel_filter': "Marketing Channel",
        'all': "All",
        'tab1': "1. Sales & Performance",
        'tab2': "2. Marketing Campaigns",
        'tab3': "3. Customer Segmentation",
        'tab4': "4. Predictive AI & Risk Churn",
        'kpi_revenue': "Total Revenue",
        'kpi_customers': "Active Customers",
        'kpi_roi': "Average Campaign ROI",
        'kpi_churn': "Predicted Churn Rate",
        'kpi_transactions': "Number of Transactions",
        'kpi_avg_per_client': "Average Revenue per Client",
        'sales_pending': "Detailed sales",
        'feature_importance': "Churn Model Feature Importance",
        'feature_importance_pending': "The feature importance",
        'budget_vs_conv': "Budget vs Conversions by Campaign",
        'conversion_rate': "Conversion Rate",
        'sales_trend': "Revenue Trend & Average Order Value",
        'sales_by_cat': "Sales Breakdown by Product Category",
        'demo_dist': "Customer Demographics",
        'funnel': "Campaign Conversion Funnel",
        'channel_perf': "ROI vs CPA/CPC Comparison by Marketing Channel",
        'campaign_table': "Detailed Campaign Performance Table",
        'cluster_map': "2D Customer Cluster Mapping",
        'cluster_dist': "Customer Distribution by Segment",
        'persona_details': "Persona Profile & Segment Characteristics",
        'churn_dist': "Customer Attrition Probability Distribution",
        'clv_vs_churn': "Customer Lifetime Value (CLV) vs Churn Risk Matrix",
        'export_churn': "Export High Churn Risk Customer",
        'download_btn': "Download CSV File",
        'notice_segmentation': "Segmentation",
        'notice_churn': "Churn/CLV scores",
        'notice_roi': "ROI estimated from average order value",
    }
}



# 3. CHARGEMENT DES VRAIES DONNÉES DU PROJET


PROJECT_ROOT = Path(__file__).resolve().parent.parent   
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"

SALES_FILE = DATA_RAW_DIR / "sales_data.csv"                         
PRODUCTS_FILE = DATA_RAW_DIR / "products_data.csv"                    
SEGMENTS_FILE = DATA_PROCESSED_DIR / "segments_clients.csv"                 
MARKETING_KPIS_FILE = DATA_PROCESSED_DIR / "marketing_kpis.csv"            
MARKETING_KPIS_CHANNEL_FILE = DATA_PROCESSED_DIR / "marketing_kpis_by_channel.csv" 
STRATEGY_FILE = DATA_PROCESSED_DIR / "strategie_segments.csv"               
PREDICTIONS_FILE = DATA_PROCESSED_DIR / "predictions.csv"                  
CHURN_MODEL_FILE = MODELS_DIR / "logistic_churn.pkl"                   
FEATURE_IMPORTANCE_FILE = DATA_PROCESSED_DIR / "feature_importance.csv"     


def _norm_cols(df):
    """Normalise les noms de colonnes reçus (Customer_ID, CUSTOMER_ID...) vers snake_case."""
    return df.rename(columns={c: c.strip().lower() for c in df.columns})


@st.cache_data
def load_and_generate_data():
    demo_notes = []

    customers_df = _norm_cols(pd.read_csv(SEGMENTS_FILE)).rename(columns={
        'recency_days': 'recency', 'purchase_frequency': 'frequency',
        'monetary_total': 'monetary', 'cluster': 'cluster_id',
    })
    customers_df['signup_date'] = pd.to_datetime(customers_df['join_date'])
    pca_df = customers_df[['customer_id', 'frequency', 'monetary']].rename(
        columns={'frequency': 'pca_x', 'monetary': 'pca_y'}
    )


    if STRATEGY_FILE.exists():
        strategy_df = _norm_cols(pd.read_csv(STRATEGY_FILE))
    
        # Normalisation du nom de la colonne cluster
        if 'cluster' not in strategy_df.columns:
            if 'cluster_id' in strategy_df.columns:
                strategy_df = strategy_df.rename(columns={'cluster_id': 'cluster'})
            else:
                raise KeyError(
                    f"Colonne 'cluster' introuvable dans strategie_segments.csv. "
                    f"Colonnes disponibles : {strategy_df.columns.tolist()}"
                )
    
        if 'persona' not in strategy_df.columns:
            raise KeyError(
                f"Colonne 'persona' introuvable dans strategie_segments.csv. "
                f"Colonnes disponibles : {strategy_df.columns.tolist()}"
            )
    
        persona_map = strategy_df.set_index('cluster')['persona'].to_dict()
    
        customers_df['cluster'] = customers_df['cluster_id'].map(
            lambda c: f"{c} - {persona_map.get(c, 'Segment ' + str(c))}"
        )
    else:
        strategy_df = None
        customers_df['cluster'] = 'Segment ' + customers_df['cluster_id'].astype(str)
    customers_raw_ids = customers_df.set_index('customer_id')['total_spent']


    if SALES_FILE.exists() and PRODUCTS_FILE.exists():
        products_raw = pd.read_csv(PRODUCTS_FILE)
        sales_raw = pd.read_csv(SALES_FILE)
        sales_df = sales_raw.merge(
            products_raw[['Product_ID', 'Category']], on='Product_ID', how='left'
        ).rename(columns={
            'Sale_ID': 'transaction_id', 'Customer_ID': 'customer_id', 'Date': 'date', 'Category': 'category',
        })
        sales_df['date'] = pd.to_datetime(sales_df['date'])
        sales_df['amount'] = (sales_df['Quantity'] * sales_df['Sale_Price']).round(2)
    else:
        sales_df = None
        demo_notes.append('sales')


    mkt_df = _norm_cols(pd.read_csv(MARKETING_KPIS_FILE)).rename(columns={
        'budget': 'spend', 'revenue_estimated': 'revenue',
        'roi_percent': 'roi', 'conversion_rate': 'taux_conversion',
    })
    mkt_df['campaign'] = 'Campagne_' + mkt_df['campaign_id'].astype(str)
    mkt_df['taux_conversion'] = (mkt_df['taux_conversion'] * 100).round(2)

    channel_kpis_df = _norm_cols(pd.read_csv(MARKETING_KPIS_CHANNEL_FILE)) if MARKETING_KPIS_CHANNEL_FILE.exists() else None


    if PREDICTIONS_FILE.exists():
        churn_df = _norm_cols(pd.read_csv(PREDICTIONS_FILE))
        # colonnes réelles : customer_id, name, churn_probability_final, clv, clv_score,
        # retention_priority, retention_priority_level, marketing_action

        risk_translation = {
            'priorité faible': 'Faible/Low',
            'priorité moyenne': 'Moyen/Medium',
            'priorité élevée': 'Élevé/High',
            'priorité très élevée': 'Élevé/High',
        }
        churn_df['churn_risk'] = (
            churn_df['retention_priority_level'].str.strip().str.lower().map(risk_translation)
        )

        predictive_df = customers_df[['customer_id', 'cluster']].merge(churn_df, on='customer_id', how='left')
        if pca_df is not None:
            predictive_df = predictive_df.merge(pca_df, on='customer_id', how='left')
    else:



        spent = customers_raw_ids
        spent_norm = 1 - (spent - spent.min()) / (spent.max() - spent.min() + 1e-9)
        predictive_df = customers_df[['customer_id', 'cluster']].copy()
        predictive_df['churn_probability_final'] = predictive_df['customer_id'].map(spent_norm).round(3)
        predictive_df['churn_risk'] = pd.cut(
            predictive_df['churn_probability_final'], bins=[-0.01, 0.35, 0.65, 1.0],
            labels=['Faible/Low', 'Moyen/Medium', 'Élevé/High']
        )
        predictive_df['clv'] = predictive_df['customer_id'].map(spent) * 2.5
        if pca_df is not None:
            predictive_df = predictive_df.merge(pca_df, on='customer_id', how='left')
        else:
            age_norm = (customers_df['age'] - customers_df['age'].mean()) / (customers_df['age'].std() + 1e-9)
            spent_z = (predictive_df['customer_id'].map(spent) - spent.mean()) / (spent.std() + 1e-9)
            predictive_df['pca_x'] = age_norm.values
            predictive_df['pca_y'] = spent_z.values
        demo_notes.append('churn')

    return customers_df, sales_df, mkt_df, predictive_df, strategy_df, channel_kpis_df, demo_notes

try:
    customers_df, sales_df, mkt_df, predictive_df, strategy_df, channel_kpis_df, demo_notes = load_and_generate_data()
except FileNotFoundError as e:
    st.error(
        f"Fichier de données introuvable : {e.filename}\n\n"
        f"Vérifie que segments_clients.csv et marketing_kpis.csv sont bien dans "
        f"data/processed à la racine du repo."
    )
    st.stop()






# 4. SIDEBAR & LANGUAGE TOGGLE

with st.sidebar:
    lang = st.radio("Language / Langue", options=['FR', 'EN'], horizontal=True)
    t = TEXTS[lang]
    
    st.markdown(
        f'<div class="section-title" style="margin-bottom:0.3rem;">'
        f'<span class="section-title-icon">{svg_icon("tab_clusters", 15)}</span>'
        f'<span style="font-size:15px;">{t["sidebar_filters"]}</span></div>',
        unsafe_allow_html=True
    )
        
    # Segment Filter
    segment_options = [t['all']] + list(customers_df['cluster'].unique())
    selected_segment = st.selectbox(t['segment_filter'], options=segment_options)
    
    # Channel Filter
    channel_options = [t['all']] + list(mkt_df['channel'].unique())
    selected_channel = st.selectbox(t['channel_filter'], options=channel_options)

    st.markdown(
        f'<div class="section-title" style="margin-bottom:0.3rem;">'
        f'<span class="section-title-icon">{svg_icon("tab_clusters", 15)}</span>'
        f'<span style="font-size:15px;">Actions</span></div>',
        unsafe_allow_html=True
    )

    def set_active_tab(tab_number):
        st.session_state.active_tab = tab_number

    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 1

    for i, label_key in enumerate(['tab1', 'tab2', 'tab3', 'tab4'], start=1):
        st.button(
            t[label_key],
            key=f"navtab_{i}",
            use_container_width=True,
            type="primary" if st.session_state.active_tab == i else "secondary",
            on_click=set_active_tab,
            args=(i,),
        )

    active_tab = st.session_state.active_tab

    st.markdown("---")
 
# Filter Data Logic
filtered_cust = customers_df.copy()
filtered_mkt = mkt_df.copy()
filtered_pred = predictive_df.copy()
filtered_sales = sales_df.copy() if sales_df is not None else None
 
if selected_segment != t['all']:
    filtered_cust = filtered_cust[filtered_cust['cluster'] == selected_segment]
    filtered_pred = filtered_pred[filtered_pred['cluster'] == selected_segment]
    if filtered_sales is not None:
        filtered_sales = filtered_sales[filtered_sales['customer_id'].isin(filtered_cust['customer_id'])]
 
if selected_channel != t['all']:
    filtered_mkt = filtered_mkt[filtered_mkt['channel'] == selected_channel]




#HEADER SECTION

st.markdown(f"""
    <div class="header-bar">
        <div class="header-badge">{svg_icon('logo', 24)}</div>
        <div>
            <div class="header-title">{t['title']}</div>
            <div class="header-subtitle">{t['subtitle']}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Bandeau informatif : signale les valeurs provisoires (segmentation/churn/ROI)
# tant que les livrables réels de M3/M4/M5/M6 ne sont pas encore branchés.
notice_keys = {'segmentation': 'notice_segmentation', 'churn': 'notice_churn', 'roi': 'notice_roi', 'sales': 'sales_pending'}
active_notices = [t[notice_keys[n]] for n in demo_notes if n in notice_keys]
if active_notices:
    st.warning("  \n".join(active_notices))

# KPI BANNER
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
 
total_rev = filtered_cust['total_spent'].sum()
active_cust = filtered_cust['customer_id'].nunique()
avg_roi = filtered_mkt['roi'].mean()
avg_churn = filtered_pred['churn_probability_final'].mean() * 100
 
with col_kpi1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon-wrap">{svg_icon('revenue', 18)}</div>
            <div class="kpi-title">{t['kpi_revenue']}</div>
            <div class="kpi-value">{format_ar(total_rev)}</div>
            <div class="kpi-sub">+12.4% vs mois dernier</div>
        </div>
    """, unsafe_allow_html=True)
 
with col_kpi2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon-wrap">{svg_icon('customers', 18)}</div>
            <div class="kpi-title">{t['kpi_customers']}</div>
            <div class="kpi-value">{active_cust:,}</div>
            <div class="kpi-sub">+5.1% ce trimestre</div>
        </div>
    """, unsafe_allow_html=True)
 
with col_kpi3:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon-wrap">{svg_icon('roi', 18)}</div>
            <div class="kpi-title">{t['kpi_roi']}</div>
            <div class="kpi-value">{avg_roi:.1f} %</div>
            <div class="kpi-sub">Performance Optimale</div>
        </div>
    """, unsafe_allow_html=True)
 
with col_kpi4:
    st.markdown(f"""
        <div class="kpi-card warning-card">
            <div class="kpi-icon-wrap warning">{svg_icon('churn', 18, color='#C0623D')}</div>
            <div class="kpi-title">{t['kpi_churn']}</div>
            <div class="kpi-value">{avg_churn:.1f} %</div>
            <div class="kpi-sub">Alerte Rétention</div>
        </div>
    """, unsafe_allow_html=True)
 
 
 
st.markdown("<br>", unsafe_allow_html=True)


# TAB 2: MARKETING CAMPAIGNS (M5)

if active_tab == 2:
    col_c, col_d = st.columns([1, 1])

    with col_c:
        section_title(t['funnel'], 'tab_campaigns')
        funnel_data = pd.DataFrame({
            'Stage': ['Impressions', 'Clicks', 'Conversions'],
            'Value': [
                int(filtered_mkt['impressions'].sum()),
                int(filtered_mkt['clicks'].sum()),
                int(filtered_mkt['conversions'].sum()),
            ]
        })
        fig_funnel = px.funnel(funnel_data, x='Value', y='Stage', color_discrete_sequence=['#8B5CF6'])
        style_chart(fig_funnel, xaxis_title="Volume", yaxis_title="")
        st.plotly_chart(fig_funnel, use_container_width=True)

    with col_d:
        section_title(t['channel_perf'], 'tab_campaigns')
        if channel_kpis_df is not None:
            channel_metrics = channel_kpis_df.rename(columns={'avg_roi_percent': 'avg_roi'})
        else:
            channel_metrics = filtered_mkt.groupby('channel', as_index=False).agg(
                avg_roi=('roi', 'mean'),
                avg_cpc=('cpc', 'mean'),
                avg_cpa=('cpa', 'mean')
            )
        fig_channel = px.bar(channel_metrics, x='channel', y='avg_roi', color='channel',
                             color_discrete_sequence=['#8B5CF6', '#6D3BBD', '#B497FF', '#D9C7FF', '#5B8DEF'])
        style_chart(fig_channel, xaxis_title="Canal", yaxis_title="ROI moyen (%)")
        st.plotly_chart(fig_channel, use_container_width=True)

    st.markdown("---")
    section_title(t['budget_vs_conv'], 'tab_campaigns')
    fig_budget = px.scatter(filtered_mkt, x='spend', y='conversions', color='channel', size='spend',
                             hover_data=['campaign'],
                             color_discrete_sequence=['#8B5CF6', '#6D3BBD', '#B497FF', '#D9C7FF', '#5B8DEF'])
    style_chart(fig_budget, xaxis_title="Budget (Ar)", yaxis_title="Conversions")
    st.plotly_chart(fig_budget, use_container_width=True)

    st.markdown("---")
    section_title(t['campaign_table'], 'tab_campaigns')
    st.dataframe(filtered_mkt[['campaign', 'channel', 'impressions', 'clicks', 'conversions', 'taux_conversion', 'spend', 'revenue', 'roi', 'cpc', 'cpa']], use_container_width=True)

# TAB 1: SALES & PERFORMANCE (M2)

if active_tab == 1:
    col_t1, col_t2 = st.columns(2)
    n_transactions = int(filtered_cust['frequency'].sum()) if 'frequency' in filtered_cust.columns else 0
    avg_per_client = filtered_cust['total_spent'].mean() if len(filtered_cust) else 0
    with col_t1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon-wrap">{svg_icon('tab_sales', 18)}</div>
                <div class="kpi-title">{t['kpi_transactions']}</div>
                <div class="kpi-value">{n_transactions:,}</div>
            </div>
        """, unsafe_allow_html=True)
    with col_t2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon-wrap">{svg_icon('revenue', 18)}</div>
                <div class="kpi-title">{t['kpi_avg_per_client']}</div>
                <div class="kpi-value">{format_ar(avg_per_client)}</div>
            </div>
        """, unsafe_allow_html=True)

    if sales_df is None:
        st.info(t['sales_pending'])

    st.markdown("---")
    section_title(t['demo_dist'], 'customers')
    fig_demo = px.histogram(filtered_cust, x='age', color='gender', barmode='group',
                            color_discrete_sequence=['#5B8DEF', '#A6C2F5'])
    style_chart(fig_demo, xaxis_title="Âge", yaxis_title="Nombre de Clients")
    st.plotly_chart(fig_demo, use_container_width=True)



# TAB 3: CUSTOMER SEGMENTATION (M3/M4)

if active_tab == 3:
    col_e, col_f = st.columns([1.5, 1])
    
    with col_e:
        section_title(t['cluster_map'], 'tab_clusters')
        fig_pca = px.scatter(filtered_pred, x='pca_x', y='pca_y', color='cluster',
                             hover_data=['customer_id', 'clv'],
                             color_discrete_sequence=['#8B5CF6', '#6D3BBD', '#B497FF', '#D9C7FF'])
        style_chart(fig_pca, xaxis_title="Axe 1 (RFM ou provisoire)", yaxis_title="Axe 2 (RFM ou provisoire)")
        st.plotly_chart(fig_pca, use_container_width=True)
        
    with col_f:
        section_title(t['cluster_dist'], 'tab_clusters')
        cluster_counts = filtered_cust['cluster'].value_counts().reset_index()
        fig_pie = px.pie(cluster_counts, names='cluster', values='count', hole=0.4,
                         color_discrete_sequence=['#8B5CF6', '#6D3BBD', '#B497FF', '#D9C7FF'])
        style_chart(fig_pie)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    st.markdown("---")
    section_title(t['persona_details'], 'tab_clusters')
    if strategy_df is not None:
        st.dataframe(strategy_df, use_container_width=True)
    else:
        st.info("**Segment VIP (Exemple Persona M4)** : Clientèle de 35-50 ans avec panier moyen supérieur à 250 Ar, forte sensibilité aux campagnes Email et réachat régulier.")




# TAB 4: PREDICTIVE AI & CHURN RISK (M6/M7)

if active_tab == 4:
    col_g, col_h = st.columns([1, 1])
    
    with col_g:
        section_title(t['churn_dist'], 'tab_ai')
        fig_churn = px.histogram(filtered_pred, x='churn_probability_final', color='churn_risk', nbins=20,
                                 color_discrete_map={'Faible/Low': '#34D399', 'Moyen/Medium': '#F5A524', 'Élevé/High': '#F87171'})
        style_chart(fig_churn, xaxis_title="Probabilité de Churn", yaxis_title="Nombre de Clients")
        st.plotly_chart(fig_churn, use_container_width=True)
        
    with col_h:
        section_title(t['clv_vs_churn'], 'tab_ai')
        fig_clv = px.scatter(filtered_pred, x='churn_probability_final', y='clv', color='churn_risk',
                             hover_data=['customer_id'],
                             color_discrete_map={'Faible/Low': '#34D399', 'Moyen/Medium': '#F5A524', 'Élevé/High': '#F87171'})
        style_chart(fig_clv, xaxis_title="Probabilité de Churn", yaxis_title="Valeur à Vie (CLV Ar)")
        st.plotly_chart(fig_clv, use_container_width=True)
        
    st.markdown("---")
    section_title(t['feature_importance'], 'tab_ai')
    if FEATURE_IMPORTANCE_FILE.exists():
        fi_df = _norm_cols(pd.read_csv(FEATURE_IMPORTANCE_FILE)).sort_values('importance', ascending=True)
        fig_fi = px.bar(fi_df, x='importance', y='variable', orientation='h',
                         color_discrete_sequence=['#8B5CF6'])
        style_chart(fig_fi, xaxis_title="Importance", yaxis_title="")
        st.plotly_chart(fig_fi, use_container_width=True)
    else:
        st.info(t['feature_importance_pending'])

    st.markdown("---")
    section_title(t['export_churn'], 'download')
    high_risk_df = filtered_pred[filtered_pred['churn_risk'] == 'Élevé/High']
    st.dataframe(high_risk_df[['customer_id', 'cluster', 'churn_probability_final', 'clv']], use_container_width=True)
    
    csv_data = high_risk_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=t['download_btn'],
        data=csv_data,
        file_name='clients_risque_churn_prioritaire.csv',
        mime='text/csv'
    )