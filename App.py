import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# ================= SUPABASE =================
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except:
    st.error("🚨 Configuration Supabase manquante !")
    st.stop()

# ================= CONFIG =================
st.set_page_config(page_title="365 GYM & FITNESS", layout="wide", page_icon="💪")

logo_path = "logo.png"

def afficher_logo(w=200):
    if os.path.exists(logo_path):
        st.image(logo_path, width=w)
    else:
        st.title("🏋️ 365 GYM & FITNESS")

# ================= DATA =================
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

# ================= SESSION =================
if "page" not in st.session_state:
    st.session_state.page = "Accueil"

if "logged" not in st.session_state:
    st.session_state.logged = False

if "edit" not in st.session_state:
    st.session_state.edit = None

# ================= CSS LAYOUT PAYSAGE =================
st.markdown("""
<style>
/* Body */
.stApp {
    background-color: #0b1c2c;
    color: white;
}

/* Conteneur principal en paysage */
.main-row {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: flex-start;
}

/* Colonne gauche */
.left-col {
    flex: 3;
    padding-right: 20px;
}

/* Colonne droite menu */
.right-col {
    flex: 1;
    position: sticky;
    top: 0;
    height: 100vh;
}

/* Menu boutons */
.menu-button {
    display: block;
    width: 100%;
    margin-bottom: 10px;
    background-color: #ff6b2c;
    color: white;
    border-radius: 5px;
    padding: 12px;
    font-weight: bold;
    text-align: center;
    border: none;
    font-size: 16px;
    cursor: pointer;
}
.menu-button:hover {
    background-color: #ff9c5c;
    color: white;
}

/* Hero */
.hero {
    background: linear-gradient(rgba(6,18,29,0.85), rgba(6,18,29,0.95)), url('logo.png');
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
    height: 400px;
    border-radius: 15px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
}
.hero h1 {
    font-size: 50px;
    color: white;
}
.hero p {
    color: #ff6b2c;
    font-size: 18px;
}
</style>
""", unsafe_allow_html=True)

# ================= LAYOUT =================
st.markdown('<div class="main-row">', unsafe_allow_html=True)

# -------------------- COLONNE GAUCHE --------------------
st.markdown('<div class="left-col">', unsafe_allow_html=True)
col_left = st.container()

