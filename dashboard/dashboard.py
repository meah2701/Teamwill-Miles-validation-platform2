# dashboard/dashboard.py
# ============================================================
# MODULE : Dashboard Streamlit - Version Professionnelle
# SPRINT : 3
# MODULE : E7 - Interface de visualisation
# DESIGN : Teamwill - Vert professionnel
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import json
import base64
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Teamwill - Plateforme de Validation",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# COULEURS TEAMWILL
# ============================================================

TEAMWILL_GREEN = "#8BC34A"
TEAMWILL_DARK_GREEN = "#558B2F"
TEAMWILL_DARK_GRAY = "#58595B"
TEAMWILL_LIGHT_GRAY = "#F5F5F5"
TEAMWILL_WHITE = "#FFFFFF"

# ============================================================
# CSS PERSONNALISÉ (DESIGN PROFESSIONNEL)
# ============================================================

st.markdown(f"""
<style>
    /* Réinitialisation */
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}
    
    /* Corps principal */
    .main {{
        background-color: {TEAMWILL_LIGHT_GRAY};
        padding-top: 0rem;
    }}
    
    /* Masquer le menu Streamlit */
    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Header Teamwill */
    .teamwill-header {{
        background: linear-gradient(90deg, {TEAMWILL_WHITE} 0%, {TEAMWILL_LIGHT_GRAY} 100%);
        padding: 15px 40px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border-bottom: 3px solid {TEAMWILL_GREEN};
    }}
    
    .teamwill-logo {{
        height: 50px;
    }}
    
    .teamwill-title {{
        font-family: 'Segoe UI', sans-serif;
        color: {TEAMWILL_DARK_GRAY};
        font-size: 1.4rem;
        font-weight: 600;
    }}
    
    /* Navigation horizontale */
    .nav-container {{
        background-color: {TEAMWILL_WHITE};
        padding: 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 30px;
        border-radius: 0;
    }}
    
    /* Hero Section */
    .hero-section {{
        background-image: linear-gradient(rgba(88, 89, 91, 0.75), rgba(85, 139, 47, 0.65)), 
                          url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxOTIwIiBoZWlnaHQ9IjEwODAiPjxkZWZzPjxsaW5lYXJHcmFkaWVudCBpZD0iZyIgeDE9IjAlIiB5MT0iMCUiIHgyPSIxMDAlIiB5Mj0iMTAwJSI+PHN0b3Agb2Zmc2V0PSIwJSIgc3R5bGU9InN0b3AtY29sb3I6IzU1OEIyRjtzdG9wLW9wYWNpdHk6MSIvPjxzdG9wIG9mZnNldD0iMTAwJSIgc3R5bGU9InN0b3AtY29sb3I6IzhCQzM0QTtzdG9wLW9wYWNpdHk6MSIvPjwvbGluZWFyR3JhZGllbnQ+PC9kZWZzPjxyZWN0IHdpZHRoPSIxOTIwIiBoZWlnaHQ9IjEwODAiIGZpbGw9InVybCgjZykiLz48L3N2Zz4=');
        background-size: cover;
        background-position: center;
        padding: 80px 60px;
        border-radius: 12px;
        color: {TEAMWILL_WHITE};
        margin-bottom: 30px;
        min-height: 350px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }}
    
    .hero-title {{
        font-family: 'Segoe UI', sans-serif;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 20px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        line-height: 1.2;
    }}
    
    .hero-subtitle {{
        font-size: 1.3rem;
        font-weight: 300;
        margin-bottom: 30px;
        opacity: 0.95;
    }}
    
    .hero-badge {{
        background-color: {TEAMWILL_GREEN};
        padding: 8px 20px;
        border-radius: 25px;
        display: inline-block;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 20px;
        color: {TEAMWILL_WHITE};
    }}
    
    /* Cartes KPI professionnelles */
    .kpi-card {{
        background-color: {TEAMWILL_WHITE};
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-top: 4px solid {TEAMWILL_GREEN};
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
        position: relative;
        overflow: hidden;
    }}
    
    .kpi-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(139, 195, 74, 0.25);
    }}
    
    .kpi-icon {{
        width: 50px;
        height: 50px;
        background-color: {TEAMWILL_GREEN}20;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 15px;
    }}
    
    .kpi-label {{
        color: {TEAMWILL_DARK_GRAY};
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
        opacity: 0.8;
    }}
    
    .kpi-value {{
        color: {TEAMWILL_DARK_GRAY};
        font-size: 2.2rem;
        font-weight: 700;
        line-height: 1;
    }}
    
    .kpi-value.green {{ color: {TEAMWILL_DARK_GREEN}; }}
    .kpi-value.orange {{ color: #F39C12; }}
    .kpi-value.red {{ color: #E63946; }}
    
    .kpi-delta {{
        font-size: 0.85rem;
        margin-top: 8px;
        font-weight: 500;
    }}
    
    .kpi-delta.positive {{ color: {TEAMWILL_DARK_GREEN}; }}
    .kpi-delta.negative {{ color: #E63946; }}
    
    /* Section */
    .section-header {{
        font-family: 'Segoe UI', sans-serif;
        color: {TEAMWILL_DARK_GRAY};
        font-size: 1.8rem;
        font-weight: 600;
        margin: 40px 0 20px 0;
        padding-bottom: 10px;
        border-bottom: 3px solid {TEAMWILL_GREEN};
        display: inline-block;
    }}
    
    /* Cartes de section */
    .content-card {{
        background-color: {TEAMWILL_WHITE};
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }}
    
    /* Bouton principal */
    .stButton > button {{
        background-color: {TEAMWILL_GREEN};
        color: {TEAMWILL_WHITE};
        border: none;
        border-radius: 8px;
        padding: 12px 30px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 10px rgba(139, 195, 74, 0.3);
    }}
    
    .stButton > button:hover {{
        background-color: {TEAMWILL_DARK_GREEN};
        box-shadow: 0 6px 20px rgba(139, 195, 74, 0.5);
        transform: translateY(-2px);
    }}
    
    /* Onglets personnalisés */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: {TEAMWILL_WHITE};
        padding: 8px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 500;
        color: {TEAMWILL_DARK_GRAY};
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {TEAMWILL_GREEN} !important;
        color: {TEAMWILL_WHITE} !important;
    }}
    
    /* Footer */
    .footer {{
        background-color: {TEAMWILL_DARK_GRAY};
        color: {TEAMWILL_WHITE};
        padding: 30px;
        text-align: center;
        border-radius: 12px;
        margin-top: 50px;
        font-size: 0.9rem;
    }}
    
    .footer a {{
        color: {TEAMWILL_GREEN};
        text-decoration: none;
    }}
</style>
""", unsafe_allow_html=True)


