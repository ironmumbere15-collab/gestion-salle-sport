import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="365 GYM & FITNESS", layout="wide")

# --- LOGIN ADMIN SIMPLE ---
admin_password = "monmotdepasse"  # REMPLACE PAR TON MOT DE PASSE
if 'admin_logged' not in st.session_state:
    st.session_state.admin_logged = False

if not st.session_state.admin_logged:
    st.title("🔒 Connexion Admin")
    pwd = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        if pwd == admin_password:
            st.session_state.admin_logged = True
            st.experimental_rerun()
        else:
            st.error("Mot de passe incorrect")
else:
    # --- SIDEBAR GAUCHE ---
    st.sidebar.image("logo.png", width=150)
    st.sidebar.markdown("<h3 style='text-align:center;color:#1a73e8;'>365 GYM & FITNESS</h3>", unsafe_allow_html=True)

    menu = ["Tableau de Bord", "Ajouter/Modifier Abonnés", "Notifier Abonnements", "Abonnés Expirés", "Forum", "Galerie", "Contact WhatsApp"]
    choix = st.sidebar.selectbox("", menu)

    # --- DONNÉES SIMULÉES ---
    data = {
        'Nom': ['Jean Dupont', 'Marie Martin', 'Isaac Kabuya', 'Sarah Luvumbu'],
        'Téléphone': ['+24381000000', '+24399000000', '+24382000000', '+24385000000'],
        'Date_Fin': ['2024-05-28', '2024-06-15', '2024-05-28', '2024-07-01'],
        'Type': ['Mensuel', 'Trimestriel', 'Mensuel', 'Annuel']
    }
    df = pd.DataFrame(data)
    df['Date_Fin'] = pd.to_datetime(df['Date_Fin'])

    aujourdhui = datetime.now()
    dans_3_jours = (aujourdhui + timedelta(days=3)).date()

    # --- STYLE CSS POUR LES COULEURS ---
    st.markdown("""
    <style>
    .stButton>button {background-color: #1a73e8; color: white;}
    .stMetric>div {background-color:#e3f2fd; border-radius:10px; padding:10px;}
    .stTextInput>div>input {border-radius:5px; border:1px solid #1a73e8;}
    .stDateInput>div>input {border-radius:5px; border:1px solid #1a73e8;}
    </style>
    """, unsafe_allow_html=True)

    # --- TABLEAU DE BORD ---
    if choix == "Tableau de Bord":
        st.title("🏋️ Tableau de Bord Premium")
        # Statistiques
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Abonnés", len(df))
        col2.metric("Abonnements Actifs", len(df[df['Date_Fin'].dt.date >= aujourdhui.date()]))
        col3.metric("Expirations (3j)", len(df[df['Date_Fin'].dt.date == dans_3_jours]))
        st.divider()

    # --- FORMULAIRE AJOUT/MODIFICATION/SUPPRESSION ---
    elif choix == "Ajouter/Modifier Abonnés" and st.session_state.admin_logged:
        st.image("logo.png", width=100)
        st.markdown("<h3 style='text-align:center;color:#1a73e8;'>365 GYM & FITNESS</h3>", unsafe_allow_html=True)
        st.header("📝 Ajouter / Modifier / Supprimer un abonné")
        with st.form("form_abonne"):
            nom = st.text_input("Nom")
            telephone = st.text_input("Téléphone")
            date_fin = st.date_input("Date de fin d'abonnement")

            st.markdown("### Actions")
            col1, col2, col3 = st.columns(3)
            submit_add = col1.form_submit_button("➕ Ajouter")
            submit_mod = col2.form_submit_button("✏️ Modifier")
            submit_del = col3.form_submit_button("🗑️ Supprimer")

            if submit_add:
                st.success(f"✅ Abonné {nom} ajouté !")
            elif submit_mod:
                st.info(f"✏️ Abonné {nom} modifié !")
            elif submit_del:
                st.warning(f"🗑️ Abonné {nom} supprimé !")

    # --- FORMULAIRE NOTIFIER ---
    elif choix == "Notifier Abonnements" and st.session_state.admin_logged:
        st.image("logo.png", width=100)
        st.markdown("<h3 style='text-align:center;color:#1a73e8;'>365 GYM & FITNESS</h3>", unsafe_allow_html=True)
        st.header("📣 Notifications WhatsApp pour abonnements proches de l'expiration")
        expirant_bientot = df[df['Date_Fin'].dt.date == dans_3_jours]
        if expirant_bientot.empty:
            st.info("Aucun abonnement n'expire dans 3 jours.")
        else:
            for index, row in expirant_bientot.iterrows():
                st.write(f"⚠️ {row['Nom']} - {row['Date_Fin'].date()}")
                message_auto = f"Salut {row['Nom']}, ton abonnement finit le {row['Date_Fin'].date()}."
                lien_wa = f"https://wa.me{row['Téléphone']}?text={message_auto}"
                st.markdown(f"[📱 Notifier via WhatsApp]({lien_wa})")

    # --- FORMULAIRE ABONNÉS EXPIRÉS ---
    elif choix == "Abonnés Expirés" and st.session_state.admin_logged:
        st.image("logo.png", width=100)
        st.markdown("<h3 style='text-align:center;color:#1a73e8;'>365 GYM & FITNESS</h3>", unsafe_allow_html=True)
        st.header("❌ Liste des abonnés expirés")
        expirés = df[df['Date_Fin'].dt.date < aujourdhui.date()]
        if expirés.empty:
            st.info("Aucun abonné n'a dépassé la date d'expiration.")
        else:
            st.dataframe(expirés)

    # --- FORUM, GALERIE, CONTACT ---
    elif choix == "Forum":
        st.header("💬 Forum de discussion (Public)")
    elif choix == "Galerie":
        st.header("📸 Galerie vidéos/photos (Public)")
    elif choix == "Contact WhatsApp":
        st.header("📱 Contact Direct (Public)")
