import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime

# 1. CONNEXION SUPABASE (Sécurisée)
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("🚨 Configuration Supabase manquante dans les Secrets !")
    st.stop()

# 2. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="365 GYM & FITNESS", layout="wide", page_icon="💪")

# 3. INITIALISATION DU SESSION STATE
if 'admin' not in st.session_state:
    st.session_state['admin'] = False

# Fonction pour charger les données (Utilisée par l'Admin)
def charger_depuis_supabase():
    try:
        response = supabase.table("abonnes").select("*").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            # Mapping pour correspondre à ton ancien tableau
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

# 4. EN-TÊTE & LOGO
st.title("🏋️ 365 GYM & FITNESS")
# Ici, remplace par l'URL de ton logo réel
st.image("https://via.placeholder.com", use_container_width=True)

# 5. NAVIGATION PAR ONGLETS (Comme dans ton projet initial)
tab1, tab2, tab3 = st.tabs(["📝 Inscription", "🔐 Administration", "📲 Notifications"])

# --- TAB 1 : FORMULAIRE D'AJOUT (PUBLIC) ---
with tab1:
    st.header("Ajouter un nouvel abonné")
    with st.form("form_ajout", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom Complet")
            whatsapp = st.text_input("Numéro WhatsApp")
        with col2:
            date_debut = st.date_input("Date de début", datetime.now())
            duree = st.number_input("Durée (mois)", min_value=1, value=1)
        
        date_fin = date_debut + pd.DateOffset(months=duree)
        
        if st.form_submit_button("💾 Enregistrer"):
            if nom and whatsapp:
                data = {
                    "nom": nom, "date_debut": date_debut.strftime("%Y-%m-%d"),
                    "duree_mois": int(duree), "date_fin": date_fin.strftime("%Y-%m-%d"),
                    "whatsapp": str(whatsapp), "statut": "Actif"
                }
                supabase.table("abonnes").upsert(data, on_conflict="whatsapp").execute()
                st.success(f"✅ {nom} ajouté à la base de données !")
            else:
                st.warning("Remplissez tous les champs.")

# --- TAB 2 : ADMINISTRATION (FORMULAIRE ADMIN) ---
with tab2:
    if not st.session_state['admin']:
        pwd = st.text_input("Mot de passe Admin", type="password")
        if st.button("Accéder"):
            if pwd == "1980":
                st.session_state['admin'] = True
                st.rerun()
    else:
        st.header("Gestion des Abonnés")
        df_admin = charger_depuis_supabase()
        st.dataframe(df_admin, use_container_width=True)
        
        with st.expander("Modifier ou Supprimer un abonné"):
            # Formulaire de modification spécifique Admin
            nom_edit = st.selectbox("Sélectionner un abonné", df_admin["Nom"].tolist())
            col_a, col_b = st.columns(2)
            with col_a:
                nouveau_statut = st.selectbox("Changer Statut", ["Actif", "Inactif", "Suspendu"])
            with col_b:
                if st.button("🗑️ Supprimer définitivement"):
                    supabase.table("abonnes").delete().eq("nom", nom_edit).execute()
                    st.success("Supprimé !")
                    st.rerun()

# --- TAB 3 : NOTIFICATIONS (TWILIO PRÊT) ---
with tab3:
    st.header("Envoyer des rappels WhatsApp")
    if st.button("💾 Synchroniser avec Supabase pour les rappels"):
        df_sync = charger_depuis_supabase()
        st.write(df_sync)
        st.success("✅ Données prêtes pour l'envoi !")
    
    nom_notif = st.text_input("Nom du client à notifier")
    if st.button("📲 Envoyer Notification (Simulation)"):
        st.info(f"Envoi du message à {nom_notif} via Twilio...")
        # Ici viendra ton code Twilio
        st.success("Message envoyé !")