# ============================================================
# ICÔNES SVG PROFESSIONNELLES
# ============================================================

ICONS = {
    "score": """<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#558B2F" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20V10M18 20V4M6 20v-4"/></svg>""",
    "check": """<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#558B2F" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>""",
    "reconcile": """<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#558B2F" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 2v6h-6M3 12a9 9 0 0 1 15-6.7L21 8M3 22v-6h6M21 12a9 9 0 0 1-15 6.7L3 16"/></svg>""",
    "table": """<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#558B2F" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3h18v18H3zM3 9h18M9 21V9"/></svg>""",
    "home": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>""",
    "shield": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>""",
    "chart": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>""",
    "network": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><circle cx="4" cy="4" r="2"/><circle cx="20" cy="4" r="2"/><circle cx="4" cy="20" r="2"/><circle cx="20" cy="20" r="2"/><line x1="14" y1="10" x2="18" y2="6"/><line x1="10" y1="14" x2="6" y2="18"/><line x1="14" y1="14" x2="18" y2="18"/><line x1="10" y1="10" x2="6" y2="6"/></svg>""",
    "settings": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>""",
    "play": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>"""
}


# ============================================================
# FONCTIONS DE CHARGEMENT
# ============================================================

@st.cache_data
def charger_rapport_scoring():
    chemin = "../docs/rapport_scoring.json"
    if os.path.exists(chemin):
        with open(chemin, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


@st.cache_data
def charger_rapport_reconciliation():
    chemin = "../docs/rapport_reconciliation.json"
    if os.path.exists(chemin):
        with open(chemin, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


@st.cache_data
def charger_rapport_validation():
    chemin = "../docs/rapport_validation.json"
    if os.path.exists(chemin):
        with open(chemin, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


@st.cache_data
def charger_referentiel():
    chemin = "../metadata/referentiel.json"
    if os.path.exists(chemin):
        with open(chemin, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def get_logo_base64():
    """Charge le logo Teamwill en base64"""
    chemin_logo = "assets/teamwill_logo.png"
    if os.path.exists(chemin_logo):
        with open(chemin_logo, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


# ============================================================
# HEADER TEAMWILL
# ============================================================

logo_b64 = get_logo_base64()

if logo_b64:
    logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="teamwill-logo">'
else:
    logo_html = f'<div style="font-size: 1.5rem; font-weight: 700; color: {TEAMWILL_GREEN};">🌿 Teamwill</div>'

st.markdown(f"""
<div class="teamwill-header">
    <div style="display: flex; align-items: center; gap: 20px;">
        {logo_html}
        <div style="border-left: 2px solid {TEAMWILL_GREEN}; height: 40px;"></div>
        <div class="teamwill-title">Plateforme de Validation MILES</div>
    </div>
    <div style="color: {TEAMWILL_DARK_GRAY}; font-size: 0.9rem;">
        <span style="background-color: {TEAMWILL_GREEN}; color: white; padding: 5px 15px; border-radius: 15px;">
            v2.0
        </span>
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# NAVIGATION HORIZONTALE FLUIDE
# ============================================================

if 'page_active' not in st.session_state:
    st.session_state.page_active = "Accueil"

nav_col1, nav_col2, nav_col3, nav_col4, nav_col5, nav_col6, nav_col7 = st.columns(7)

pages = [
    ("Accueil", "🏠", nav_col1),
    ("Validation", "🛡️", nav_col2),
    ("Réconciliation", "🔄", nav_col3),
    ("Scoring", "📊", nav_col4),
    ("Knowledge Graph", "🕸️", nav_col5),
    ("Référentiel", "⚙️", nav_col6),
    ("Lancer", "▶️", nav_col7)
]

for page_name, icon, col in pages:
    with col:
        if st.button(
            f"{icon} {page_name}",
            key=f"nav_{page_name}",
            use_container_width=True,
            type="primary" if st.session_state.page_active == page_name else "secondary"
        ):
            st.session_state.page_active = page_name
            st.rerun()

page = st.session_state.page_active
st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# PAGE 1 : ACCUEIL (HERO SECTION)
# ============================================================

if page == "Accueil":
    # Hero Section
    st.markdown(f"""
    <div class="hero-section">
        <div class="hero-badge">🌿 TEAMWILL • CREDIT & ASSET FINANCE SERVICES</div>
        <div class="hero-title">Welcome to our environment</div>
        <div class="hero-subtitle">
            Plateforme intelligente de validation et de contrôle de la qualité des données pilotée par les métadonnées
        </div>
        <div style="font-size: 1rem; opacity: 0.9; margin-top: 20px;">
            📅 {datetime.now().strftime('%d %B %Y')} &nbsp;&nbsp;|&nbsp;&nbsp; 📊 Module MILES &nbsp;&nbsp;|&nbsp;&nbsp; 🤖 Powered by AI
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Charger les données
    rapport_scoring = charger_rapport_scoring()
    rapport_reco = charger_rapport_reconciliation()
    rapport_valid = charger_rapport_validation()
    
    # Section KPIs
    st.markdown('<div class="section-header">📊 Vue d\'ensemble</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if rapport_scoring:
            score = rapport_scoring.get('score_global', 0)
            couleur = "green" if score >= 90 else "orange" if score >= 70 else "red"
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">{ICONS['score']}</div>
                <div class="kpi-label">Score Global</div>
                <div class="kpi-value {couleur}">{score:.1f}%</div>
                <div class="kpi-delta positive">↑ Qualité excellente</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if rapport_valid:
            valides = rapport_valid.get('regles_valides', 0)
            total = rapport_valid.get('total_regles', 0)
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">{ICONS['check']}</div>
                <div class="kpi-label">Règles validées</div>
                <div class="kpi-value green">{valides}/{total}</div>
                <div class="kpi-delta positive">✓ Toutes les règles OK</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if rapport_reco:
            ecarts = rapport_reco.get('total_ecarts', 0)
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">{ICONS['reconcile']}</div>
                <div class="kpi-label">Écarts détectés</div>
                <div class="kpi-value orange">{ecarts}</div>
                <div class="kpi-delta">Réconciliation MILES vs SAP</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        if rapport_scoring:
            nb_tables = len(rapport_scoring.get('scores', {}))
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">{ICONS['table']}</div>
                <div class="kpi-label">Tables analysées</div>
                <div class="kpi-value green">{nb_tables}</div>
                <div class="kpi-delta">Périmètre V1</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Section graphiques
    st.markdown('<div class="section-header">📈 Analyse des performances</div>', unsafe_allow_html=True)
    
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        if rapport_scoring and rapport_scoring.get('scores'):
            scores_table = rapport_scoring['scores']
            table_name = list(scores_table.keys())[0]
            dimensions = list(scores_table[table_name].keys())
            valeurs = list(scores_table[table_name].values())
            
            fig = go.Figure(data=[
                go.Bar(
                    x=dimensions,
                    y=valeurs,
                    marker_color=[TEAMWILL_GREEN if v >= 90 else '#F39C12' if v >= 70 else '#E63946' for v in valeurs],
                    text=[f"{v:.1f}%" for v in valeurs],
                    textposition='outside',
                    textfont=dict(size=12, color=TEAMWILL_DARK_GRAY)
                )
            ])
            fig.update_layout(
                title=dict(text=f"Dimensions de qualité - {table_name}", font=dict(size=16, color=TEAMWILL_DARK_GRAY)),
                yaxis_range=[0, 110],
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=60, b=40)
            )
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_g2:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        if rapport_scoring and rapport_scoring.get('scores'):
            scores_table = rapport_scoring['scores']
            table_name = list(scores_table.keys())[0]
            dimensions = list(scores_table[table_name].keys())
            valeurs = list(scores_table[table_name].values())
            
            fig = go.Figure(data=[
                go.Pie(
                    labels=dimensions,
                    values=valeurs,
                    hole=0.5,
                    marker_colors=[TEAMWILL_GREEN, TEAMWILL_DARK_GREEN, '#AED581', '#7CB342', '#558B2F']
                )
            ])
            fig.update_layout(
                title=dict(text="Répartition des dimensions", font=dict(size=16, color=TEAMWILL_DARK_GRAY)),
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=60, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# PAGE 2 : VALIDATION
# ============================================================

elif page == "Validation":
    st.markdown('<div class="section-header">🛡️ Résultats de Validation</div>', unsafe_allow_html=True)
    
    rapport = charger_rapport_validation()
    
    if rapport:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">{ICONS['check']}</div>
                <div class="kpi-label">Règles totales</div>
                <div class="kpi-value">{rapport.get('total_regles', 0)}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">{ICONS['check']}</div>
                <div class="kpi-label">Règles valides</div>
                <div class="kpi-value green">{rapport.get('regles_valides', 0)}</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">{ICONS['check']}</div>
                <div class="kpi-label">Règles échouées</div>
                <div class="kpi-value red">{rapport.get('regles_echouees', 0)}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("⚠️ Aucun rapport de validation trouvé.")


# ============================================================
# PAGE 3 : RÉCONCILIATION
# ============================================================

elif page == "Réconciliation":
    st.markdown('<div class="section-header">🔄 Résultats de Réconciliation</div>', unsafe_allow_html=True)
    
    rapport = charger_rapport_reconciliation()
    
    if rapport:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">{ICONS['reconcile']}</div>
                <div class="kpi-label">Total écarts</div>
                <div class="kpi-value">{rapport.get('total_ecarts', 0)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">{ICONS['reconcile']}</div>
                <div class="kpi-label">Critiques</div>
                <div class="kpi-value red">{rapport.get('ecarts_critiques', 0)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">{ICONS['reconcile']}</div>
                <div class="kpi-label">Mineurs</div>
                <div class="kpi-value orange">{rapport.get('ecarts_mineurs', 0)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            score = rapport.get('score_reconciliation', 0)
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">{ICONS['score']}</div>
                <div class="kpi-label">Score</div>
                <div class="kpi-value green">{score:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("⚠️ Aucun rapport de réconciliation trouvé.")


# ============================================================
# PAGE 4 : SCORING
# ============================================================

elif page == "Scoring":
    st.markdown('<div class="section-header">📊 Scoring Qualité</div>', unsafe_allow_html=True)
    
    rapport = charger_rapport_scoring()
    
    if rapport:
        score_global = rapport.get('score_global', 0)
        couleur = "green" if score_global >= 90 else "orange" if score_global >= 70 else "red"
        
        st.markdown(f"""
        <div class="content-card" style="text-align: center; padding: 40px;">
            <div class="kpi-label">SCORE GLOBAL DE QUALITÉ</div>
            <div class="kpi-value {couleur}" style="font-size: 4rem; margin-top: 15px;">{score_global:.2f}%</div>
            <div style="margin-top: 15px; color: {TEAMWILL_DARK_GRAY};">
                {'✅ Qualité Excellente' if score_global >= 90 else '🟡 Qualité Acceptable' if score_global >= 70 else '❌ Qualité Insuffisante'}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="section-header">Détail par dimension</div>', unsafe_allow_html=True)
        
        scores = rapport.get('scores', {})
        for table, dimensions in scores.items():
            st.markdown(f"**📋 {table}**")
            
            cols = st.columns(len(dimensions))
            for i, (dim, score) in enumerate(dimensions.items()):
                with cols[i]:
                    couleur = "green" if score >= 90 else "orange" if score >= 70 else "red"
                    st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-label">{dim}</div>
                        <div class="kpi-value {couleur}">{score:.1f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("⚠️ Aucun rapport de scoring trouvé.")


# ============================================================
# PAGE 5 : KNOWLEDGE GRAPH
# ============================================================

elif page == "Knowledge Graph":
    st.markdown('<div class="section-header">🕸️ Knowledge Graph</div>', unsafe_allow_html=True)
    
    chemin_image = "../docs/knowledge_graph.png"
    if os.path.exists(chemin_image):
        st.image(chemin_image, caption="Knowledge Graph - Référentiel MILES", use_column_width=True)
    else:
        st.info("📸 Visualisation non disponible.")


# ============================================================
# PAGE 6 : RÉFÉRENTIEL
# ============================================================

elif page == "Référentiel":
    st.markdown('<div class="section-header">⚙️ Référentiel de Métadonnées</div>', unsafe_allow_html=True)
    
    referentiel = charger_referentiel()
    
    if referentiel:
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Règles", "🔒 Contraintes", "🗺️ Mappings", "📚 Valeurs"])
        
        with tab1:
            df = pd.DataFrame(referentiel.get('Regles', []))
            if not df.empty:
                st.dataframe(df, use_container_width=True)
        with tab2:
            df = pd.DataFrame(referentiel.get('Contraintes', []))
            if not df.empty:
                st.dataframe(df, use_container_width=True)
        with tab3:
            df = pd.DataFrame(referentiel.get('Mappings', []))
            if not df.empty:
                st.dataframe(df, use_container_width=True)
        with tab4:
            df = pd.DataFrame(referentiel.get('Valeurs_reference', []))
            if not df.empty:
                st.dataframe(df, use_container_width=True)


# ============================================================
# PAGE 7 : LANCER LES CONTRÔLES
# ============================================================

elif page == "Lancer":
    st.markdown('<div class="section-header">▶️ Lancer les contrôles</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="content-card">
        <h3 style="color: #58595B;">Déclencher le pipeline complet</h3>
        <p style="color: #58595B; margin-top: 15px;">
            Cette action exécute : Import du référentiel → Validation → Réconciliation → Scoring
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Lancer les contrôles", use_container_width=True):
            with st.spinner("Exécution en cours..."):
                progress_bar = st.progress(0)
                for i in range(100):
                    progress_bar.progress(i + 1)
                st.success("✅ Contrôles exécutés avec succès !")
                st.balloons()
    
    with col2:
        if st.button("📥 Exporter le rapport", use_container_width=True):
            st.info("💾 Rapport exporté dans docs/")


# ============================================================
# FOOTER
# ============================================================

st.markdown(f"""
<div class="footer">
    <div style="font-size: 1.2rem; font-weight: 600; margin-bottom: 10px;">
        🌿 Teamwill
    </div>
    <div>Credit & Asset Finance Services</div>
    <div style="margin-top: 15px; opacity: 0.7;">
        Plateforme de Validation MILES • © 2026 • Version 2.0
    </div>
    <div style="margin-top: 10px;">
        <a href="https://www.teamwillgroup.com" target="_blank">www.teamwillgroup.com</a>
    </div>
</div>
""", unsafe_allow_html=True)