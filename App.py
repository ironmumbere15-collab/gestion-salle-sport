import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# ================= CONFIG & DESIGN (NOIR & OR) =================
st.set_page_config(page_title="365 GYM & FITNESS", layout="wide", page_icon="💪")

LOGO_BLACK = "#000000" 
LOGO_GOLD = "#e1ad01"  
TEXT_WHITE = "#FFFFFF"

st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)), 
                    url("https://images.unsplash.com");
        background-size: cover;
        background-attachment: fixed;
    }}
    header[data-testid="stHeader"] {{ background-color: {LOGO_BLACK} !important; border-bottom: 2px solid {LOGO_GOLD}; }}
    [data-testid="stSidebar"] {{ background-color: {LOGO_BLACK} !important; border-right: 1px solid {LOGO_GOLD}; }}
    .stButton>button {{
        background-color: rgba(225, 173, 1, 0.1); color: {TEXT_WHITE};
        border: 1px solid {LOGO_GOLD}; width: 100%; font-weight: bold; transition: 0.3s;
    }}
    .stButton>button:hover {{ background-color: {LOGO_GOLD}; color: {LOGO_BLACK}; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: #111; color: white; border: 1px solid #333; padding: 10px 20px; border-radius: 4px;
    }}
    .stTabs [aria-selected="true"] {{ background-color: {LOGO_GOLD} !important; color: {LOGO_BLACK} !important; }}
    input, select, textarea {{ background-color: rgba(255, 255, 255, 0.05) !important; color: white !important; border: 1px solid {LOGO_GOLD} !important; }}
    </style>
