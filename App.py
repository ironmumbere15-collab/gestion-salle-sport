import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime

# 1. CONNEXION SÉCURISÉE (Utilise les noms des secrets Streamlit)
try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("🚨 Erreur de configuration : Vérifie tes Secrets dans Streamlit Cloud !")
    st.stop()

# 2. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="365 GYM & FITNESS", layout="wide", page_icon="💪")

# 3. STYLE PERSONNALISÉ (CSS)
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #FF4B4B; color: white; }
    .stTextInput>div>div>input { border-radius: 5px; }
    </style>
    """, unsafe_allow_now=True)

# 4. INITIALISATION DU SESSION STATE
if 'admin' not in st.session_state:
    st.session_state['admin'] = False

if 'abonnés' not in st.session_state:
    st.session_state['abonnés'] = pd.DataFrame(columns=["Nom", "Date début", "Durée (mois)", "Date fin", "WhatsApp", "Statut"])

# 5. FONCTIONS LOGIQUES
def calculer_date_fin(date_debut, duree):
    return date_debut + pd.DateOffset(months=duree)

def charger_depuis_supabase():
    try:
        response = supabase.table("abonnes").select("*").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            # Conversion pour l'affichage Streamlit
            df_final = pd.DataFrame()
            df_final["Nom"] = df["nom"]
            df_final["Date début"] = pd.to_datetime(df["date_debut"])
            df_final["Durée (mois)"] = df["duree_mois"]
            df_final["Date fin"] = pd.to_datetime(df["date_fin"])
            df_final["WhatsApp"] = df["whatsapp"]
            df_final["Statut"] = df["statut"]
            st.session_state['abonnés'] = df_final
    except Exception as e:
        st.error(f"Erreur de chargement : {e}")

def sauvegarder_dans_supabase(nom, debut, duree, fin, whatsapp, statut):
    try:
        data = {
            "nom": nom,
            "date_debut": debut.strftime("%Y-%m-%d"),
            "duree_mois": int(duree),
            "date_fin": fin.strftime("%Y-%m-%d"),
            "whatsapp": str(whatsapp),
            "statut": statut
        }
        supabase.table("abonnes").upsert(data, on_conflict="whatsapp").execute()
        st.success(f"✅ {nom} enregistré avec succès !")
    except Exception as e:
        st.error(f"Erreur de sauvegarde : {e}")

# Charger les données au lancement
if st.session_state['abonnés'].empty:
    charger_depuis_supabase()

# 6. INTERFACE UTILISATEUR
st.title("🏋️ 365 GYM & FITNESS - GESTION")

# --- SECTION CONNEXION ADMIN ---
if not st.session_state['admin']:
    with st.sidebar:
        st.subheader("Connexion Admin")
        password = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            if password == "1980":
                st.session_state['admin'] = True
                st.rerun()
            else:
                st.error("Mot de passe incorrect")
else:
    if st.sidebar.button("Se déconnecter"):
        st.session_state['admin'] = False
        st.rerun()

# --- FORMULAIRE D'AJOUT ---
st.header("➕ Ajouter ou Modifier un Abonné")
with st.form("form_ajoute", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        nom = st.text_input("Nom complet")
        whatsapp = st.text_input("Numéro WhatsApp (ex: 2126000000)")
    with col2:
        date_debut = st.date_input("Date de début", datetime.now())
        duree = st.number_input("Durée (mois)", min_value=1, max_value=24, value=1)
    with col3:
        statut = st.selectbox("Statut", ["Actif", "Inactif", "En attente"])
    
    date_fin = calculer_date_fin(date_debut, duree)
    st.info(f"Date de fin prévue : {date_fin.strftime('%d/%m/%Y')}")
    
    submit = st.form_submit_button("💾 Enregistrer l'abonné")
    
    if submit:
        if nom and whatsapp:
            sauvegarder_dans_supabase(nom, date_debut, duree, date_fin, whatsapp, statut)
            charger_depuis_supabase() # Rafraîchir la liste
            st.rerun()
        else:
            st.warning("Veuillez remplir le nom et le numéro WhatsApp.")

# --- LISTE DES ABONNÉS ---
st.header("📋 Liste des Abonnés")
if not st.session_state['abonnés'].empty:
    st.dataframe(st.session_state['abonnés'], use_container_width=True)
else:
    st.info("Aucun abonné trouvé dans la base de données.")

if st.button("🔄 Forcer la synchronisation"):
    charger_depuis_supabase()
    st.rerun()
