import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configuration de la page
st.set_page_config(page_title="Ma Salle de Sport", layout="wide")

# --- TITRE ET NAVIGATION ---
st.title("🏋️ Gestion de ma Salle de Sport")
menu = ["Tableau de Bord", "Forum de Discussion", "Galerie Vidéos/Photos", "Contact WhatsApp"]
choix = st.sidebar.selectbox("Menu", menu)

# --- DONNÉES SIMULÉES (À remplacer par ton fichier CSV plus tard) ---
if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- SECTION 1 : TABLEAU DE BORD (GESTION) ---
if choix == "Tableau de Bord":
    st.header("👥 Suivi des Abonnés")
    # Exemple de données
    data = {
        'Nom': ['Jean Dupont', 'Marie Martin'],
        'Téléphone': ['+24381000000', '+24399000000'],
        'Fin Abonnement': ['2024-05-25', '2024-06-15']
    }
    df = pd.DataFrame(data)
    st.table(df)

# --- SECTION 2 : FORUM ---
elif choix == "Forum de Discussion":
    st.header("💬 Forum de la Communauté")
    pseudo = st.text_input("Ton pseudo")
    msg = st.text_area("Ton message")
    if st.button("Publier"):
        st.session_state.messages.append(f"**{pseudo}**: {msg}")
    
    st.write("---")
    for m in reversed(st.session_state.messages):
        st.write(m)

# --- SECTION 3 : GALERIE ---
elif choix == "Galerie Vidéos/Photos":
    st.header("📸 Galerie de la Salle")
    st.info("Ici tu peux poster tes exploits !")
    # Note : Pour les vraies vidéos, on utilise st.video("lien_url")
    st.write("Espace pour tes photos et vidéos d'entraînement.")

# --- SECTION 4 : CONTACT WHATSAPP ---
elif choix == "Contact WhatsApp":
    st.header("📱 Contact Direct")
    mon_numero = "243000000000" # REMPLACE PAR TON NUMÉRO
    message_auto = "Bonjour, j'ai une question sur mon abonnement."
    lien_wa = f"https://wa.me{mon_numero}?text={message_auto}"
    
    st.write("Besoin d'aide ? Clique sur le bouton ci-dessous :")
    st.link_button("Ouvrir WhatsApp", lien_wa)
