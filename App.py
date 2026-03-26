import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime
import os
import urllib.parse

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
        return pd.DataFrame(response.data) if response.data else pd.DataFrame(columns=["nom", "date_debut", "duree_mois", "date_fin", "WhatsApp", "statut"])
    except:
        return pd.DataFrame(columns=["nom", "date_debut", "duree_mois", "date_fin", "WhatsApp", "statut"])

def charger_publicites():
    try:
        # On récupère les posts (le plus récent en haut)
        response = supabase.table("publicite").select("*").order("id", desc=True).execute()
        return response.data if response.data else []
    except:
        return []

# 4. NAVIGATION
st.sidebar.title("🧭 Menu")
page = st.sidebar.radio("Navigation", ["📢 Page Publicité", "🔐 Gestion Admin"])

# --- PAGE 1 : PUBLICITÉ (LE FIL D'ACTUALITÉ) ---
if page == "📢 Page Publicité":
    afficher_logo(300)
    st.title("Bienvenue chez 365 GYM & FITNESS")
    
    posts = charger_publicites()
    if posts:
        for post in posts:
            with st.container():
                st.divider()
                # On affiche le média selon son type
                if post.get('type') == "Photo" and post.get('url_media'):
                    st.image(post['url_media'], caption=post.get('legende'), use_container_width=True)
                elif post.get('type') == "Vidéo" and post['url_media']:
                    st.video(post['url_media'])
                    st.caption(post.get('legende'))
                else:
                    st.subheader(post.get('legende', "Annonce"))
    else:
        st.info("### 🔥 Bienvenue !\nSuivez nos actualités ici.")

