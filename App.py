import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from PIL import Image

# ===== CONFIGURATION =====
st.set_page_config(page_title="365 GYM & FITNESS", layout="wide", page_icon="💪")

ADMIN_PASSWORD = "1980"

# ===== SESSION STATE =====
if 'admin' not in st.session_state:
    st.session_state['admin'] = False

if 'abonnés' not in st.session_state:
    st.session_state['abonnés'] = pd.DataFrame(columns=[
        "Nom", "Date début", "Durée (mois)", "Date fin", "WhatsApp", "Statut"
    ])

# ===== FONCTIONS =====
def calculer_date_fin(date_debut, duree):
    return date_debut + pd.DateOffset(months=duree)

def notifier_whatsapp(nom):
    st.success(f"Message WhatsApp envoyé à {nom} (simulé)")

def embellir_formulaire():
    st.markdown("""
    <style>
    .stTextInput>div>div>input {border-radius: 10px; border:2px solid #ff4b4b; padding:8px;}
    .stNumberInput>div>div>input {border-radius: 10px; border:2px solid #ff4b4b; padding:8px;}
    .stButton>button {background-color:#ff4b4b; color:white; border-radius:10px; padding:10px 20px; font-weight:bold;}
    .stDataFrame table {border-radius:10px; overflow:hidden;}
    </style>
    """, unsafe_allow_html=True)

# ===== LOGIN ADMIN =====
st.sidebar.image("logo.png", width=120)
st.sidebar.markdown("<h4 style='text-align:center;color:#ff4b4b;'>365 GYM & FITNESS</h4>", unsafe_allow_html=True)

if not st.session_state['admin']:
    st.sidebar.subheader("Connexion Admin")
    password_input = st.sidebar.text_input("Mot de passe", type="password")
    if st.sidebar.button("Se connecter"):
        if password_input == ADMIN_PASSWORD:
            st.session_state['admin'] = True
            st.experimental_rerun()
        else:
            st.sidebar.error("Mot de passe incorrect")

# ===== BARRE DE NAVIGATION =====
menu_public = ["Forum", "Galerie", "Contact", "Publicité / Site web"]
menu_admin = ["Tableau de bord", "Ajouter Abonné", "Abonnés expirant", "Abonnés expirés"]

menu = menu_admin + menu_public if st.session_state.get('admin', False) else menu_public
choix = st.sidebar.radio("Menu", menu)

# ===== EMBELLISSEMENT =====
embellir_formulaire()

# ===== FORMULAIRES ADMIN =====
if st.session_state.get('admin', False):
    if choix == "Tableau de bord":
        st.title("Tableau de bord - 365 GYM & FITNESS")
        df = st.session_state['abonnés']
        st.subheader("Liste des abonnés")
        search = st.text_input("🔍 Rechercher par nom")
        if search:
            df = df[df["Nom"].str.contains(search, case=False)]
        st.dataframe(df.style.set_properties(**{'border-radius': '10px'}))

        # Expirations dans 3 jours
        exp_3_jours = df[df["Date fin"] <= (pd.Timestamp(datetime.now()) + timedelta(days=3))]
        st.subheader("Abonnements expirant dans 3 jours")
        for _, row in exp_3_jours.iterrows():
            col1, col2 = st.columns([3,1])
            with col1:
                st.markdown(f"💡 **{row['Nom']}** - Expire le {row['Date fin'].strftime('%d/%m/%Y')}")
            with col2:
                if st.button("📩 Notifier", key=f"notif_{row['Nom']}"):
                    notifier_whatsapp(row['Nom'])

        st.subheader("Statistiques")
        st.markdown(f"🏋️ Total abonnés : **{len(df)}**")
        st.markdown(f"⏳ Abonnements expirés : **{len(df[df['Statut']=='Expiré'])}**")

    elif choix == "Ajouter Abonné":
        st.title("➕ Ajouter un nouvel abonné")
        nom = st.text_input("Nom")
        date_debut = st.date_input("Date de début")
        duree = st.number_input("Durée (mois)", min_value=1, max_value=24, value=1)
        whatsapp = st.text_input("WhatsApp")
        if st.button("Ajouter"):
            date_fin = calculer_date_fin(pd.Timestamp(date_debut), duree)
            st.session_state['abonnés'] = pd.concat([st.session_state['abonnés'], pd.DataFrame([{
                "Nom": nom,
                "Date début": date_debut,
                "Durée (mois)": duree,
                "Date fin": date_fin,
                "WhatsApp": whatsapp,
                "Statut": "Actif"
            }])], ignore_index=True)
            st.success(f"✅ Abonné {nom} ajouté !")

    elif choix == "Abonnés expirant":
        st.title("⏳ Abonnements proches de l'expiration")
        df = st.session_state['abonnés']
        exp_3_jours = df[df["Date fin"] <= (pd.Timestamp(datetime.now()) + timedelta(days=3))]
        for _, row in exp_3_jours.iterrows():
            st.markdown(f"💡 **{row['Nom']}** - Expire le {row['Date fin'].strftime('%d/%m/%Y')}")
            if st.button("📩 Notifier", key=f"notif2_{row['Nom']}"):
                notifier_whatsapp(row['Nom'])

    elif choix == "Abonnés expirés":
        st.title("❌ Abonnements expirés")
        df = st.session_state['abonnés']
        expirés = df[df["Date fin"] < pd.Timestamp(datetime.now())]
        st.dataframe(expirés)

# ===== FORMULAIRES PUBLICS =====
if choix == "Forum":
    st.title("💬 Forum")
    message = st.text_area("Écrire un message")
    if st.button("Publier"):
        st.success("Message publié ! (simulation)")

elif choix == "Galerie":
    st.title("📸 Galerie")
    st.file_uploader("Ajouter une photo ou vidéo", type=["png","jpg","mp4"])

elif choix == "Contact":
    st.title("📞 Contact")
    st.write("Contacter via WhatsApp : +243XXXXXXXXX")

elif choix == "Publicité / Site web":
    st.title("365 GYM & FITNESS")
    st.write("Poster vos exploits, photos ou liens vers le site web")
    st.text_input("Titre / Sujet")
    st.text_area("Description / Détails")
    st.file_uploader("Ajouter image ou vidéo", type=["png","jpg","mp4"])
    st.text_input("Lien du site web")
    if st.button("Publier"):
        st.success("✅ Publication ajoutée ! (simulation)")
