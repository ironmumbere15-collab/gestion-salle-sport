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

# 2. CONFIGURATION PAGE
st.set_page_config(page_title="365 GYM & FITNESS", layout="wide", page_icon="💪")

# 🎨 DESIGN MODERNE
st.markdown("""
<style>
.stApp { background-color: #0b1c2c; color: white; }
section[data-testid="stSidebar"] { background-color: #06121d; }
.stButton>button {
    background-color: #f1c40f;
    color: black;
    border-radius: 8px;
    font-weight: bold;
}
h1, h2, h3 { color: #f1c40f; }
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

# NAVIGATION
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

# PAGE PUBLICITE
if page == "📢 Page Publicité":
    afficher_logo(300)
    st.title("Bienvenue chez 365 GYM & FITNESS")

    posts = charger_publicites()
    if posts:
        for post in posts:
            st.divider()
            if post.get('type') == "Photo":
                st.image(post['url_media'], caption=post.get('legende'), use_container_width=True)
            elif post.get('type') == "Vidéo":
                st.video(post['url_media'])
                st.caption(post.get('legende'))
            else:
                st.subheader(post.get('legende'))
    else:
        st.info("🔥 Nos Offres\n- 1 Mois : 300 DH\n- 12 Mois : 2500 DH")

# PAGE ADMIN
elif page == "🔐 Gestion Admin":
    pwd = st.sidebar.text_input("🔑 Code", type="password")

    if pwd == "1980":
        afficher_logo(100)
        st.header("⚙️ Admin")

        tab1, tab2, tab3, tab4 = st.tabs([
            "📝 Inscriptions",
            "📊 Membres",
            "📣 Publier",
            "⏳ Expirations"
        ])

        # -------- TAB 1 --------
        with tab1:
            df_selec = charger_depuis_supabase()

            liste_noms = ["--- NOUVEL ABONNÉ ---"] + df_selec["nom"].tolist()
            choix = st.selectbox("Rechercher :", liste_noms)

            if st.button("✏️ Modifier"):
                st.session_state["edit_nom"] = choix

            v_nom, v_wa, v_statut, v_duree = "", "", "Actif", 1

            if st.session_state.get("edit_nom") and st.session_state["edit_nom"] != "--- NOUVEL ABONNÉ ---":
                l = df_selec[df_selec["nom"] == st.session_state["edit_nom"]].iloc[0]
                v_nom, v_wa, v_statut, v_duree = l["nom"], l["WhatsApp"], l["statut"], int(l["duree_mois"])

            with st.form("form"):
                nom = st.text_input("Nom", value=v_nom)
                wa = st.text_input("WhatsApp", value=v_wa)
                stt = st.selectbox("Statut", ["Actif", "Inactif"])
                debut = st.date_input("Début", datetime.now())
                mois = st.number_input("Mois", 1, 24, v_duree)

                fin = pd.to_datetime(debut) + pd.DateOffset(months=int(mois))

                if st.form_submit_button("💾 Enregistrer"):
                    data = {
                        "nom": nom,
                        "date_debut": debut.strftime("%Y-%m-%d"),
                        "duree_mois": int(mois),
                        "date_fin": fin.strftime("%Y-%m-%d"),
                        "WhatsApp": wa,
                        "statut": stt
                    }
                    supabase.table("abonnes").upsert(data, on_conflict="WhatsApp").execute()
                    st.success("✅ OK")
                    st.rerun()

            # SUPPRIMER
            st.subheader("🗑️ Supprimer")
            if not df_selec.empty:
                nom_sup = st.selectbox("Choisir", df_selec["nom"].tolist())
                if st.button("❌ Supprimer"):
                    supabase.table("abonnes").delete().eq("nom", nom_sup).execute()
                    st.success("Supprimé")
                    st.rerun()

        # -------- TAB 2 --------
        with tab2:
            st.dataframe(charger_depuis_supabase(), use_container_width=True)

        # -------- TAB 3 --------
        with tab3:
            t_pub = st.selectbox("Type", ["Photo", "Vidéo", "Message"])
            fichier = st.file_uploader("Fichier", ["png", "jpg", "mp4"])

            if fichier:
                if t_pub == "Photo":
                    st.image(fichier)
                elif t_pub == "Vidéo":
                    st.video(fichier)

            with st.form("pub"):
                legende = st.text_area("Texte")

                if st.form_submit_button("Publier"):
                    if fichier:
                        nom_f = fichier.name
                        supabase.storage.from_("medias").upload(nom_f, fichier.getvalue())
                        url = supabase.storage.from_("medias").get_public_url(nom_f)

                        supabase.table("publicite").insert({
                            "type": t_pub,
                            "url_media": url,
                            "legende": legende
                        }).execute()
                    else:
                        supabase.table("publicite").insert({
                            "type": "Message",
                            "url_media": "",
                            "legende": legende
                        }).execute()

                    st.success("Publié")
                    st.rerun()

        # -------- TAB 4 --------
        with tab4:
            df = charger_depuis_supabase()

            if not df.empty:
                df['date_fin'] = pd.to_datetime(df['date_fin'])
                today = pd.Timestamp(datetime.now().date())
                df['restant'] = (df['date_fin'] - today).dt.days

                # ALERTES J-3
                st.subheader("⏳ Bientôt expirés")
                alert = df[(df['restant'] <= 3) & (df['restant'] >= 0)]

                for _, r in alert.iterrows():
                    num = "".join(filter(str.isdigit, str(r["WhatsApp"])))

                    if num.startswith("243"):
                        final = num
                    elif num.startswith("0"):
                        final = "243" + num[1:]
                    else:
                        final = "243" + num

                    msg = f"Bonjour {r['nom']} votre abonnement expire le {r['date_fin'].date()}"
                    url = f"https://wa.me/{final}?text={urllib.parse.quote(msg)}"

                    st.warning(f"{r['nom']} expire dans {r['restant']} jours")
                    st.markdown(f"[📩 WhatsApp]({url})")

                # EXPIRÉS
                st.subheader("🚫 Expirés")
                exp = df[df['restant'] < 0]

                for _, r in exp.iterrows():
                    st.error(f"{r['nom']} expiré depuis {abs(r['restant'])} jours")

    else:
        st.error("Code incorrect")