# --- PAGE 2 : GESTION ADMIN ---
elif page == "🔐 Gestion Admin":
    pwd = st.sidebar.text_input("🔑 Code d'accès", type="password")
    
    if pwd == "1980":
        afficher_logo(100)
        st.header("⚙️ Panneau de Contrôle Admin")
        
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Inscriptions", "📊 Liste Membres", "📣 Publier News", "⏳ Expirations J-3"])
        
        with tab1:
            with st.form("form_gestion", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    nom = st.text_input("Nom de l'abonné")
                    whatsapp_val = st.text_input("WhatsApp (Ex: 0812345678)")
                    statut_opt = st.selectbox("Statut", ["Actif", "Inactif"])
                with col2:
                    date_debut = st.date_input("Date début", datetime.now())
                    duree = st.number_input("Durée (mois)", min_value=1, value=1)
                
                date_fin_calc = date_debut + pd.DateOffset(months=duree)
                st.write(f"Fin prévue : **{date_fin_calc.strftime('%d/%m/%Y')}**")

                col_b1, col_b2, col_b3 = st.columns(3)
                data_pkg = {"nom": nom, "date_debut": date_debut.strftime("%Y-%m-%d"), "duree_mois": int(duree), "date_fin": date_fin_calc.strftime("%Y-%m-%d"), "WhatsApp": whatsapp_val, "statut": statut_opt}

                if col_b1.form_submit_button("➕ AJOUTER"):
                    if nom and whatsapp_val:
                        supabase.table("abonnes").upsert(data_pkg, on_conflict="WhatsApp").execute()
                        st.success(f"Ajouté : {nom}")

                if col_b2.form_submit_button("🔄 MODIFIER"):
                    if whatsapp_val:
                        supabase.table("abonnes").upsert(data_pkg, on_conflict="WhatsApp").execute()
                        st.success(f"Mis à jour : {nom}")

                if col_b3.form_submit_button("🗑️ SUPPRIMER"):
                    if whatsapp_val:
                        supabase.table("abonnes").delete().eq("WhatsApp", whatsapp_val).execute()
                        st.warning(f"Supprimé : {whatsapp_val}")

        with tab2:
            st.subheader("Base de données complète")
            df_view = charger_depuis_supabase()
            st.dataframe(df_view, use_container_width=True)

        with tab3:
                    with tab3:
            st.subheader("🚀 Publier sur la Page Publicité")
            t_pub = st.selectbox("Type", ["Photo", "Vidéo", "Message"])
            fichier = st.file_uploader("Choisir un fichier", type=["png", "jpg", "jpeg", "mp4"])
            
            if fichier:
                if t_pub == "Photo": st.image(fichier, width=300)
                if t_pub == "Vidéo": st.video(fichier)
            
            with st.form("form_pub_final", clear_on_submit=True):
                m_pub = st.text_area("Légende")
                if st.form_submit_button("📢 PUBLIER"):
                    if fichier:
                        try:
                            # ON NETTOIE LE NOM DU FICHIER POUR ÉVITER LES BUGS
                            safe_name = "".join(x for x in fichier.name if x.isalnum() or x in "._-")
                            nom_f = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{safe_name}"
                            
                            # --- ATTENTION : NOM DE TON SEAU ICI ---
                            nom_seau = "MEDIAS PUBLICS" # Vérifie bien s'il y a un É ou E
                            
                            # 1. ENVOI AU STORAGE
                            supabase.storage.from_(nom_seau).upload(
                                path=nom_f, 
                                file=fichier.getvalue()
                            )
                            
                            # 2. RÉCUPÉRATION DE L'URL
                            res_url = supabase.storage.from_(nom_seau).get_public_url(nom_f)
                            url_final = res_url if isinstance(res_url, str) else res_url.public_url
                            
                            # 3. ENREGISTREMENT DANS LA TABLE
                            supabase.table("publicite").insert({
                                "type": t_pub, 
                                "url_media": url_final, 
                                "legende": m_pub
                            }).execute()
                            
                            st.success("✅ BOUM ! C'est en ligne sur la page Publicité !")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erreur : {e}")
                    elif t_pub == "Message":
                         supabase.table("publicite").insert({"type": t_pub, "url_media": "", "legende": m_pub}).execute()
                         st.success("✅ Message posté !")
                         st.rerun()
                        
        with tab4:
            st.subheader("⏳ Relances WhatsApp RDC (J-3)")
            df_suivi = charger_depuis_supabase()
            if not df_suivi.empty:
                c_statut = next((c for c in df_suivi.columns if c.lower() == 'statut'), None)
                c_fin = next((c for c in df_suivi.columns if c.lower() in ['date_fin', 'date fin']), None)
                c_wa = next((c for c in df_suivi.columns if c.lower() == 'whatsapp'), None)
                c_nom = next((c for c in df_suivi.columns if c.lower() == 'nom'), None)
                if c_statut and c_fin:
                    auj = pd.Timestamp(datetime.now().date())
                    df_suivi['date_fin_dt'] = pd.to_datetime(df_suivi[c_fin])
                    df_suivi['restant'] = (df_suivi['date_fin_dt'] - auj).dt.days
                    alerte_df = df_suivi[(df_suivi['restant'] <= 3) & (df_suivi[c_statut].astype(str).str.lower() == 'actif')]
                    if not alerte_df.empty:
                        for _, row in alerte_df.iterrows():
                            num_raw = "".join(filter(str.isdigit, str(row[c_wa])))
                            num_f = "243" + (num_raw[1:] if num_raw.startswith("0") else num_raw if num_raw.startswith("243") else num_raw)
                            msg_wa = f"Bonjour {row[c_nom]} ! 👋\nC'est 365 GYM & FITNESS. Votre abonnement se termine le {row[c_fin]}."
                            wa_url = f"https://wa.me{num_f}?text={urllib.parse.quote(msg_wa)}"
                            st.write(f"🔔 **{row[c_nom]}** | Fin : {row[c_fin]}")
                            st.markdown(f"👉 [NOTIFIER SUR WHATSAPP]({wa_url})")
                            st.divider()

    elif pwd != "":
        st.error("❌ Code incorrect")
