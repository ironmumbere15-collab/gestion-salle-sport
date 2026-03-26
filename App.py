import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# ================= CONFIG & DESIGN (LOOK ADVENTURE) =================
st.set_page_config(page_title="365 GYM & FITNESS", layout="wide", page_icon="💪")

# Couleurs de l'image & Logo
MAIN_BLUE = "#001b3a"  # Bleu nuit de l'image
GOLD = "#e1ad01"       # Jaune/Or du bouton "Discover"

st.markdown(f"""
    <style>
    /* Image de fond style Adventure */
    .stApp {{
        background: linear-gradient(rgba(0, 27, 58, 0.8), rgba(0, 27, 58, 0.8)), 
                    url("https://images.unsplash.com");
        background-size: cover;
        background-attachment: fixed;
    }}
    
    /* Barre de navigation haute */
    header[data-testid="stHeader"] {{
        background-color: {MAIN_BLUE} !important;
        border-bottom: 2px solid {GOLD};
    }}
    
    /* Menu Latéral */
    [data-testid="stSidebar"] {{
        background-color: {MAIN_BLUE} !important;
        border-right: 1px solid {GOLD};
    }}

    /* Boutons de navigation */
    .stButton>button {{
        background-color: transparent;
        color: white;
        border: 1px solid {GOLD};
        width: 100%;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        background-color: {GOLD};
        color: {MAIN_BLUE};
    }}

    /* Champs de saisie */
    input, select, textarea {{
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid {GOLD} !important;
    }}
    </style>
""", unsafe_allow_html=True)

# ================= SUPABASE =================
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("🚨 Configuration Supabase manquante !")
    st.stop()

# ================= FONCTIONS (GARDÉES TEL QUEL) =================
logo_path = "logo.png"
def afficher_logo(w=200):
    if os.path.exists(logo_path): st.image(logo_path, width=w)
    else: st.info("🏋️ 365 GYM & FITNESS")

def charger_depuis_supabase():
    try:
        r = supabase.table("abonnes").select("*").execute()
        return pd.DataFrame(r.data) if r.data else pd.DataFrame(columns=["nom","date_debut","duree_mois","date_fin","WhatsApp","statut"])
    except: return pd.DataFrame(columns=["nom","date_debut","duree_mois","date_fin","WhatsApp","statut"])

def charger_publicites():
    try:
        r = supabase.table("publicite").select("*").order("id", desc=True).execute()
        return r.data if r.data else []
    except: return []

# ================= SESSION & NAV =================
if 'page' not in st.session_state: st.session_state['page'] = "📢 Page Publicité"
if 'logged' not in st.session_state: st.session_state['logged'] = False
if 'edit_data' not in st.session_state: st.session_state['edit_data'] = None

# Navigation style "Adventure" (Onglets en haut simulés)
col_l, col_m1, col_m2 = st.columns([1, 2, 2])
with col_l: afficher_logo(120)
with col_m1: 
    if st.button("📢 ACCUEIL / PUB"): st.session_state['page'] = "📢 Page Publicité"; st.rerun()
with col_m2: 
    if st.button("🔐 ESPACE ADMIN"): st.session_state['page'] = "🔐 Gestion Admin"; st.rerun()

st.divider()

page = st.session_state['page']

# ================= PAGE PUBLICITÉ =================
if page=="📢 Page Publicité":
    st.markdown(f"<h1 style='text-align:center; color:{GOLD};'>NEW ADVENTURE AT 365 GYM</h1>", unsafe_allow_html=True)
    posts = charger_publicites()
    if posts:
        for post in posts:
            with st.container():
                if post.get('type')=="Photo": st.image(post['url_media'], caption=post.get('legende'))
                elif post.get('type')=="Vidéo": st.video(post['url_media'])
                else: st.subheader(post.get('legende'))
    else:
        st.info("### 🔥 Nos Offres\n- **1 Mois** : 300 DH\n- **12 Mois** : 2500 DH")

