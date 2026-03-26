import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime

# 1. CONNEXION SUPABASE
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("Configuration Supabase manquante dans les Secrets.")
    st.stop()

# 2. CONFIGURATION & STYLE
st.set_page_config(page_title="365 GYM & FITNESS", layout="wide", page_icon="💪")

# 3. INITIALISATION ADMIN
if 'admin' not in st.session_state:
    st.session_state['admin'] = False

# FONCTION CHARGEMENT
def charger_depuis_supabase():
    try:
        response = supabase.table("abonnes").select("*").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            df_final = pd.DataFrame()
            df_final["Nom"] = df["nom"]
            df_final["Date début"] = pd.to_datetime(df["date_debut"])
            df_final["Durée (mois)"] = df["duree_mois"]
            df_final["Date fin"] = pd.to_datetime(df["date_fin"])
            df_final["WhatsApp"] = df["whatsapp"]
            df_final["Statut"] = df["statut"]
            return df_final
        return pd.DataFrame(columns=["Nom", "Date début", "Durée (mois)", "Date fin", "WhatsApp", "Statut"])
    except:
        return pd.DataFrame(columns=["Nom", "Date début", "Durée (mois)", "Date fin", "WhatsApp", "Statut"])

# 4. BARRE LATÉRALE (NAVIGATION)
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Aller vers :", ["📢 Publicité & Offres", "🔐 Espace Gestion Admin"])

# --- PAGE 1 : PUBLICITÉ (PUBLIQUE) ---
if page == "📢 Publicité & Offres":
    st.markdown("<h1 style='text-align: center;'>🏋️ 365 GYM & FITNESS</h1>", unsafe_allow_html=True)
    st.image("https://via.placeholder.com", use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("### 1 MOIS\n**300 DH**\nAccès Illimité")
    with col2:
        st.success("### 3 MOIS\n**800 DH**\n+ 1 Séance Coaching")
    with col3:
        st.warning("### 12 MOIS\n**2500 DH**\nLe meilleur prix !")

# --- PAGE 2 : ESPACE GESTION (ADMIN UNIQUEMENT) ---
elif page == "🔐 Espace Gestion Admin":
    if not st.session_state['admin']:
        st.subheader("Connexion requise")
        pwd = st.sidebar.text_input("Mot de passe", type="password")
        if st.sidebar.button("Se connecter"):
            if pwd == "1980":
                st.session_state['admin'] = True
                st.rerun()
            else:
                st.error("Mot de passe incorrect")
    else:
        st.sidebar.success("Mode Admin Actif")
        if st.sidebar.button("Se déconnecter"):
            st.session_state['admin'] = False
            st.rerun()

        # Onglets à l'intérieur de l'espace Admin
        tab1, tab2, tab3 = st.tabs(["📝 Nouvel Abonné", "📋 Liste & Modif", "📲 Notifications"])

        with tab1:
            st.subheader("Inscrire un client")
            with st.form("ajout_admin", clear_on_submit=True):
                nom = st.text_input("Nom Complet")
                wa = st.text_input("WhatsApp (ex: 212...)")
                duree = st.number_input("Durée", 1)
                if st.form_submit_button("💾 Sauvegarder"):
                    fin = datetime.now() + pd.DateOffset(months=duree)
                    data = {"nom": nom, "date_debut": datetime.now().strftime("%Y-%m-%d"), 
                            "duree_mois": int(duree), "date_fin": fin.strftime("%Y-%m-%d"),
                            "whatsapp": wa, "statut": "Actif"}
                    supabase.table("abonnes").upsert(data, on_conflict="whatsapp").execute()
                    st.success("Client ajouté !")

        with tab2:
            st.subheader("Base de données")
            df = charger_depuis_supabase()
            st.dataframe(df, use_container_width=True)
            if st.button("🗑️ Supprimer un abonné"):
                 # Logique de suppression ici
                 pass

        with tab3:
            st.subheader("Rappels Twilio")
            st.write("Liste des abonnements arrivant à échéance...")
            if st.button("📲 Envoyer rappels"):
                st.warning("Twilio n'est pas encore configuré.")
