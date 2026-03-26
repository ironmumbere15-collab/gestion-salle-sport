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
        # On récupère les pubs de la table 'publicite' (Newest first)
        response = supabase.table("publicite").select("*").order("id", desc=True).execute()
        return response.data if response.data else []
    except:
        return []

# 4. NAVIGATION
st.sidebar.title("🧭 Menu")
page = st.sidebar.radio("Navigation", ["📢 Page Publicité", "🔐 Gestion Admin"])

# --- PAGE 1 : PUBLICITÉ (DYNAMIQUE) ---
if page == "📢 Page Publicité":
    afficher_logo(300)
    st.title("Bienvenue chez 365 GYM & FITNESS")
    
    # AFFICHAGE DES NEWS POSTÉES DEPUIS L'ADMIN
    posts = charger_publicites()
    if posts:
        for post in posts:
            with st.container():
                st.divider()
                if post['type'] == "Photo" and post['url_media']:
                    st.image(post['url_media'], caption=post['legende'], use_container_width=True)
                elif post['type'] == "Vidéo" and post['url_media']:
                    st.video(post['url_media'])
                    st.caption(post['legende'])
                else:
                    st.subheader(post['legende'])
    else:
        st.info("### 🔥 Nos Offres Exceptionnelles\n- **1 Mois** : 300 DH\n- **12 Mois** : 2500 DH")

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
                
                date_fin_calculed = date_debut + pd.DateOffset(months=duree)
                st.write(f"Fin prévue : **{date_fin_calculed.strftime('%d/%m/%Y')}**")

                col_b1, col_b2, col_b3 = st.columns(3)
                data_package = {"nom": nom, "date_debut": date_debut.strftime("%Y-%m-%d"), "duree_mois": int(duree), "date_fin": date_fin_calculed.strftime("%Y-%m-%d"), "WhatsApp": whatsapp_val, "statut": statut_opt}

                if col_b1.form_submit_button("➕ AJOUTER"):
                    if nom and whatsapp_val:
                        supabase.table("abonnes").upsert(data_package, on_conflict="WhatsApp").execute()
                        st.success(f"Ajouté : {nom}")
                    else:
                        st.error("Nom et WhatsApp obligatoires.")

                if col_b2.form_submit_button("🔄 MODIFIER"):
                    if whatsapp_val:
                        supabase.table("abonnes").upsert(data_package, on_conflict="WhatsApp").execute()
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
            st.subheader("🚀 Publier un Média (Galerie)")
            with st.form("form_pub", clear_on_submit=True):
                t_pub = st.selectbox("Type", ["Photo", "Vidéo", "Message"])
                fichier = st.file_uploader("Choisir un fichier", type=["png", "jpg", "jpeg", "mp4"])
                m_pub = st.text_area("Légende")
                
                if st.form_submit_button("📢 Publier"):
                    if fichier:
                        nom_f = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{fichier.name}"
                        supabase.storage.from_("publicite_media").upload(nom_f, fichier.getvalue())
                        # Récupération URL publique
                        res = supabase.storage.from_("publicite_media").get_public_url(nom_f)
                        url_finale = res if isinstance(res, str) else res.public_url
                        
                        supabase.table("publicite").insert({"type": t_pub, "url_media": url_finale, "legende": m_pub}).execute()
                        st.success("✅ Publication réussie !")
                        st.rerun()
                    elif t_pub == "Message" and m_pub:
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
                    aujourdhui = pd.Timestamp(datetime.now().date())
                    df_suivi['date_fin_dt'] = pd.to_datetime(df_suivi[c_fin])
                    df_suivi['restant'] = (df_suivi['date_fin_dt'] - aujourdhui).dt.days
                    
                    alerte_df = df_suivi[(df_suivi['restant'] <= 3) & (df_suivi[c_statut].astype(str).str.lower() == 'actif')]
                    
                    if not alerte_df.empty:
                        for _, row in alerte_df.iterrows():
                            num_raw = "".join(filter(str.isdigit, str(row[c_wa])))
                            num_final = "243" + (num_raw[1:] if num_raw.startswith("0") else num_raw if num_raw.startswith("243") else num_raw)
                            msg = f"Bonjour {row[c_nom]} ! 👋\nC'est 365 GYM & FITNESS. Votre abonnement se termine le {row[c_fin]}."
                            wa_url = f"https://wa.me{num_final}?text={urllib.parse.quote(msg)}"
                            st.write(f"🔔 **{row[c_nom]}** | Fin : {row[c_fin]}")
                            st.markdown(f"👉 [NOTIFIER SUR WHATSAPP]({wa_url})")
                            st.divider()
    elif pwd != "":
        st.error("❌ Code incorrect")