with col_left:
    # ================= PAGE ACCUEIL =================
    if st.session_state.page == "Accueil":
        st.markdown("""
        <div class="hero">
            <div>
                <h1>365 GYM & FITNESS</h1>
                <p>Transforme ton corps. Dépasse tes limites.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        posts = charger_publicites()
        if posts:
            for p in posts:
                st.divider()
                if p.get("type")=="Photo" and p.get("url_media"):
                    st.image(p["url_media"], use_container_width=True)
                    st.caption(p.get("legende",""))
                elif p.get("type")=="Vidéo" and p.get("url_media"):
                    st.video(p["url_media"])
                    st.caption(p.get("legende",""))
                else:
                    st.subheader(p.get("legende","Annonce"))
        else:
            st.info("🔥 Bienvenue chez 365 GYM & FITNESS")

    # ================= PAGE ADMIN =================
    elif st.session_state.page == "Admin":
        if not st.session_state.logged:
            pwd = st.text_input("Mot de passe", type="password")
            if st.button("Se connecter"):
                if pwd=="1980":
                    st.session_state.logged = True
                    st.rerun()
                else:
                    st.error("❌ Mauvais code")
        else:
            afficher_logo(100)
            st.header("⚙️ Panneau Admin")

            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Inscriptions","📊 Membres","📣 Publier","⏳ Expirations J-3","❌ Expirés"])

            # -------- INSCRIPTIONS --------
            with tab1:
                df = charger_depuis_supabase()
                noms = ["--- NOUVEL ABONNÉ ---"] + df["nom"].tolist()
                choix = st.selectbox("Rechercher", noms)
                v_nom, v_wa, v_statut, v_duree = "", "", "Actif", 1
                if choix != "--- NOUVEL ABONNÉ ---":
                    l = df[df["nom"]==choix].iloc[0]
                    v_nom, v_wa, v_statut, v_duree = l["nom"], l["WhatsApp"], l["statut"], int(l["duree_mois"])
                with st.form("form_inscription", clear_on_submit=True):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        nom = st.text_input("Nom", value=v_nom)
                        wa = st.text_input("WhatsApp", value=v_wa)
                        stt = st.selectbox("Statut", ["Actif","Inactif"], index=0 if v_statut=="Actif" else 1)
                    with col_b:
                        debut = st.date_input("Début", datetime.now())
                        mois = st.number_input("Durée (mois)", min_value=1, value=v_duree)
                    fin = debut + pd.DateOffset(months=mois)
                    if st.form_submit_button("💾 ENREGISTRER"):
                        supabase.table("abonnes").upsert({
                            "nom": nom,
                            "date_debut": debut.strftime("%Y-%m-%d"),
                            "duree_mois": int(mois),
                            "date_fin": fin.strftime("%Y-%m-%d"),
                            "WhatsApp": wa,
                            "statut": stt
                        }, on_conflict="WhatsApp").execute()
                        st.success("✅ Enregistré !")
                        st.rerun()

            # -------- MEMBRES --------
            with tab2:
                st.dataframe(charger_depuis_supabase(), use_container_width=True)

            # -------- PUBLIER --------
            with tab3:
                t_pub = st.selectbox("Type", ["Photo","Vidéo","Message"])
                fichier = st.file_uploader("Choisir un média", type=["png","jpg","jpeg","mp4"])
                if fichier:
                    if t_pub=="Photo": st.image(fichier, width=300)
                    if t_pub=="Vidéo": st.video(fichier)
                with st.form("form_pub", clear_on_submit=True):
                    legende_txt = st.text_area("Légende")
                    if st.form_submit_button("📢 PUBLIER"):
                        if fichier:
                            nom_f = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{fichier.name}"
                            supabase.storage.from_("medias").upload(nom_f, fichier.getvalue())
                            res_url = supabase.storage.from_("medias").get_public_url(nom_f)
                            url_final = res_url if isinstance(res_url,str) else res_url.public_url
                            supabase.table("publicite").insert({"type":t_pub,"url_media":url_final,"legende":legende_txt}).execute()
                        else:
                            supabase.table("publicite").insert({"type":"Message","url_media":"","legende":legende_txt}).execute()
                        st.success("✅ Publication réussie !")
                        st.rerun()

            # -------- EXPIRATIONS J-3 --------
            with tab4:
                df_s = charger_depuis_supabase()
                if not df_s.empty:
                    df_s['date_fin_dt'] = pd.to_datetime(df_s['date_fin'])
                    df_s['restant'] = (df_s['date_fin_dt'] - pd.Timestamp(datetime.now().date())).dt.days
                    alerte = df_s[(df_s['restant']<=3) & (df_s['restant']>=0) & (df_s['statut'].str.lower()=="actif")]
                    for _, r in alerte.iterrows():
                        num_raw = "".join(filter(str.isdigit,str(r["WhatsApp"])))
                        num_final = "243" + (num_raw[1:] if num_raw.startswith("0") else num_raw if num_raw.startswith("243") else num_raw)
                        msg = f"Bonjour {r['nom']} ! Votre abonnement se termine le {r['date_fin']}."
                        wa_url = f"https://wa.me/{num_final}?text={urllib.parse.quote(msg)}"
                        st.markdown(f"🔔 **{r['nom']}** | Fin : {r['date_fin']}  👉 [Notifier sur WhatsApp]({wa_url})")
                        st.divider()

            # -------- EXPIRÉS --------
            with tab5:
                df_s = charger_depuis_supabase()
                if not df_s.empty:
                    df_s['date_fin_dt'] = pd.to_datetime(df_s['date_fin'])
                    df_s['restant'] = (df_s['date_fin_dt'] - pd.Timestamp(datetime.now().date())).dt.days
                    exp = df_s[df_s['restant']<0]
                    for _, r in exp.iterrows():
                        st.error(f"❌ {r['nom']} expiré depuis {abs(r['restant'])} jours")

st.markdown('</div>', unsafe_allow_html=True)  # close left-col
st.markdown('</div>', unsafe_allow_html=True)  # close main-row
