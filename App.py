import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# 1. SUPABASE CONNECTION
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("🚨 Configuration Supabase manquante dans les Secrets !")
    st.stop()

# 2. PAGE CONFIGURATION
st.set_page_config(page_title="365 GYM & FITNESS", layout="wide", page_icon="💪")

# 3. LOGO & FUNCTIONS
logo_path = "logo.png" 

def afficher_logo(largeur=200):
    if os.path.exists(logo_path):
        st.image(logo_path, width=largeur)
    else:
        st.info("🏋️ 365 GYM & FITNESS")

def charger_depuis_supabase():
    try:
        response = supabase.table("abonnes").select("*").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame(columns=["nom", "date_debut", "duree_mois", "date_fin", "WhatsApp", "statut"])
    except:
        return pd.DataFrame(columns=["nom", "date_debut", "duree_mois", "date_fin", "WhatsApp", "statut"])

def charger_publicites():
    try:
        # We fetch all rows and sort them by the newest ID first
        response = supabase.table("publicite").select("*").order("id", desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        st.sidebar.error(f"Erreur de chargement Pub: {e}")
        return []

# 4. NAVIGATION
st.sidebar.title("🧭 Menu")
page = st.sidebar.radio("Navigation", ["📢 Page Publicité", "🔐 Gestion Admin"])

# --- PAGE 1: PUBLICITÉ (VISIBLE TO ALL) ---
if page == "📢 Page Publicité":
    afficher_logo(300)
    st.title("Bienvenue chez 365 GYM & FITNESS")
    
    posts = charger_publicites()
    if posts:
        for post in posts:
            with st.container():
                st.divider()
                if post.get('type') == "Photo" and post.get('url_media'):
                    st.image(post['url_media'], caption=post.get('legende', ""), use_container_width=True)
                elif post.get('type') == "Vidéo" and post.get('url_media'):
                    st.video(post['url_media'])
                    st.caption(post.get('legende', ""))
                else:
                    # Default to text if no media or type 'Message'
                    st.subheader(post.get('legende', "Message sans contenu"))
    else:
        st.info("### 🔥 Offre de Lancement\nSoyez les bienvenus ! Les nouvelles offres arrivent bientôt.")

# --- PAGE 2: ADMIN MANAGEMENT ---
elif page == "🔐 Gestion Admin":
    pwd = st.sidebar.text_input("🔑 Code d'accès", type="password")
    
    if pwd == "1980":
        afficher_logo(100)
        st.header("⚙️ Panneau de Contrôle Admin")
        
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Inscriptions", "📊 Liste Membres", "📣 Publier News", "⏳ Expirations J-3"])
        
        # [TAB 1, 2, 4 Logic remains the same as your working version...]
        with tab1:
            st.subheader("📝 Gérer les Membres")
            df_selec = charger_depuis_supabase()
            liste_noms = ["--- NOUVEL ABONNÉ ---"] + df_selec["nom"].tolist()
            choix = st.selectbox("Sélectionner un membre :", liste_noms)
            # (Rest of form logic...)

        with tab3:
            st.subheader("🚀 Publier sur la Page Publique")
            with st.form("form_pub", clear_on_submit=True):
                t_pub = st.selectbox("Type de Média", ["Photo", "Vidéo", "Message"])
                fichier = st.file_uploader("Importer une Photo ou Vidéo", type=["png", "jpg", "jpeg", "mp4"])
                m_pub = st.text_area("Légende / Texte")
                
                if st.form_submit_button("📢 PUBLIER MAINTENANT"):
                    if fichier:
                        try:
                            # 1. Generate unique filename
                            nom_f = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{fichier.name}"
                            # 2. Upload to Storage
                            supabase.storage.from_("publicite_media").upload(nom_f, fichier.getvalue())
                            # 3. GET DIRECT PUBLIC URL
                            url_res = supabase.storage.from_("publicite_media").get_public_url(nom_f)
                            # 4. Insert into the database table 'publicite'
                            data_to_save = {
                                "type": t_pub,
                                "url_media": url_res,
                                "legende": m_pub
                            }
                            supabase.table("publicite").insert(data_to_save).execute()
                            st.success("✅ Publié avec succès ! Allez voir la Page Publicité.")
                        except Exception as e:
                            st.error(f"Erreur lors de la publication : {e}")
                    elif t_pub == "Message" and m_pub:
                        supabase.table("publicite").insert({"type": t_pub, "url_media": "", "legende": m_pub}).execute()
                        st.success("✅ Message publié !")
                    else:
                        st.warning("Veuillez sélectionner un fichier ou écrire un message.")

        # [Other tabs omitted for brevity, but they should stay in your code]
    elif pwd != "":
        st.error("❌ Code incorrect")
