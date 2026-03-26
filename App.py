import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# ================== SUPABASE ==================
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except:
    st.error("🚨 Supabase non configuré !")
    st.stop()

# ================== PAGE ==================
st.set_page_config(page_title="365 GYM & FITNESS", layout="wide", page_icon="💪")

# ================== DESIGN IMAGE STYLE ==================
st.markdown("""
<style>

/* BACKGROUND GLOBAL */
.stApp {
    background-color: #0b1c2c;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: #06121d;
    padding-top: 20px;
}

/* MENU BUTTON STYLE */
.stButton>button {
    width: 100%;
    background: transparent;
    color: white;
    border: none;
    text-align: left;
    padding: 14px;
    font-size: 15px;
    border-radius: 8px;
}

.stButton>button:hover {
    background-color: #f1c40f;
    color: black;
}

/* CARD STYLE */
.block-container {
    background-color: #0f2538;
    padding: 2rem;
    border-radius: 15px;
}

/* TITRES */
h1, h2, h3 {
    color: #f1c40f;
}

/* INPUT */
input, textarea {
    border-radius: 8px !important;
}

</style>
""", unsafe_allow_html=True)

# ================== LOGO ==================
logo_path = "logo.png"

def afficher_logo(w=200):
    if os.path.exists(logo_path):
        st.image(logo_path, width=w)
    else:
        st.title("🏋️ 365 GYM & FITNESS")

# ================== DATA ==================
def charger_depuis_supabase():
    try:
        r = supabase.table("abonnes").select("*").execute()
        return pd.DataFrame(r.data) if r.data else pd.DataFrame(columns=["nom","date_debut","duree_mois","date_fin","WhatsApp","statut"])
    except:
        return pd.DataFrame(columns=["nom","date_debut","duree_mois","date_fin","WhatsApp","statut"])

def charger_publicites():
    try:
        r = supabase.table("publicite").select("*").order("id", desc=True).execute()
        return r.data if r.data else []
    except:
        return []

# ================== NAVIGATION ==================
if "page" not in st.session_state:
    st.session_state.page = "home"

st.sidebar.title("💎 365 GYM")

if st.sidebar.button("🏠 Accueil"):
    st.session_state.page = "home"
    st.rerun()

if st.sidebar.button("🔐 Admin"):
    st.session_state.page = "admin"
    st.rerun()

# ================== PAGE PUBLIC ==================
if st.session_state.page == "home":
    afficher_logo(250)
    st.title("Bienvenue chez 365 GYM")

    posts = charger_publicites()

    if posts:
        for p in posts:
            st.divider()
            if p["type"] == "Photo":
                st.image(p["url_media"], use_container_width=True)
                st.caption(p["legende"])
            elif p["type"] == "Vidéo":
                st.video(p["url_media"])
                st.caption(p["legende"])
            else:
                st.subheader(p["legende"])
    else:
        st.info("🔥 Offres disponibles")

# ================== ADMIN ==================
elif st.session_state.page == "admin":

    # LOGIN
    if "logged" not in st.session_state:
        st.session_state.logged = False

    if not st.session_state.logged:
        st.subheader("🔐 Connexion")

        pwd = st.text_input("Mot de passe", type="password")

        if st.button("Se connecter"):
            if pwd == "1980":
                st.session_state.logged = True
                st.rerun()
            else:
                st.error("Code incorrect")

    else:
        afficher_logo(100)

        if st.button("🚪 Déconnexion"):
            st.session_state.logged = False
            st.rerun()

        st.header("⚙️ Tableau de bord")

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Inscriptions",
            "Membres",
            "Publier",
            "Expirations",
            "Expirés"
        ])

        # -------- INSCRIPTIONS --------
        with tab1:
            df = charger_depuis_supabase()

            noms = ["---"] + df["nom"].tolist()
            choix = st.selectbox("Rechercher", noms)

            if st.button("Modifier"):
                st.session_state.edit = choix

            v_nom, v_wa, v_statut, v_mois = "", "", "Actif", 1

            if st.session_state.get("edit") and st.session_state.edit != "---":
                d = df[df["nom"] == st.session_state.edit].iloc[0]
                v_nom, v_wa, v_statut, v_mois = d["nom"], d["WhatsApp"], d["statut"], int(d["duree_mois"])

            with st.form("form"):
                nom = st.text_input("Nom", value=v_nom)
                wa = st.text_input("WhatsApp", value=v_wa)
                statut = st.selectbox("Statut", ["Actif","Inactif"])
                debut = st.date_input("Début", datetime.now())
                mois = st.number_input("Durée", 1, 24, v_mois)

                fin = pd.to_datetime(debut) + pd.DateOffset(months=int(mois))

                if st.form_submit_button("Enregistrer"):
                    supabase.table("abonnes").upsert({
                        "nom": nom,
                        "date_debut": debut.strftime("%Y-%m-%d"),
                        "duree_mois": int(mois),
                        "date_fin": fin.strftime("%Y-%m-%d"),
                        "WhatsApp": wa,
                        "statut": statut
                    }, on_conflict="WhatsApp").execute()

                    st.success("OK")
                    st.rerun()

            # SUPPRIMER
            st.subheader("Supprimer")
            if not df.empty:
                sup = st.selectbox("Choisir", df["nom"].tolist())
                if st.button("Supprimer"):
                    supabase.table("abonnes").delete().eq("nom", sup).execute()
                    st.success("Supprimé")
                    st.rerun()

        # -------- MEMBRES --------
        with tab2:
            st.dataframe(charger_depuis_supabase(), use_container_width=True)

        # -------- PUBLICATION --------
        with tab3:
            t = st.selectbox("Type", ["Photo","Vidéo","Message"])
            f = st.file_uploader("Fichier", ["png","jpg","mp4"])

            if f:
                if t == "Photo":
                    st.image(f)
                elif t == "Vidéo":
                    st.video(f)

            with st.form("pub"):
                txt = st.text_area("Texte")

                if st.form_submit_button("Publier"):
                    if f:
                        nom = f.name
                        supabase.storage.from_("medias").upload(nom, f.getvalue())
                        url = supabase.storage.from_("medias").get_public_url(nom)

                        supabase.table("publicite").insert({
                            "type": t,
                            "url_media": url,
                            "legende": txt
                        }).execute()
                    else:
                        supabase.table("publicite").insert({
                            "type": "Message",
                            "url_media": "",
                            "legende": txt
                        }).execute()

                    st.success("Publié")
                    st.rerun()

        # -------- EXPIRATION --------
        with tab4:
            df = charger_depuis_supabase()

            if not df.empty:
                df["date_fin"] = pd.to_datetime(df["date_fin"])
                today = pd.Timestamp(datetime.now().date())
                df["restant"] = (df["date_fin"] - today).dt.days

                alert = df[(df["restant"] <= 3) & (df["restant"] >= 0)]

                for _, r in alert.iterrows():
                    st.warning(f"{r['nom']} expire dans {r['restant']} jours")

        # -------- EXPIRÉS --------
        with tab5:
            df = charger_depuis_supabase()

            if not df.empty:
                df["date_fin"] = pd.to_datetime(df["date_fin"])
                today = pd.Timestamp(datetime.now().date())
                df["restant"] = (df["date_fin"] - today).dt.days

                exp = df[df["restant"] < 0]

                for _, r in exp.iterrows():
                    st.error(f"{r['nom']} expiré depuis {abs(r['restant'])} jours")
