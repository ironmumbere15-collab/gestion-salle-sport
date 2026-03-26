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

# 🎨 DESIGN (comme ton image)
st.markdown("""
<style>
.stApp {
    background-color: #0b1c2c;
    color: white;
}
section[data-testid="stSidebar"] {
    background-color: #06121d;
    width: 260px !important;
}
.stButton>button {
    width: 100%;
    background-color: transparent;
    color: white;
    border: none;
    text-align: left;
    padding: 15px;
    font-size: 16px;
}
.stButton>button:hover {
    background-color: #f1c40f;
    color: black;
}
.block-container {
    background-color: #0f2538;
    padding: 2rem;
    border-radius: 10px;
}
h1, h2, h3 {
    color: #f1c40f;
}
</style>
""", unsafe_allow_html=True)

# 3. LOGO
logo_path = "logo.png"

def afficher_logo(largeur=200):
    if os.path.exists(logo_path):
        st.image(logo_path, width=largeur)
    else:
        st.info("🏋️ 365 GYM & FITNESS")

# 4. DATA
def charger_depuis_supabase():
    try:
        response = supabase.table("abonnes").select("*").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame(columns=["nom", "date_debut", "duree_mois", "date_fin", "WhatsApp", "statut"])
    except:
        return pd.DataFrame(columns=["nom", "date_debut", "duree_mois", "date_fin", "WhatsApp", "statut"])

def charger_publicites():
    try:
        response = supabase.table("publicite").select("*").order("id", desc=True).execute()
        return response.data if response.data else []
    except:
        return []

# 5. NAVIGATION
if 'page' not in st.session_state:
    st.session_state['page'] = "📢 Page Publicité"

st.sidebar.title("💎 365 GYM MENU")

if st.sidebar.button("📢 PAGE PUBLICITÉ", use_container_width=True):
    st.session_state['page'] = "📢 Page Publicité"
    st.rerun()

if st.sidebar.button("🔐 GESTION ADMIN", use_container_width=True):
    st.session_state['page'] = "🔐 Gestion Admin"
    st.rerun()

page = st.session_state['page']

# --- PAGE 1 : PUBLICITÉ ---
if page == "📢 Page Publicité":
    afficher_logo(300)
    st.title("Bienvenue chez 365 GYM & FITNESS")
    
    posts = charger_publicites()
    if posts:
        for post in posts:
            with st.container():
                st.divider()
                if post.get('type') == "Photo" and post.get('url_media'):
                    st.image(post['url_media'], caption=post.get('legende'), use_container_width=True)
                elif post.get('type') == "Vidéo" and post.get('url_media'):
                    st.video(post['url_media'])
                    st.caption(post.get('legende'))
                else:
                    st.subheader(post.get('legende', "Annonce"))
    else:
        st.info("### 🔥 Nos Offres\n- **1 Mois** : 300 DH\n- **12 Mois** : 2500 DH")

