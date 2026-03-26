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

        # --- NOUVEL ONGLET : RAPPELS EXPIRATION ---
        with tab3: # Ou crée un tab4 si tu veux garder l'onglet Publier séparé
            st.subheader("⚠️ Abonnements arrivant à expiration (J-3)")
            
            df_suivi = charger_depuis_supabase()
            
            if not df_suivi.empty:
                # 1. Calculer les jours restants
                aujourdhui = pd.Timestamp(datetime.now().date())
                df_suivi['Date fin'] = pd.to_datetime(df_suivi['date_fin'])
                df_suivi['Jours restants'] = (df_suivi['Date fin'] - aujourdhui).dt.days
                
                # 2. Filtrer ceux qui expirent dans 3 jours ou moins (et qui sont encore Actifs)
                alerte_df = df_suivi[(df_suivi['Jours restants'] <= 3) & (df_suivi['statut'] == 'Actif')]
                
                if not alerte_df.empty:
                    for index, row in alerte_df.iterrows():
                        col_info, col_action = st.columns([3, 1])
                        
                        jours = row['Jours restants']
                        couleur = "🔴" if jours < 0 else "🟠"
                        etat = "Expiré" if jours < 0 else f"Expire dans {jours} jours"
                        
                        col_info.write(f"{couleur} **{row['nom']}** ({etat}) - Fin le : {row['Date fin'].strftime('%d/%m/%Y')}")
                        
                        # 3. BOUTON WHATSAPP MAGIQUE
                        # On prépare le message automatique
                        msg = f"Bonjour {row['nom']}, c'est 365 GYM & FITNESS. Votre abonnement arrive à terme le {row['Date fin'].strftime('%d/%m/%Y')}. Pensez à vous réabonner pour continuer vos séances ! 💪"
                        
                        # Création du lien WhatsApp (format international sans le +)
                        wa_link = f"https://wa.me{row['whatsapp']}?text={msg.replace(' ', '%20')}"
                        
                        col_action.markdown(f"[📲 Notifier]({wa_link})")
                    
                    st.divider()
                    st.info("💡 En cliquant sur 'Notifier', votre WhatsApp s'ouvrira avec le message déjà prêt.")
                else:
                    st.success("✅ Aucun abonnement n'expire dans les 3 prochains jours.")
            else:
                st.info("La base de données est vide.")

# 4. NAVIGATION
st.sidebar.title("🧭 Menu")
page = st.sidebar.radio("Navigation", ["📢 Page Publicité", "🔐 Gestion Admin"])

# --- PAGE 1 : PUBLICITÉ (VISIBLE PAR TOUS) ---
if page == "📢 Page Publicité":
    afficher_logo(300)
    st.title("Bienvenue chez 365 GYM & FITNESS")
    
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
            st.subheader("🚀 Publier un Média (Galerie)")
            with st.form("form_pub", clear_on_submit=True):
                t_pub = st.selectbox("Type", ["Photo", "Vidéo", "Message"])
                fichier = st.file_uploader("Choisir un fichier", type=["png", "jpg", "jpeg", "mp4"])
                m_pub = st.text_area("Légende")
                
                if st.form_submit_button("📢 Publier"):
                    if fichier:
                        nom_f = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{fichier.name}"
                        # Envoi au Bucket
                        supabase.storage.from_("publicite_media").upload(nom_f, fichier.getvalue())
                        url_pub = supabase.storage.from_("publicite_media").get_public_url(nom_f)
                        # Enregistrement Table
                        supabase.table("publicite").insert({"type": t_pub, "url_media": url_pub, "legende": m_pub}).execute()
                        st.success("C'est en ligne !")
                        st.rerun()
                    elif t_pub == "Message" and m_pub:
                        supabase.table("publicite").insert({"type": t_pub, "url_media": "", "legende": m_pub}).execute()
                        st.success("Message posté !")
                        st.rerun()

    elif pwd != "":
        st.error("❌ Code incorrect")