# ================= PAGE ADMIN =================
elif page=="🔐 Gestion Admin":
    if not st.session_state.logged:
        pwd = st.text_input("🔑 Code d'accès", type="password")
        if st.button("Se connecter"):
            if pwd=="1980": st.session_state.logged = True; st.rerun()
            else: st.error("❌ Code incorrect")
    else:
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Inscriptions","📊 Liste","📣 Publier","⏳ J-3","❌ EXPIRÉS"])

        # -------- INSCRIPTIONS (MODIFIER AUTOMATIQUE) --------
        with tab1:
            st.subheader("📝 Gérer les Membres")
            df = charger_depuis_supabase()
            
            # Si on a cliqué sur modifier dans la liste
            edit = st.session_state.edit_data
            v_nom = edit['nom'] if edit else ""
            v_wa = edit['WhatsApp'] if edit else ""
            v_stt = edit['statut'] if edit else "Actif"
            v_duree = int(edit['duree_mois']) if edit else 1

            with st.form("form_gestion", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    nom = st.text_input("Nom", value=v_nom)
                    wa = st.text_input("WhatsApp", value=v_wa)
                    stt = st.selectbox("Statut", ["Actif","Inactif"], index=0 if v_stt=="Actif" else 1)
                with col2:
                    debut = st.date_input("Début", datetime.now())
                    mois = st.number_input("Mois", min_value=1, value=v_duree)
                if st.form_submit_button("💾 ENREGISTRER"):
                    fin = debut + pd.DateOffset(months=mois)
                    data = {"nom":nom,"date_debut":debut.strftime("%Y-%m-%d"),"duree_mois":int(mois),"date_fin":fin.strftime("%Y-%m-%d"),"WhatsApp":wa,"statut":stt}
                    supabase.table("abonnes").upsert(data, on_conflict="WhatsApp").execute()
                    st.session_state.edit_data = None
                    st.success("✅ Enregistré !")
                    st.rerun()

        # -------- LISTE AVEC MODIFIER / SUPPRIMER --------
        with tab2:
            data_m = charger_depuis_supabase()
            for i, r in data_m.iterrows():
                c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
                c1.write(r['nom'])
                c2.write(f"Fin: {r['date_fin']}")
                if c3.button("✏️", key=f"ed_{i}"):
                    st.session_state.edit_data = r
                    st.rerun()
                if c4.button("🗑️", key=f"del_{i}"):
                    supabase.table("abonnes").delete().eq("WhatsApp", r['WhatsApp']).execute()
                    st.rerun()

        # -------- PUBLIER (TEL QUEL) --------
        with tab3:
            t_pub = st.selectbox("Type", ["Photo","Vidéo","Message"])
            fichier = st.file_uploader("Choisir un média", type=["png","jpg","jpeg","mp4"])
            with st.form("form_pub_final", clear_on_submit=True):
                legende_txt = st.text_area("Légende")
                if st.form_submit_button("📢 PUBLIER"):
                    if fichier:
                        nom_f = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{fichier.name}"
                        supabase.storage.from_("medias").upload(nom_f,fichier.getvalue())
                        url_final = supabase.storage.from_("medias").get_public_url(nom_f).public_url
                        supabase.table("publicite").insert({"type":t_pub,"url_media":url_final,"legende":legende_txt}).execute()
                    else:
                        supabase.table("publicite").insert({"type":"Message","url_media":"","legende":legende_txt}).execute()
                    st.rerun()

        # -------- EXPIRATIONS J-3 --------
        with tab4:
            df_s = charger_depuis_supabase()
            if not df_s.empty:
                df_s['date_fin_dt'] = pd.to_datetime(df_s['date_fin'])
                df_s['restant'] = (df_s['date_fin_dt'] - pd.Timestamp(datetime.now().date())).dt.days
                alerte = df_s[(df_s['restant']<=3) & (df_s['restant']>=0) & (df_s['statut'].str.lower()=="actif")]
                for _,r in alerte.iterrows():
                    num_raw = "".join(filter(str.isdigit,str(r["WhatsApp"])))
                    num_final = "243"+(num_raw[1:] if num_raw.startswith("0") else num_raw)
                    msg = f"Bonjour {r['nom']} ! 👋 Votre abonnement se termine le {r['date_fin']}."
                    st.markdown(f"🔔 **{r['nom']}** | [WhatsApp](https://wa.me{num_final}?text={urllib.parse.quote(msg)})")

        # -------- NOUVEAU : LISTE DES EXPIRÉS --------
        with tab5:
            st.subheader("❌ Membres ayant dépassé la date")
            df_e = charger_depuis_supabase()
            if not df_e.empty:
                df_e['date_fin_dt'] = pd.to_datetime(df_e['date_fin'])
                exp = df_e[df_e['date_fin_dt'] < pd.Timestamp(datetime.now().date())]
                if not exp.empty:
                    for _, r in exp.iterrows():
                        st.markdown(f"<div style='color:red; font-weight:bold;'>❌ {r['nom']} - Expiré le {r['date_fin']}</div>", unsafe_allow_html=True)
                else:
                    st.success("Personne n'est expiré.")
