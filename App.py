import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="365 GYM & FITNESS", layout="wide")

# --- SIDEBAR GAUCHE ---
st.sidebar.image("logo.png", width=200)
st.sidebar.markdown("### 365 GYM & FITNESS")

menu = ["Tableau de Bord", "Ajouter/Modifier Abonnés", "Notifier Abonnements", "Abonnés Expirés", "Forum", "Galerie", "Contact WhatsApp"]
choix = st.sidebar.selectbox("", menu)  # plus de mot "Navigation"

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

# --- TABLEAU DE BORD ---
if choix == "Tableau de Bord":
    st.title("🏋️ Tableau de Bord Premium")

    # Statistiques
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Abonnés", len(df))
    col2.metric("Abonnements Actifs", len(df[df['Date_Fin'].dt.date >= aujourdhui.date()]))
    col3.metric("Expirations (3j)", len(df[df['Date_Fin'].dt.date == dans_3_jours]))

    # Alertes J-3
    expirant_bientot = df[df['Date_Fin'].dt.date == dans_3_jours]
    if not expirant_bientot.empty:
        st.error(f"⚠️ {len(expirant_bientot)} abonnés expirent dans 3 jours !")
        st.dataframe(expirant_bientot)

    st.divider()

    # Recherche
    st.subheader("🔍 Rechercher un abonné")
    c1, c2 = st.columns(2)
    nom_cherche = c1.text_input("Par nom")
    mois_cherche = c2.selectbox("Par mois d'expiration", ["Tous", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"])

    df_filtre = df.copy()
    if nom_cherche:
        df_filtre = df_filtre[df_filtre['Nom'].str.contains(nom_cherche, case=False)]
    if mois_cherche != "Tous":
        mois_index = ["Tous", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"].index(mois_cherche)
        df_filtre = df_filtre[df_filtre['Date_Fin'].dt.month == mois_index]

    st.dataframe(df_filtre, use_container_width=True)
    st.download_button("📥 Télécharger le rapport (CSV)", df_filtre.to_csv(index=False), "rapport_salle.csv")

# --- FORMULAIRE AJOUT/MODIFICATION/SUPPRESSION ---
elif choix == "Ajouter/Modifier Abonnés":
    st.header("📝 Ajouter / Modifier / Supprimer un abonné")
    with st.form("form_abonne"):
        nom = st.text_input("Nom")
        telephone = st.text_input("Téléphone")
        type_abo = st.selectbox("Type d'abonnement", ["Mensuel", "Trimestriel", "Annuel"])
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
elif choix == "Notifier Abonnements":
    st.header("📣 Notifications WhatsApp pour abonnements proches de l'expiration")
    expirant_bientot = df[df['Date_Fin'].dt.date == dans_3_jours]
    if expirant_bientot.empty:
        st.info("Aucun abonnement n'expire dans 3 jours.")
    else:
        for index, row in expirant_bientot.iterrows():
            st.write(f"⚠️ {row['Nom']} - {row['Type']} - {row['Date_Fin'].date()}")
            message_auto = f"Salut {row['Nom']}, ton abonnement {row['Type']} finit le {row['Date_Fin'].date()}. Prêt pour ta séance ?"
            lien_wa = f"https://wa.me{row['Téléphone']}?text={message_auto}"
            st.markdown(f"[📱 Notifier via WhatsApp]({lien_wa})")

# --- FORMULAIRE ABONNÉS EXPIRÉS ---
elif choix == "Abonnés Expirés":
    st.header("❌ Liste des abonnés expirés")
    expirés = df[df['Date_Fin'].dt.date < aujourdhui.date()]
    if expirés.empty:
        st.info("Aucun abonné n'a dépassé la date d'expiration.")
    else:
        st.dataframe(expirés)

# --- FORUM ---
elif choix == "Forum":
    st.header("💬 Forum de discussion")
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    pseudo = st.text_input("Pseudo")
    msg = st.text_area("Message")
    if st.button("📨 Publier"):
        st.session_state.messages.append(f"**{pseudo}**: {msg}")

    for m in reversed(st.session_state.messages):
        st.write(m)

# --- GALERIE ---
elif choix == "Galerie":
    st.header("📸 Galerie vidéos/photos")
    st.info("Espace pour poster vos exploits (manuellement pour l'instant).")

# --- CONTACT WHATSAPP ---
elif choix == "Contact WhatsApp":
    st.header("📱 Contact Direct")
    mon_numero = "243000000000"  # REMPLACE PAR TON NUMÉRO
    message_auto = "Bonjour, j'ai une question sur mon abonnement."
    lien_wa = f"https://wa.me{mon_numero}?text={message_auto}"
    st.markdown(f"[📞 Contacter via WhatsApp]({lien_wa})")
