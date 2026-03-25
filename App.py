import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --------------------------- MOT DE PASSE ADMIN ---------------------------
PASSWORD = "1980"

# --------------------------- COULEURS ---------------------------
PRIMARY_COLOR = "#FF5733"  # adapte aux couleurs du logo
SECONDARY_COLOR = "#FFFFFF"

# --------------------------- TITRE ET LOGO ---------------------------
st.sidebar.image("logo.png", width=150)
st.sidebar.markdown("<h2 style='color:white; font-weight:bold;'>365 GYM & FITNESS</h2>", unsafe_allow_html=True)

# --------------------------- LOGIN ---------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    password_input = st.text_input("Mot de passe Admin", type="password")
    if st.button("Se connecter"):
        if password_input == PASSWORD:
            st.session_state.logged_in = True
            st.success("Connecté en tant qu'Admin")
        else:
            st.error("Mot de passe incorrect")

# --------------------------- MENU ---------------------------
menu = ["Forum", "Galerie", "Contact"]
if st.session_state.logged_in:
    menu += ["Abonnés", "Nouveaux abonnements", "Expirants", "Publicité"]

choice = st.sidebar.radio("Menu", menu)

# --------------------------- DATA SIMULÉE ---------------------------
data = {
    "Nom": ["Alice", "Bob", "Charlie", "David"],
    "Date début": [datetime(2026,3,1), datetime(2026,2,25), datetime(2026,3,10), datetime(2026,3,5)],
    "Date fin": [datetime(2026,4,1), datetime(2026,3,27), datetime(2026,4,10), datetime(2026,3,8)]
}
df = pd.DataFrame(data)

# --------------------------- FONCTIONS ---------------------------
def afficher_formulaire_abonnes():
    st.subheader("Liste des abonnés")
    st.dataframe(df)

def afficher_nouveaux_abonnements():
    st.subheader("Nouveaux abonnements")
    for idx, row in df.iterrows():
        st.markdown(f"👤 **{row['Nom']}** - Début: {row['Date début'].strftime('%d/%m/%Y')} Fin: {row['Date fin'].strftime('%d/%m/%Y')}")
        st.button("Modifier", key=f"mod_{idx}")
        st.button("Supprimer", key=f"sup_{idx}")

def afficher_expirants():
    st.subheader("Abonnements expirant dans 3 jours")
    exp_3_jours = df[df["Date fin"] <= (datetime.now() + timedelta(days=3))]
    for idx, row in exp_3_jours.iterrows():
        st.markdown(f"💡 **{row['Nom']}** - Expire le {row['Date fin'].strftime('%d/%m/%Y')}")
        st.button("Modifier", key=f"mod_exp_{idx}")
        st.button("Supprimer", key=f"sup_exp_{idx}")
        # BOUTON NOTIFIER
        if st.button(f"📩 Notifier {row['Nom']}", key=f"notif_{idx}"):
            message = f"Bonjour {row['Nom']}, votre abonnement à 365 GYM & FITNESS arrive bientôt à expiration. Renouvelez vite !"
            st.success(f"Message prêt à envoyer : {message}")

def afficher_publicite():
    st.subheader("Publicité")
    st.markdown("📢 Ici vous pouvez poster vos exploits, promotions ou annonces")
    # Exemple simple de formulaire pour poster
    titre = st.text_input("Titre de la publicité")
    contenu = st.text_area("Contenu")
    if st.button("Publier"):
        st.success(f"Publicité '{titre}' publiée !")

def afficher_forum():
    st.subheader("Forum")
    st.text_area("Poster un message")

def afficher_galerie():
    st.subheader("Galerie")
    st.file_uploader("Télécharger des photos ou vidéos", accept_multiple_files=True)

def afficher_contact():
    st.subheader("Contact")
    st.text_input("Envoyer un message via WhatsApp")

# --------------------------- AFFICHAGE SELON MENU ---------------------------
if choice == "Forum":
    afficher_forum()
elif choice == "Galerie":
    afficher_galerie()
elif choice == "Contact":
    afficher_contact()
elif choice == "Abonnés":
    afficher_formulaire_abonnes()
elif choice == "Nouveaux abonnements":
    afficher_nouveaux_abonnements()
elif choice == "Expirants":
    afficher_expirants()
elif choice == "Publicité":
    afficher_publicite()
