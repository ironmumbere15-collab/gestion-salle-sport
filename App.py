import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime

# 1. CONNEXION SUPABASE (Sécurisée via Secrets)
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("Configuration Supabase manquante dans les Secrets Streamlit.")
    st.stop()

# 2. CONFIGURATION DE LA PAGE & STYLE
st.set_page_config(page_title="365 GYM & FITNESS", layout="wide", page_icon="💪")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #FF4B4B; color: white; }
    .title-text { text-align: center; color: #1E1E1E; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. INITIALISATION DES DONNÉES
if 'admin' not in st.session_state:
    st.session_state['admin'] = False

# 4. FONCTIONS
def calculer_date_fin(date_debut, duree):
    return date_debut + pd.DateOffset(months=duree)

def sauvegarder_abonné(nom, debut, duree, fin, whatsapp, statut):
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
        st.error(f"Erreur lors de l'enregistrement : {e}")

def charger_abonnes():
    try:
        response = supabase.table("abonnes").select("*").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            # Mapping propre pour l'affichage
            df_display = pd.DataFrame()
            df_display["Nom"] = df["nom"]
            df_display["Date début"] = pd.to_datetime(df["date_debut"])
            df_display["Durée (mois)"] = df["duree_mois"]
            df_display["Date fin"] = pd.to_datetime(df["date_fin"])
            df_display["WhatsApp"] = df["whatsapp"]
            df_display["Statut"] = df["statut"]
            return df_display
        return pd.DataFrame(columns=["Nom", "Date début", "Durée (mois)", "Date fin", "WhatsApp", "Statut"])
    except:
        return pd.DataFrame(columns=["Nom", "Date début", "Durée (mois)", "Date fin", "WhatsApp", "Statut"])

# 5. EN-TÊTE ET LOGO
st.markdown("<h1 class='title-text'>🏋️ 365 GYM & FITNESS</h1>", unsafe_allow_html=True)
# Remplace l'URL ci-dessous par le lien de ton image si tu en as une
st.image("https://via.placeholder.com", use_container_width=True)

# 6. NAVIGATION
menu = st.sidebar.selectbox("Menu", ["Inscription Client", "Espace Admin"])

# --- PAGE 1 : INSCRIPTION CLIENT ---
if menu == "Inscription Client":
    st.header("📝 Inscription Nouvel Abonné")
    with st.form("form_public", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom complet")
            whatsapp = st.text_input("Numéro WhatsApp")
        with col2:
            date_debut = st.date_input("Date de début", datetime.now())
            duree = st.selectbox("Forfait", [1, 3, 6, 12], format_func=lambda x: f"{x} mois")
        
        date_fin = calculer_date_fin(date_debut, duree)
        st.info(f"Votre abonnement se terminera le : {date_fin.strftime('%d/%m/%Y')}")
        
        if st.form_submit_button("S'inscrire"):
            if nom and whatsapp:
                sauvegarder_abonné(nom, date_debut, duree, date_fin, whatsapp, "Actif")
            else:
                st.warning("Veuillez remplir tous les champs.")

# --- PAGE 2 : ESPACE ADMIN ---
elif menu == "Espace Admin":
    if not st.session_state['admin']:
        st.subheader("🔐 Accès Restreint")
        pwd = st.text_input("Mot de passe Admin", type="password")
        if st.button("Se connecter"):
            if pwd == "1980":
                st.session_state['admin'] = True
                st.rerun()
            else:
                st.error("Mot de passe incorrect")
    else:
        st.sidebar.button("Se déconnecter", on_click=lambda: st.session_state.update({"admin": False}))
        
        st.header("⚙️ Gestion des Abonnés")
        
        # Affichage de la liste
        df_admin = charger_abonnes()
        if not df_admin.empty:
            st.dataframe(df_admin, use_container_width=True)
            
            # Options Admin
            st.subheader("Actions rapides")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🔄 Actualiser la liste"):
                    st.rerun()
            with col_b:
                # Bouton pour exporter si besoin
                csv = df_admin.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Télécharger CSV", csv, "abonnes.csv", "text/csv")
        else:
            st.info("Aucun abonné enregistré pour le moment.")
