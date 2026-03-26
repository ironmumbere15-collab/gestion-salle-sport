import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# ================= CONFIG & DESIGN =================
st.set_page_config(page_title="365 GYM & FITNESS", layout="wide", page_icon="💪")

# Couleurs inspirées de l'image (Bleu nuit & Or)
MAIN_COLOR = "#001F3F" # Bleu sombre
ACCENT_COLOR = "#FFD700" # Or / Jaune bouton

st.markdown(f"""
    <style>
    .stApp {{ background-color: #0e1117; }}
    [data-testid="stSidebar"] {{ background-color: {MAIN_COLOR}; border-right: 2px solid {ACCENT_COLOR}; }}
    .stButton>button {{ background-color: {ACCENT_COLOR}; color: {MAIN_COLOR}; font-weight: bold; border-radius: 5px; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
    .stTabs [data-baseweb="tab"] {{ background-color: #1a1a1a; color: white; border-radius: 5px 5px 0 0; padding: 10px; }}
    .stTabs [aria-selected="true"] {{ background-color: {ACCENT_COLOR} !important; color: {MAIN_COLOR} !important; }}
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
def charger_depuis_supabase():
    try:
        r = supabase.table("abonnes").select("*").execute()
        return pd.DataFrame(r.data) if r.data else pd.DataFrame(columns=["nom","date_debut","duree_mois","date_fin","WhatsApp","statut"])
    except:
        return pd.DataFrame(columns=["nom","date_debut","duree_mois","date_fin","WhatsApp","statut"])

def supprimer_membre(whatsapp):
    supabase.table("abonnes").delete().eq("WhatsApp", whatsapp).execute()
    st.success(f"🗑️ Membre supprimé !")
    st.rerun()

# ================= SESSION STATE =================
if 'edit_member' not in st.session_state: st.session_state.edit_member = None
if 'page' not in st.session_state: st.session_state['page'] = "📢 Page Publicité"
if 'logged' not in st.session_state: st.session_state['logged'] = False

# ================= SIDEBAR (Design Adventure) =================
with st.sidebar:
    st.markdown(f"<h1 style='color:{ACCENT_COLOR}; text-align:center;'>365 GYM</h1>", unsafe_allow_html=True)
    if st.button("📢 PAGE PUBLICITÉ", use_container_width=True):
        st.session_state['page'] = "📢 Page Publicité"
        st.rerun()
    if st.button("🔐 GESTION ADMIN", use_container_width=True):
        st.session_state['page'] = "🔐 Gestion Admin"
        st.rerun()

page = st.session_state['page']

# ================= PAGE PUBLICITÉ =================
if page=="📢 Page Publicité":
    st.title("🔥 Dernières News")
    # ... (Gardez votre code de chargement publicitaire ici)

# ================= PAGE ADMIN =================
elif page=="🔐 Gestion Admin":
    if not st.session_state.logged:
        pwd = st.text_input("🔑 Code d'accès", type="password")
        if st.button("Se connecter"):
            if pwd=="1980": st.session_state.logged = True; st.rerun()
            else: st.error("❌ Code incorrect")
    else:
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Inscriptions","📊 Liste","📣 Publier","⏳ J-3","❌ EXPIRÉS"])

        # -------- FORMULAIRE (Modifié pour permettre l'édition) --------
        with tab1:
            st.subheader("📝 Inscription / Modification")
            df = charger_depuis_supabase()
            
            # Pré-remplissage si clic sur "Modifier"
            edit = st.session_state.edit_member
            v_nom = edit['nom'] if edit else ""
            v_wa = edit['WhatsApp'] if edit else ""
            v_stt = edit['statut'] if edit else "Actif"
            v_duree = int(edit['duree_mois']) if edit else 1

            with st.form("form_gestion", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    nom = st.text_input("Nom Complet", value=v_nom)
                    wa = st.text_input("WhatsApp (ex: 243...)", value=v_wa)
                    stt = st.selectbox("Statut", ["Actif","Inactif"], index=0 if v_stt=="Actif" else 1)
                with col2:
                    debut = st.date_input("Date de début", datetime.now())
                    mois = st.number_input("Nombre de mois", min_value=1, value=v_duree)
                
                fin = debut + pd.DateOffset(months=mois)
                if st.form_submit_button("💾 ENREGISTRER DANS LA BASE"):
                    data = {"nom":nom, "date_debut":debut.strftime("%Y-%m-%d"), 
                            "duree_mois":int(mois), "date_fin":fin.strftime("%Y-%m-%d"),
                            "WhatsApp":wa, "statut":stt}
                    supabase.table("abonnes").upsert(data, on_conflict="WhatsApp").execute()
                    st.session_state.edit_member = None # Reset après save
                    st.success("✅ Données synchronisées !")
                    st.rerun()

        # -------- LISTE AVEC BOUTONS MODIFIER/SUPPRIMER --------
        with tab2:
            df_list = charger_depuis_supabase()
            if not df_list.empty:
                for i, row in df_list.iterrows():
                    col_n, col_d, col_btn1, col_btn2 = st.columns([3, 2, 1, 1])
                    col_n.write(f"**{row['nom']}** ({row['WhatsApp']})")
                    col_d.write(f"Fin: {row['date_fin']}")
                    if col_btn1.button("✏️", key=f"edit_{i}"):
                        st.session_state.edit_member = row
                        st.rerun()
                    if col_btn2.button("🗑️", key=f"del_{i}"):
                        supprimer_membre(row['WhatsApp'])
            else:
                st.info("Aucun membre enregistré.")

        # -------- EXPIRÉS (Version améliorée) --------
        with tab5:
            st.subheader("❌ Abonnements Terminés")
            df_s = charger_depuis_supabase()
            if not df_s.empty:
                df_s['date_fin_dt'] = pd.to_datetime(df_s['date_fin'])
                df_s['restant'] = (df_s['date_fin_dt'] - pd.Timestamp(datetime.now().date())).dt.days
                exp = df_s[df_s['restant'] < 0].sort_values(by="restant")
                
                if not exp.empty:
                    for _, r in exp.iterrows():
                        st.error(f"**{r['nom']}** - Expiré depuis **{abs(r['restant'])} jours** (le {r['date_fin']})")
                else:
                    st.success("Aucun abonnement expiré ! 🎉")

        # (Gardez tab3 et tab4 tels quels, ils sont déjà fonctionnels)
