import streamlit as st
from supabase import create_client, Client
import pandas as pd

# 1. RÉCUPÉRATION SÉCURISÉE DES SECRETS (Correction des KeyErrors)
# On utilise les noms des "tiroirs" définis dans Streamlit Cloud
try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("Erreur de configuration Supabase. Vérifie tes Secrets Streamlit !")
    st.stop()

# 2. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="365 GYM & FITNESS", layout="wide", page_icon="💪")

# 3. INITIALISATION DU SESSION STATE
if 'admin' not in st.session_state:
    st.session_state['admin'] = False

if 'abonnés' not in st.session_state:
    # On crée un DataFrame vide par défaut
    st.session_state['abonnés'] = pd.DataFrame(columns=[
        "Nom", "Date début", "Durée (mois)", "Date fin", "WhatsApp", "Statut"
    ])

# 4. VARIABLES GLOBALES
ADMIN_PASSWORD = "1980"

# 5. FONCTIONS
def calculer_date_fin(date_debut, duree):
    return date_debut + pd.DateOffset(months=duree)

def notifier_whatsapp(nom):
    st.success(f"Message WhatsApp envoyé à {nom} (simulation)")

def sync_abonnes_to_supabase():
    df = st.session_state['abonnés']
    if not df.empty:
        for _, row in df.iterrows():
            supabase.table("abonnes").upsert({
                "nom": row["Nom"],
                "date_debut": row["Date début"].strftime("%Y-%m-%d"),
                "duree_mois": int(row["Durée (mois)"]),
                "date_fin": row["Date fin"].strftime("%Y-%m-%d"),
                "whatsapp": str(row["WhatsApp"]),
                "statut": row["Statut"]
            }, on_conflict="whatsapp").execute()
        st.success("✅ Base de données Supabase mise à jour !")
    else:
        st.warning("Rien à synchroniser, la liste est vide.")

def charger_abonnes_depuis_supabase():
    try:
        response = supabase.table("abonnes").select("*").execute()
        data = response.data
        if data:
            df = pd.DataFrame(data)
            # Mapping des colonnes DB vers l'affichage App
            df_display = pd.DataFrame()
            df_display["Nom"] = df["nom"]
            df_display["Date début"] = pd.to_datetime(df["date_debut"])
            df_display["Durée (mois)"] = df["duree_mois"]
            df_display["Date fin"] = pd.to_datetime(df["date_fin"])
            df_display["WhatsApp"] = df["whatsapp"]
            df_display["Statut"] = df["statut"]
            st.session_state['abonnés'] = df_display
    except Exception as e:
        st.error(f"Erreur lors du chargement : {e}")

# Lancement du chargement au démarrage
if st.session_state['abonnés'].empty:
    charger_abonnes_depuis_supabase()

# 6. INTERFACE (Exemple simple pour tester)
st.title("🏋️ 365 GYM & FITNESS")
if st.button("🔄 Rafraîchir depuis la base"):
    charger_abonnes_depuis_supabase()
    st.rerun()

st.table(st.session_state['abonnés'])
