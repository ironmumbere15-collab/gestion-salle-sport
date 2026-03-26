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
except Exception as e:
    st.error("🚨 Configuration Supabase manquante dans les Secrets !")
    st.stop()

# ================= CONFIG (COULEURS LOGO) =================
st.set_page_config(page_title="365 GYM & FITNESS", layout="wide", page_icon="💪")
logo_path = "logo.png"

# Style pour correspondre au noir et or de ton logo
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: white; }
    [data-testid="stSidebar"] { background-color: #000000; border-right: 1px solid #e1ad01; }
    .stButton>button { background-color: #e1ad01; color: black; font-weight: bold; }
    .stTabs [aria-selected="true"] { background-color: #e1ad01 !important; color: black !important; }
    </style>
""", unsafe_allow_html=True)

def afficher_logo(w=200):
    if os.path.exists(logo_path):
        st.image(logo_path, width=w)
    else:
        st.info("🏋️ 365 GYM & FITNESS")

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
if 'page' not in st.session_state:
    st.session_state['page'] = "📢 Page Publicité"
if 'logged' not in st.session_state:
    st.session_state['logged'] = False
if 'edit_item' not in st.session_state:
    st.session_state['edit_item'] = None

# ================= NAVIGATION =================
st.sidebar.title("💎 365 GYM MENU")
if st.sidebar.button("📢 PAGE PUBLICITÉ", type="primary" if st.session_state['page']=="📢 Page Publicité" else "secondary"):
    st.session_state['page'] = "📢 Page Publicité"
    st.rerun()
if st.sidebar.button("🔐 GESTION ADMIN", type="primary" if st.session_state['page']=="🔐 Gestion Admin" else "secondary"):
    st.session_state['page'] = "🔐 Gestion Admin"
    st.rerun()

page = st.session_state['page']

# ================= PAGE PUBLICITÉ =================
if page=="📢 Page Publicité":
    afficher_logo(300)
    st.title("Bienvenue chez 365 GYM & FITNESS")
    
    # Infos Horaires demandées
    st.markdown("### ⏰ Nos Horaires d'Ouverture")
    st.info("**Matin :** 06h00 — 09h00 | **Soir :** 16h00 — 19h00")
    
    posts = charger_publicites()
    if posts:
        for post in posts:
            with st.container():
                st.divider()
                if post.get('type')=="Photo" and post.get('url_media'):
                    st.image(post['url_media'], caption=post.get('legende'), use_container_width=True)
                elif post.get('type')=="Vidéo" and post.get('url_media'):
                    st.video(post['url_media'])
                    st.caption(post.get('legende'))
                else:
                    st.subheader(post.get('legende',"Annonce"))
    else:
        st.info("### 🔥 Nos Offres\n- **1 Mois** : 300 DH\n- **12 Mois** : 2500 DH")

# ================= PAGE ADMIN =================
elif page=="🔐 Gestion Admin":
    if not st.session_state.logged:
        pwd = st.text_input("🔑 Code d'accès", type="password")
        if st.button("Se connecter"):
            if pwd=="1980":
                st.session_state.logged = True
                st.rerun()
            else:
                st.error("❌ Code incorrect")
    else:
        afficher_logo(100)
        st.header("⚙️ Panneau de Contrôle Admin")

        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Inscriptions","📊 Liste Membres","📣 Publier News","⏳ Expirations J-3","❌ EXPIRÉS"])

        # -------- INSCRIPTIONS (AVEC FONCTION MODIFIER) --------
        with tab1:
            st.subheader("📝 Gérer les Membres")
            edit = st.session_state.edit_item
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
                fin = debut + pd.DateOffset(months=mois)
                if st.form_submit_button("💾 ENREGISTRER"):
                    data = {"nom":nom,"date_debut":debut.strftime("%Y-%m-%d"),
                            "duree_mois":int(mois),"date_fin":fin.strftime("%Y-%m-%d"),
                            "WhatsApp":wa,"statut":stt}
                    supabase.table("abonnes").upsert(data, on_conflict="WhatsApp").execute()
                    st.session_state.edit_item = None
                    st.success("✅ Enregistré !")
                    st.rerun()

        # -------- LISTE MEMBRES (AVEC BOUTONS) --------
        with tab2:
            df_list = charger_depuis_supabase()
            if not df_list.empty:
                for i, row in df_list.iterrows():
                    c1, c2, c3, c4 = st.columns([3,2,1,1])
                    c1.write(f"**{row['nom']}**")
                    c2.write(f"Fin: {row['date_fin']}")
                    if c3.button("✏️", key=f"edit_{i}"):
                        st.session_state.edit_item = row
                        st.rerun()
                    if c4.button("🗑️", key=f"del_{i}"):
                        supabase.table("abonnes").delete().eq("WhatsApp", row['WhatsApp']).execute()
                        st.rerun()

        # -------- PUBLIER (TON CODE ORIGINAL) --------
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
                    wa_url = f"https://wa.me{num_final}?text={urllib.parse.quote(msg)}"
                    st.markdown(f"🔔 **{r['nom']}** | Fin : {r['date_fin']} 👉 [Notifier WhatsApp]({wa_url})")

        # -------- EXPIRÉS (NOUVEL ONGLET) --------
        with tab5:
            st.subheader("❌ Abonnements Terminés")
            df_ex = charger_depuis_supabase()
            if not df_ex.empty:
                df_ex['date_fin_dt'] = pd.to_datetime(df_ex['date_fin'])
                exp = df_ex[df_ex['date_fin_dt'] < pd.Timestamp(datetime.now().date())]
                for _, r in exp.iterrows():
                    st.error(f"❌ {r['nom']} - Expiré depuis le {r['date_fin']}")