""", unsafe_allow_html=True)

# ================= SUPABASE =================
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception:
    st.error("🚨 Configuration Supabase manquante !")
    st.stop()

# ================= FONCTIONS DATA =================
logo_path = "logo.png"
def afficher_logo(w=200):
    if os.path.exists(logo_path): st.image(logo_path, width=w)
    else: st.markdown(f"<h2 style='color:{LOGO_GOLD}'>🏋️ 365 GYM</h2>", unsafe_allow_html=True)

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
if 'edit_item' not in st.session_state: st.session_state['edit_item'] = None

# Navigation haute
col_logo, col_nav1, col_nav2 = st.columns()
with col_logo: afficher_logo(120)
with col_nav1: 
    if st.button("📢 ACCUEIL / PUBLICITÉ"): st.session_state['page'] = "📢 Page Publicité"; st.rerun()
with col_nav2: 
    if st.button("🔐 GESTION ADMIN"): st.session_state['page'] = "🔐 Gestion Admin"; st.rerun()

st.divider()
page = st.session_state['page']

# ================= PAGE PUBLICITÉ (ACCUEIL) =================
if page == "📢 Page Publicité":
    st.markdown(f"""
        <div style="text-align: center; padding: 40px 10px; background: rgba(0,0,0,0.5); border-radius: 15px; border: 1px solid {LOGO_GOLD};">
            <h1 style='color:{LOGO_GOLD}; font-size: 45px; margin-bottom: 0;'>365 GYM & FITNESS</h1>
            <p style='color: white; font-size: 18px;'>Votre transformation commence ici, 365 jours par an.</p>
        </div>
    """, unsafe_allow_html=True)

    st.write("##")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div style='background:rgba(255,255,255,0.1); padding:20px; border-radius:10px; border-left:5px solid {LOGO_GOLD}; height:180px;'><h3 style='color:{LOGO_GOLD};'>⏰ HORAIRES</h3><p style='color:white;'><b>MATIN :</b> 06h00 — 09h00<br><b>SOIR :</b> 16h00 — 19h00</p><p style='color:gray; font-size:0.8em;'>Lundi au Samedi</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div style='background:rgba(255,255,255,0.1); padding:20px; border-radius:10px; border-left:5px solid {LOGO_GOLD}; height:180px;'><h3 style='color:{LOGO_GOLD};'>💪 SERVICES</h3><ul style='color:white;'><li>Musculation & Cardio</li><li>Coaching Perso</li><li>Suivi Diététique</li></ul></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div style='background:rgba(255,255,255,0.1); padding:20px; border-radius:10px; border-left:5px solid {LOGO_GOLD}; height:180px;'><h3 style='color:{LOGO_GOLD};'>📍 INFOS</h3><p style='color:white;'><b>Ambiance :</b> Motivation Maximale<br><b>Équipement :</b> Premium 2024</p></div>", unsafe_allow_html=True)

    st.write("##")
    st.markdown(f"<h2 style='text-align:center; color:{LOGO_GOLD};'>📢 NOS ACTUALITÉS</h2>", unsafe_allow_html=True)
    
    posts = charger_publicites()
    if posts:
        for post in posts:
            with st.container():
                st.markdown(f"<div style='background: rgba(0,0,0,0.6); padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #333;'>", unsafe_allow_html=True)
                if post.get('type')=="Photo" and post.get('url_media'): st.image(post['url_media'], use_container_width=True)
                elif post.get('type')=="Vidéo" and post.get('url_media'): st.video(post['url_media'])
                st.subheader(post.get('legende', ""))
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("### 🔥 Offre Spéciale : 1 Mois à 300 DH | 12 Mois à 2500 DH")

# ================= PAGE ADMIN =================
elif page == "🔐 Gestion Admin":
    if not st.session_state.logged:
        pwd = st.text_input("🔑 Code d'accès", type="password")
        if st.button("Se connecter"):
            if pwd=="1980": st.session_state.logged = True; st.rerun()
            else: st.error("❌ Code incorrect")
    else:
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Inscriptions","📊 Liste","📣 Publier","⏳ J-3","❌ EXPIRÉS"])

        with tab1:
            st.subheader("📝 Gérer les Membres")
            edit = st.session_state.edit_item
            with st.form("form_gestion", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    nom = st.text_input("Nom", value=edit['nom'] if edit else "")
                    wa = st.text_input("WhatsApp", value=edit['WhatsApp'] if edit else "")
                    stt = st.selectbox("Statut", ["Actif","Inactif"], index=0 if not edit or edit['statut']=="Actif" else 1)
                with col2:
                    debut = st.date_input("Début", datetime.now())
                    mois = st.number_input("Mois", min_value=1, value=int(edit['duree_mois']) if edit else 1)
                if st.form_submit_button("💾 ENREGISTRER"):
                    fin = debut + pd.DateOffset(months=mois)
                    data = {"nom":nom,"date_debut":debut.strftime("%Y-%m-%d"),"duree_mois":int(mois),"date_fin":fin.strftime("%Y-%m-%d"),"WhatsApp":wa,"statut":stt}
                    supabase.table("abonnes").upsert(data, on_conflict="WhatsApp").execute()
                    st.session_state.edit_item = None
                    st.success("✅ Enregistré !")
                    st.rerun()

        with tab2:
            df = charger_depuis_supabase()
            if not df.empty:
                for i, r in df.iterrows():
                    c1, c2, c3, c4 = st.columns()
                    c1.write(f"👤 {r['nom']}")
                    c2.write(f"📅 Fin: {r['date_fin']}")
                    if c3.button("✏️", key=f"e{i}"):
                        st.session_state.edit_item = r
                        st.rerun()
                    if c4.button("🗑️", key=f"d{i}"):
                        supabase.table("abonnes").delete().eq("WhatsApp", r['WhatsApp']).execute()
                        st.rerun()

        with tab3:
            t_pub = st.selectbox("Type", ["Photo","Vidéo","Message"])
            fichier = st.file_uploader("Choisir un média", type=["png","jpg","jpeg","mp4"])
            if fichier:
                if t_pub=="Photo": st.image(fichier, width=300)
                if t_pub=="Vidéo": st.video(fichier)
            with st.form("form_pub_final", clear_on_submit=True):
                legende_txt = st.text_area("Légende")
                if st.form_submit_button("📢 PUBLIER"):
                    if fichier:
                        nom_f = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{fichier.name}"
                        supabase.storage.from_("medias").upload(nom_f,fichier.getvalue())
                        res_url = supabase.storage.from_("medias").get_public_url(nom_f)
                        url_final = res_url if isinstance(res_url,str) else res_url.public_url
                        supabase.table("publicite").insert({"type":t_pub,"url_media":url_final,"legende":legende_txt}).execute()
                    else:
                        supabase.table("publicite").insert({"type":"Message","url_media":"","legende":legende_txt}).execute()
                    st.success("✅ Publication réussie !")
                    st.rerun()

        with tab4:
            df_s = charger_depuis_supabase()
            if not df_s.empty:
                df_s['date_fin_dt'] = pd.to_datetime(df_s['date_fin'])
                df_s['restant'] = (df_s['date_fin_dt'] - pd.Timestamp(datetime.now().date())).dt.days
                alerte = df_s[(df_s['restant']<=3) & (df_s['restant']>=0) & (df_s['statut']=="Actif")]
                for _,r in alerte.iterrows():
                    num_raw = "".join(filter(str.isdigit,str(r["WhatsApp"])))
                    num_final = "243"+(num_raw[1:] if num_raw.startswith("0") else num_raw)
                    msg = f"Bonjour {r['nom']} ! 👋 Votre abonnement 365 GYM se termine le {r['date_fin']}."
                    st.markdown(f"🔔 **{r['nom']}** | [Envoyer WhatsApp](https://wa.me{num_final}?text={urllib.parse.quote(msg)})")

        with tab5:
            st.subheader("❌ Abonnements Expirés")
            df_e = charger_depuis_supabase()
            if not df_e.empty:
                df_e['date_fin_dt'] = pd.to_datetime(df_e['date_fin'])
                exp = df_e[df_e['date_fin_dt'] < pd.Timestamp(datetime.now().date())]
                for _, r in exp.iterrows():
                    st.markdown(f"<div style='color:red; font-weight:bold; border:1px solid red; padding:10px; margin-bottom:5px; background:rgba(255,0,0,0.1);'>❌ {r['nom']} - Expiré le {r['date_fin']}</div>", unsafe_allow_html=True)
