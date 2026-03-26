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

# 3. GESTION DU LOGO (Nom corrigé en minuscules)
logo_path = "logo.png" 

def afficher_logo(largeur=200):
    if os.path.exists(logo_path):
        st.image(logo_path, width=largeur)
    else:
        st.info("🏋️ 365 GYM & FITNESS") # Texte de secours si l'image manque

# 4. FONCTIONS DE GESTION
# --- AJOUT DANS LES FONCTIONS (En haut du fichier) ---
def charger_publicites():
    try:
        response = supabase.table("publicite").select("*").order("created_at", desc=True).execute()
        return response.data if response.data else []
    except:
        return []

# --- MODIFICATION DE LA PAGE PUBLICITÉ (VISIBLE PAR TOUS) ---
if page == "📢 Page Publicité":
    afficher_logo(300)
    st.title("Bienvenue chez 365 GYM & FITNESS")
    
    # Affichage dynamique des posts enregistrés
    posts = charger_publicites()
    for post in posts:
        with st.container():
            st.divider()
            if post['type'] == "Photo":
                st.image(post['url_media'], caption=post['legende'], use_container_width=True)
            elif post['type'] == "Vidéo":
                st.video(post['url_media'])
                st.caption(post['legende'])
            else:
                st.info(f"### {post['legende']}")

# --- AJOUT DANS L'ESPACE ADMIN (DANS UN NOUVEL ONGLET) ---
elif page == "🔐 Gestion Abonnés (Admin)":
    pwd = st.sidebar.text_input("🔑 Code d'accès", type="password")
    if pwd == "1980":
        # On ajoute un 3ème onglet pour gérer la pub
        tab1, tab2, tab3 = st.tabs(["📝 Inscriptions", "📊 Liste Membres", "📣 Publier News"])
        
        with tab3:
            st.subheader("🚀 Publier sur la page d'accueil")
            with st.form("form_pub"):
                type_pub = st.selectbox("Type de contenu", ["Photo", "Vidéo", "Message Texte"])
                url_link = st.text_input("Lien URL du média (Image ou YouTube/Vimeo)")
                message = st.text_area("Légende ou Message à afficher")
                
                if st.form_submit_button("📢 Publier maintenant"):
                    data_pub = {"type": type_pub, "url_media": url_link, "legende": message}
                    supabase.table("publicite").insert(data_pub).execute()
                    st.success("C'est en ligne !")

            # Possibilité de supprimer les anciens posts
            st.divider()
            st.subheader("🗑️ Gérer les publications")
            all_pubs = charger_publicites()
            for p in all_pubs:
                col_p, col_d = st.columns([4, 1])
                col_p.write(f"{p['type']} : {p['legende'][:50]}...")
                if col_d.button("Supprimer", key=p['id']):
                    supabase.table("publicite").delete().eq("id", p['id']).execute()
                    st.rerun()

def charger_depuis_supabase():
    try:
        response = supabase.table("abonnes").select("*").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame(columns=["nom", "date_debut", "duree_mois", "date_fin", "whatsapp", "statut"])
    except:
        return pd.DataFrame(columns=["nom", "date_debut", "duree_mois", "date_fin", "whatsapp", "statut"])

# 5. NAVIGATION
page = st.sidebar.radio("Navigation", ["📢 Page Publicité", "🔐 Gestion Abonnés (Admin)"])

# --- PAGE 1 : PUBLICITÉ (VISIBLE PAR TOUS) ---
if page == "📢 Page Publicité":
    afficher_logo(300)
    st.title("Bienvenue chez 365 GYM & FITNESS")
    
    st.markdown("""
    ### 🔥 Nos Offres Exceptionnelles
    - **1 Mois** : 300 DH (Accès complet)
    - **3 Mois** : 800 DH (*Promotion*)
    - **12 Mois** : 2500 DH (*Meilleur prix*)
    """)
    st.info("📍 Situé au centre-ville - Ouvert 7j/7")

# --- PAGE 2 : GESTION ABONNÉS (AVEC MOT DE PASSE SYSTÉMATIQUE) ---
elif page == "🔐 Gestion Abonnés (Admin)":
    # Le mot de passe n'est pas stocké en session, il sera redemandé à chaque clic sur ce menu
    pwd = st.sidebar.text_input("🔑 Code d'accès", type="password")
    
    if pwd == "1980":
        afficher_logo(100)
        st.header("⚙️ Panneau de Contrôle Admin")
        
        tab1, tab2 = st.tabs(["📝 Enregistrement & Actions", "📊 Liste des Membres"])
        
        with tab1:
            st.subheader("Formulaire de Gestion")
            with st.form("form_gestion", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    nom = st.text_input("Nom de l'abonné")
                    whatsapp = st.text_input("Numéro WhatsApp (Identifiant unique)")
                    statut = st.selectbox("Statut", ["Actif", "Inactif"])
                with col2:
                    date_debut = st.date_input("Date début", datetime.now())
                    duree = st.number_input("Durée (mois)", min_value=1, value=1)
                
                date_fin = date_debut + pd.DateOffset(months=duree)
                st.write(f"Fin prévue : **{date_fin.strftime('%d/%m/%Y')}**")

                col_btn1, col_btn2, col_btn3 = st.columns(3)
                add_btn = col_btn1.form_submit_button("➕ AJOUTER")
                edit_btn = col_btn2.form_submit_button("🔄 MODIFIER")
                del_btn = col_btn3.form_submit_button("🗑️ SUPPRIMER")

            if add_btn or edit_btn:
                if nom and whatsapp:
                    data = {
                        "nom": nom, "date_debut": date_debut.strftime("%Y-%m-%d"),
                        "duree_mois": int(duree), "date_fin": date_fin.strftime("%Y-%m-%d"),
                        "whatsapp": whatsapp, "statut": statut
                    }
                    supabase.table("abonnes").upsert(data, on_conflict="whatsapp").execute()
                    st.success(f"Opération réussie pour {nom}")
                else:
                    st.error("Le nom et le WhatsApp sont obligatoires.")

            if del_btn:
                if whatsapp:
                    supabase.table("abonnes").delete().eq("whatsapp", whatsapp).execute()
                    st.warning(f"Abonné {whatsapp} supprimé.")
                else:
                    st.error("Entrez le numéro WhatsApp pour supprimer.")

        with tab2:
            st.subheader("Base de données")
            df_view = charger_depuis_supabase()
            if not df_view.empty:
                st.dataframe(df_view, use_container_width=True)
            else:
                st.info("La base de données est vide.")

    elif pwd != "":
        st.error("❌ Code incorrect")
