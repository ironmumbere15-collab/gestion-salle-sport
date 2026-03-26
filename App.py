import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime
import os

# 1. CONNEXION SUPABASE
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("🚨 Configuration Supabase manquante dans les Secrets !")
    st.stop()

# 2. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="365 GYM & FITNESS", layout="wide", page_icon="💪")

# 3. GESTION DU LOGO & FONCTIONS
logo_path = "logo.png" 

def afficher_logo(largeur=200):
    if os.path.exists(logo_path):
        st.image(logo_path, width=largeur)
    else:
        st.info("🏋️ 365 GYM & FITNESS")

def charger_depuis_supabase():
    try:
        response = supabase.table("abonnes").select("*").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame(columns=["nom", "date_debut", "duree_mois", "date_fin", "whatsapp", "statut"])
    except:
        return pd.DataFrame(columns=["nom", "date_debut", "duree_mois", "date_fin", "whatsapp", "statut"])

def charger_publicites():
    try:
        response = supabase.table("publicite").select("*").order("id", desc=True).execute()
        return response.data if response.data else []
    except:
        return []

# 4. NAVIGATION (Défini AVANT l'utilisation de la variable 'page')
st.sidebar.title("🧭 Menu")
page = st.sidebar.radio("Navigation", ["📢 Page Publicité", "🔐 Gestion Admin"])

# --- PAGE 1 : PUBLICITÉ (VISIBLE PAR TOUS) ---
if page == "📢 Page Publicité":
    afficher_logo(300)
    st.title("Bienvenue chez 365 GYM & FITNESS")
    
    # Affichage des posts dynamiques
    posts = charger_publicites()
    if posts:
        for post in posts:
            with st.container():
                st.divider()
                if post['type'] == "Photo":
                    st.image(post['url_media'], caption=post['legende'], use_container_width=True)
                elif post['type'] == "Vidéo":
                    st.video(post['url_media'])
                    st.caption(post['legende'])
                else:
                    st.subheader(post['legende'])
    else:
        st.info("### 🔥 Nos Offres Exceptionnelles\n- **1 Mois** : 300 DH\n- **12 Mois** : 2500 DH")

# --- PAGE 2 : GESTION ADMIN (MOT DE PASSE 1980) ---
elif page == "🔐 Gestion Admin":
    pwd = st.sidebar.text_input("🔑 Code d'accès", type="password")
    
    if pwd == "1980":
        afficher_logo(100)
        st.header("⚙️ Panneau de Contrôle Admin")
        
        tab1, tab2, tab3 = st.tabs(["📝 Inscriptions", "📊 Liste Membres", "📣 Publier News"])
        
        with tab1:
            with st.form("form_gestion", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    nom = st.text_input("Nom de l'abonné")
                    whatsapp = st.text_input("WhatsApp (Identifiant unique)")
                    statut = st.selectbox("Statut", ["Actif", "Inactif"])
                with col2:
                    date_debut = st.date_input("Date début", datetime.now())
                    duree = st.number_input("Durée (mois)", min_value=1, value=1)
                
                date_fin = date_debut + pd.DateOffset(months=duree)
                st.write(f"Fin prévue : **{date_fin.strftime('%d/%m/%Y')}**")

                col_b1, col_b2, col_b3 = st.columns(3)
                if col_b1.form_submit_button("➕ AJOUTER"):
                    data = {"nom": nom, "date_debut": date_debut.strftime("%Y-%m-%d"), "duree_mois": int(duree), "date_fin": date_fin.strftime("%Y-%m-%d"), "whatsapp": whatsapp, "statut": statut}
                    supabase.table("abonnes").upsert(data, on_conflict="whatsapp").execute()
                    st.success(f"Ajouté : {nom}")

                if col_b2.form_submit_button("🔄 MODIFIER"):
                    data = {"nom": nom, "date_debut": date_debut.strftime("%Y-%m-%d"), "duree_mois": int(duree), "date_fin": date_fin.strftime("%Y-%m-%d"), "whatsapp": whatsapp, "statut": statut}
                    supabase.table("abonnes").upsert(data, on_conflict="whatsapp").execute()
                    st.success(f"Mis à jour : {nom}")

                if col_b3.form_submit_button("🗑️ SUPPRIMER"):
                    supabase.table("abonnes").delete().eq("whatsapp", whatsapp).execute()
                    st.warning(f"Supprimé : {whatsapp}")

        with tab2:
            df_view = charger_depuis_supabase()
            st.dataframe(df_view, use_container_width=True)

        with tab3:
            st.subheader("🚀 Publier sur la page d'accueil")
            with st.form("form_pub"):
                t_pub = st.selectbox("Type", ["Photo", "Vidéo", "Message"])
                u_pub = st.text_input("Lien URL (Image ou Vidéo YouTube)")
                m_pub = st.text_area("Légende ou Message")
                if st.form_submit_button("📢 Publier"):
                    supabase.table("publicite").insert({"type": t_pub, "url_media": u_pub, "legende": m_pub}).execute()
                    st.success("Posté !")
                    st.rerun()

    elif pwd != "":
        st.error("❌ Code incorrect")