# --- PAGE 2 : GESTION ADMIN ---
elif page == "🔐 Gestion Admin":

    # 🔐 LOGIN PRO
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.subheader("🔐 Connexion Admin")

        pwd = st.text_input("Mot de passe", type="password")

        if st.button("Se connecter"):
            if pwd == "1980":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("❌ Code incorrect")

    else:
        afficher_logo(100)
        st.header("⚙️ Panneau de Contrôle Admin")

        if st.button("🚪 Déconnexion"):
            st.session_state.logged_in = False
            st.rerun()
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📝 Inscriptions",
            "📊 Liste Membres",
            "📣 Publier News",
            "⏳ Expirations J-3",
            "🚫 Expirés"
        ])
        
        with tab1:
            st.subheader("📝 Gérer les Membres")
            df_selec = charger_depuis_supabase()
            liste_noms = ["--- NOUVEL ABONNÉ ---"] + df_selec["nom"].tolist()
            choix = st.selectbox("Rechercher :", liste_noms)
            
            if st.button("✏️ Modifier"):
                st.session_state["edit_nom"] = choix
            
            v_nom, v_wa, v_statut, v_duree = "", "", "Actif", 1
            
            if st.session_state.get("edit_nom") and st.session_state["edit_nom"] != "--- NOUVEL ABONNÉ ---":
                l = df_selec[df_selec["nom"] == st.session_state["edit_nom"]].iloc[0]
                v_nom, v_wa, v_statut, v_duree = l["nom"], l["WhatsApp"], l["statut"], int(l["duree_mois"])

            with st.form("form_gestion", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    nom = st.text_input("Nom", value=v_nom)
                    wa = st.text_input("WhatsApp", value=v_wa)
                    stt = st.selectbox("Statut", ["Actif", "Inactif"], index=0 if v_statut == "Actif" else 1)
                with col2:
                    debut = st.date_input("Début", datetime.now())
                    mois = st.number_input("Mois", min_value=1, value=v_duree)
                
                fin = pd.to_datetime(debut) + pd.DateOffset(months=int(mois))

                if st.form_submit_button("💾 ENREGISTRER"):
                    data = {
                        "nom": nom,
                        "date_debut": debut.strftime("%Y-%m-%d"),
                        "duree_mois": int(mois),
                        "date_fin": fin.strftime("%Y-%m-%d"),
                        "WhatsApp": wa,
                        "statut": stt
                    }
                    supabase.table("abonnes").upsert(data, on_conflict="WhatsApp").execute()
                    st.success("✅ Enregistré !")
                    st.rerun()

            # SUPPRIMER
            st.subheader("🗑️ Supprimer un abonné")
            if not df_selec.empty:
                nom_sup = st.selectbox("Choisir à supprimer", df_selec["nom"].tolist())
                if st.button("❌ SUPPRIMER"):
                    supabase.table("abonnes").delete().eq("nom", nom_sup).execute()
                    st.success(f"{nom_sup} supprimé !")
                    st.rerun()

        with tab2:
            st.dataframe(charger_depuis_supabase(), use_container_width=True)

        with tab3:
            st.subheader("🚀 Publier un Média")
            t_pub = st.selectbox("Type", ["Photo", "Vidéo", "Message"])
            fichier = st.file_uploader("Choisir un média", type=["png", "jpg", "jpeg", "mp4"])
            
            if fichier:
                if t_pub == "Photo": st.image(fichier, width=300)
                if t_pub == "Vidéo": st.video(fichier)
            
            with st.form("form_pub_final", clear_on_submit=True):
                legende_txt = st.text_area("Légende")
                if st.form_submit_button("📢 PUBLIER"):
                    if fichier:
                        nom_seau = "medias" 
                        nom_f = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{fichier.name}"
                        supabase.storage.from_(nom_seau).upload(nom_f, fichier.getvalue())
                        res_url = supabase.storage.from_(nom_seau).get_public_url(nom_f)
                        url_final = res_url if isinstance(res_url, str) else res_url.public_url
                        supabase.table("publicite").insert({"type": t_pub, "url_media": url_final, "legende": legende_txt}).execute()
                    else:
                        supabase.table("publicite").insert({"type": t_pub, "url_media": "", "legende": legende_txt}).execute()
                    
                    st.success("✅ Publication réussie !")
                    st.rerun()

        with tab4:
            st.subheader("⏳ Relances WhatsApp (J-3)")
            df_s = charger_depuis_supabase()
            if not df_s.empty:
                df_s['date_fin'] = pd.to_datetime(df_s['date_fin'])
                today = pd.Timestamp(datetime.now().date())
                df_s['restant'] = (df_s['date_fin'] - today).dt.days

                alerte = df_s[(df_s['restant'] <= 3) & (df_s['restant'] >= 0)]

                for _, r in alerte.iterrows():
                    num_raw = "".join(filter(str.isdigit, str(r["WhatsApp"])))

                    if num_raw.startswith("243"):
                        num_final = num_raw
                    elif num_raw.startswith("0"):
                        num_final = "243" + num_raw[1:]
                    else:
                        num_final = "243" + num_raw

                    msg = f"Bonjour {r['nom']} ! 👋 Votre abonnement se termine le {r['date_fin'].date()}."
                    wa_url = f"https://wa.me/{num_final}?text={urllib.parse.quote(msg)}"

                    st.warning(f"{r['nom']} expire dans {r['restant']} jours")
                    st.markdown(f"[📩 WhatsApp]({wa_url})")

        with tab5:
            st.subheader("🚫 Abonnements Expirés")

            df_s = charger_depuis_supabase()
            if not df_s.empty:
                df_s['date_fin'] = pd.to_datetime(df_s['date_fin'])
                today = pd.Timestamp(datetime.now().date())
                df_s['restant'] = (df_s['date_fin'] - today).dt.days

                expires = df_s[df_s['restant'] < 0]

                if not expires.empty:
                    for _, r in expires.iterrows():
                        st.error(f"❌ {r['nom']} | Expiré depuis {abs(r['restant'])} jours")
                else:
                    st.success("✅ Aucun expiré")
