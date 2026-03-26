import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# ================= CONFIG & DESIGN (ADAPTÉ AU LOGO) =================
st.set_page_config(page_title="365 GYM & FITNESS", layout="wide", page_icon="💪")

# Couleurs adaptées (Noir profond et Or du logo)
LOGO_BLACK = "#000000" # Noir pur
LOGO_GOLD = "#e1ad01"  # L'or/jaune de ton logo
TEXT_WHITE = "#FFFFFF"

st.markdown(f"""
    <style>
    /* Background avec image de montagne et voile noir */
    .stApp {{
        background: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)), 
                    url("https://images.unsplash.com");
        background-size: cover;
        background-attachment: fixed;
    }}
    
    /* Barre de navigation haute (Header) */
    header[data-testid="stHeader"] {{
        background-color: {LOGO_BLACK} !important;
        border-bottom: 2px solid {LOGO_GOLD};
    }}
    
    /* Sidebar (Menu à côté) */
    [data-testid="stSidebar"] {{
        background-color: {LOGO_BLACK} !important;
        border-right: 1px solid {LOGO_GOLD};
    }}

    /* Boutons style Adventure (Bordures Or) */
    .stButton>button {{
        background-color: rgba(225, 173, 1, 0.1);
        color: {TEXT_WHITE};
        border: 1px solid {LOGO_GOLD};
        width: 100%;
        font-weight: bold;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        background-color: {LOGO_GOLD};
        color: {LOGO_BLACK};
    }}

    /* Onglets (Tabs) adaptées */
    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: #111;
        color: white;
        border: 1px solid #333;
        padding: 10px 20px;
        border-radius: 4px;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {LOGO_GOLD} !important;
        color: {LOGO_BLACK} !important;
    }}
    </style>
""", unsafe_allow_html=True)

# ================= SUPABASE =================
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception:
    st.error("🚨 Configuration Supabase manquante !")
    st.stop()

# ================= FONCTIONS (IDENTIQUES) =================
logo_path = "logo.png"
def afficher_logo(w=200):
    if os.path.exists(logo_path): st.image(logo_path, width=w)
    else: st.markdown(f"<h2 style='color:{LOGO_GOLD}'>🏋️ 365 GYM</h2>", unsafe_allow_html=True)

def charger_data():
    try:
        r = supabase.table("abonnes").select("*").execute()
        return pd.DataFrame(r.data) if r.data else pd.DataFrame(columns=["nom","date_debut","duree_mois","date_fin","WhatsApp","statut"])
    except: return pd.DataFrame()

# ================= NAVIGATION HAUTE (MENU) =================
col_logo, col_nav1, col_nav2 = st.columns([1,1,1])
with col_logo: afficher_logo(150)
with col_nav1: 
    if st.button("📢 ACCUEIL / PUBLICITÉ"): st.session_state['page'] = "pub"; st.rerun()
with col_nav2: 
    if st.button("🔐 GESTION ADMIN"): st.session_state['page'] = "admin"; st.rerun()

st.divider()

# Initialisation Session State
if 'page' not in st.session_state: st.session_state['page'] = "pub"
if 'logged' not in st.session_state: st.session_state['logged'] = False
if 'edit_item' not in st.session_state: st.session_state['edit_item'] = None

# ================= CONTENU DES PAGES =================

if st.session_state['page'] == "pub":
    st.markdown(f"<h1 style='text-align:center; color:{LOGO_GOLD}; letter-spacing: 5px;'>NEW ADVENTURE</h1>", unsafe_allow_html=True)
    # Affichage des publicités (ton code existant)
    # ...

elif st.session_state['page'] == "admin":
    if not st.session_state.logged:
        pwd = st.text_input("Code Admin", type="password")
        if st.button("Entrer"):
            if pwd=="1980": st.session_state.logged=True; st.rerun()
    else:
        t1, t2, t3, t4, t5 = st.tabs(["📝 Inscription", "📊 Liste", "📣 Publier", "⏳ J-3", "❌ EXPIRÉS"])

        # TAB 1 & 2 : GESTION + MODIFIER / SUPPRIMER
        with t1:
            edit = st.session_state.edit_item
            with st.form("inscription"):
                n = st.text_input("Nom", value=edit['nom'] if edit else "")
                w = st.text_input("WhatsApp", value=edit['WhatsApp'] if edit else "")
                m = st.number_input("Mois", min_value=1, value=int(edit['duree_mois']) if edit else 1)
                if st.form_submit_button("SAUVEGARDER"):
                    fin = datetime.now() + pd.DateOffset(months=m)
                    data = {"nom":n, "WhatsApp":w, "duree_mois":m, "date_fin":fin.strftime("%Y-%m-%d"), "statut":"Actif"}
                    supabase.table("abonnes").upsert(data, on_conflict="WhatsApp").execute()
                    st.session_state.edit_item = None
                    st.rerun()

        with t2:
            df = charger_data()
            for i, r in df.iterrows():
                c1, c2, c3, c4 = st.columns([3,2,1,1])
                c1.write(r['nom'])
                c2.write(f"Fin: {r['date_fin']}")
                if c3.button("✏️", key=f"e{i}"):
                    st.session_state.edit_item = r
                    st.session_state['page'] = "admin" # Reste ici
                    st.rerun()
                if c4.button("🗑️", key=f"d{i}"):
                    supabase.table("abonnes").delete().eq("WhatsApp", r['WhatsApp']).execute()
                    st.rerun()

        # TAB 5 : LISTE DES EXPIRÉS
        with t5:
            st.subheader("🔴 Abonnements Terminés")
            df_e = charger_data()
            if not df_e.empty:
                df_e['date_fin_dt'] = pd.to_datetime(df_e['date_fin'])
                exp = df_e[df_e['date_fin_dt'] < pd.Timestamp(datetime.now().date())]
                for _, r in exp.iterrows():
                    st.markdown(f"<div style='padding:10px; border:1px solid red; margin-bottom:5px; color:white;'>❌ {r['nom']} - Expiré le {r['date_fin']}</div>", unsafe_allow_html=True)
