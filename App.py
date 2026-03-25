import streamlit as st

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="365 Gym & Fitness", page_icon="🏋️", layout="wide")

# --- AFFICHAGE DU LOGO ET TITRE ---
col_logo, col_titre = st.columns([1, 4])
with col_logo:
    # Utilise l'URL de ton image GitHub ici
    st.image("logo.png", width=150)
with col_titre:
    st.title("365 GYM & FITNESS")
    st.subheader("Système de Gestion Intégré")

# Simulation de données (En attendant ta connexion Supabase complète)
data = {
    'Nom': ['Jean Dupont', 'Marie Martin', 'Isaac Kabuya', 'Sarah Luvumbu'],
    'Téléphone': ['+24381000000', '+24399000000', '+24382000000', '+24385000000'],
    'Date_Fin': ['2024-05-28', '2024-06-15', '2024-05-28', '2024-07-01'],
    'Type': ['Mensuel', 'Trimestriel', 'Mensuel', 'Annuel']
}
df = pd.DataFrame(data)
df['Date_Fin'] = pd.to_datetime(df['Date_Fin'])

# --- LOGIQUE DE DATE ---
aujourdhui = datetime.now()
dans_3_jours = (aujourdhui + timedelta(days=3)).date()

# --- INTERFACE ---
st.title("🏋️ Tableau de Bord Premium")

# 1. STATISTIQUES (RAPPORTS)
col1, col2, col3 = st.columns(3)
col1.metric("Total Abonnés", len(df))
col2.metric("Abonnements Actifs", len(df[df['Date_Fin'].dt.date >= aujourdhui.date()]))
col3.metric("Expirations (3j)", len(df[df['Date_Fin'].dt.date == dans_3_jours]))

# 2. ALERTES CRITIQUES (J-3)
expirant_bientot = df[df['Date_Fin'].dt.date == dans_3_jours]
if not expirant_bientot.empty:
    st.error(f"⚠️ {len(expirant_bientot)} abonnés expirent dans 3 jours !")
    st.dataframe(expirant_bientot)

st.divider()

# 3. RECHERCHE ET FILTRES
st.subheader("🔍 Rechercher un abonné")
c1, c2 = st.columns(2)
nom_cherche = c1.text_input("Par nom")
mois_cherche = c2.selectbox("Par mois d'expiration", ["Tous", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"])

# Application des filtres
df_filtre = df.copy()
if nom_cherche:
    df_filtre = df_filtre[df_filtre['Nom'].str.contains(nom_cherche, case=False)]
if mois_cherche != "Tous":
    # On filtre par le numéro du mois
    mois_index = ["Tous", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"].index(mois_cherche)
    df_filtre = df_filtre[df_filtre['Date_Fin'].dt.month == mois_index]

st.dataframe(df_filtre, use_container_width=True)

# 4. EXPORTER LE RAPPORT
st.download_button("📥 Télécharger le rapport (CSV)", df_filtre.to_csv(index=False), "rapport_salle.csv")
