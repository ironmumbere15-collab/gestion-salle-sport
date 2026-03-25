import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ===== CONFIGURATION =====
st.set_page_config(page_title="365 GYM & FITNESS", layout="wide", page_icon="💪")

ADMIN_PASSWORD = "1980"

# ===== SESSION STATE =====
if 'admin' not in st.session_state:
    st.session_state['admin'] = False

if 'abonnés' not in st.session_state:
    # Exemple de base initiale
    st.session_state['abonnés'] = pd.DataFrame(columns=[
        "Nom", "Date début", "Durée (mois)", "Date fin", "WhatsApp", "Statut"
    ])

# ===== FONCTIONS =====
def calculer_date_fin(date_debut, duree):
    return date_debut + pd.DateOffset(months=duree)

def notifier_whatsapp(nom):
    st.info(f"Message WhatsApp envoyé à {nom} (simulé)")

def afficher_abonnés(df):
    st.dataframe(df)

# ===== LOGIN ADMIN =====
st.sidebar.image("logo.png", width=100)
st.sidebar.markdown("<h3 style='text-align:center;'>365 GYM & FITNESS</h3>", unsafe_allow_html=True)

if not st.session_state['admin']:
    st.sidebar.subheader("Connexion Admin")
    password_input = st.sidebar.text_input("Mot de passe", type="password")
    if st.sidebar.button("Se connecter"):
        if password_input == ADMIN_PASSWORD:
            st.session_state['admin'] = True
            st.experimental_rerun()
        else:
            st.sidebar.error("Mot de passe incorrect")
    st.stop()

# ===== BARRE DE NAVIGATION =====
menu = ["Tableau de bord", "Ajouter Abonné", "Abonnés expirant", "Abonnés expirés", "Forum", "Galerie", "Contact"]
choix = st.sidebar.radio("Menu", menu)

# ===== TABLEAU DE BORD =====
if choix == "Tableau de bord":
    st.title("Tableau de bord - 365 GYM & FITNESS")
    df = st.session_state['abonnés']
    st.subheader("Liste des abonnés")
    search = st.text_input("Rechercher par nom")
    if search:
        df = df[df["Nom"].str.contains(search, case=False)]
    st.dataframe(df)

    # Expirations dans 3 jours
    exp_3_jours = df[df["Date fin"] <= (pd.Timestamp(datetime.now()) + timedelta(days=3))]
    st.subheader("Abonnements expirant dans 3 jours")
    for _, row in exp_3_jours.iterrows():
        col1, col2 = st.columns([3,1])
        with col1:
            st.write(f"{row['Nom']} - Expire le {row['Date fin'].strftime('%d/%m/%Y')}")
        with col2:
            if st.button(f"Notifier {row['Nom']}", key=f"notif_{row['Nom']}"):
                notifier_whatsapp(row['Nom'])

    st.subheader("Statistiques")
    st.write(f"Total abonnés : {len(df)}")
    st.write(f"Abonnements expirés : {len(df[df['Statut']=='Expiré'])}")

# ===== AJOUT ABONNÉ =====
elif choix == "Ajouter Abonné":
    st.title("Ajouter un nouvel abonné")
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
        st.success(f"Abonné {nom} ajouté !")

# ===== ABONNÉS EXPIRANT =====
elif choix == "Abonnés expirant":
    st.title("Abonnements proches de l'expiration")
    df = st.session_state['abonnés']
    exp_3_jours = df[df["Date fin"] <= (pd.Timestamp(datetime.now()) + timedelta(days=3))]
    for _, row in exp_3_jours.iterrows():
        st.write(f"{row['Nom']} - Expire le {row['Date fin'].strftime('%d/%m/%Y')}")
        if st.button(f"Notifier {row['Nom']}", key=f"notif2_{row['Nom']}"):
            notifier_whatsapp(row['Nom'])

# ===== ABONNÉS EXPIRÉS =====
elif choix == "Abonnés expirés":
    st.title("Abonnements expirés")
    df = st.session_state['abonnés']
    expirés = df[df["Date fin"] < pd.Timestamp(datetime.now())]
    st.dataframe(expirés)

# ===== FORUM =====
elif choix == "Forum":
    st.title("Forum")
    st.text_area("Écrire un message")
    st.button("Publier")

# ===== GALERIE =====
elif choix == "Galerie":
    st.title("Galerie")
    st.file_uploader("Ajouter une photo ou vidéo", type=["png","jpg","mp4"])

# ===== CONTACT =====
elif choix == "Contact":
    st.title("Contact")
    st.write("Contacter via WhatsApp : +243XXXXXXXXX")
