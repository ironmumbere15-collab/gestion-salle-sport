import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ==============================
# 1. CONFIGURATION
# ==============================
st.set_page_config(page_title="365 Gym & Fitness", page_icon="🏋️", layout="wide")

# ==============================
# 2. CHARGEMENT / SAUVEGARDE
# ==============================
def load_data():
    try:
        df = pd.read_csv("abonnes.csv")
        df['Date_Fin'] = pd.to_datetime(df['Date_Fin'])
    except:
        data = {
            'Nom': ['Jean Dupont', 'Marie Martin', 'Isaac Kabuya', 'Sarah Luvumbu'],
            'Téléphone': ['+24381000000', '+24399000000', '+24382000000', '+24385000000'],
            'Date_Fin': ['2026-03-28', '2026-04-15', '2026-03-28', '2026-05-01'],
            'Type': ['Mensuel', 'Trimestriel', 'Mensuel', 'Annuel']
        }
        df = pd.DataFrame(data)
        df['Date_Fin'] = pd.to_datetime(df['Date_Fin'])
    return df

def save_data(df):
    df.to_csv("abonnes.csv", index=False)

df = load_data()

# ==============================
# 3. HEADER
# ==============================
col_logo, col_titre = st.columns([1, 4])
with col_logo:
    try:
        st.image("logo_365.jpg", width=120)
    except:
        pass

with col_titre:
    st.title("365 GYM & FITNESS")
    st.subheader("Tableau de Bord de Gestion")

st.divider()

# ==============================
# 4. MENU (3 POINTS)
# ==============================
menu = st.selectbox(
    "⋮ Navigation",
    ["📋 Liste des abonnés", "➕ Gestion des abonnés", "📊 Rapport mensuel"]
)

# ==============================
# 5. STATISTIQUES
# ==============================
today = datetime.now()
actifs = df[df['Date_Fin'] >= today]

expire_3j = df[
    (df['Date_Fin'] >= today) &
    (df['Date_Fin'] <= today + timedelta(days=3))
]

col1, col2, col3 = st.columns(3)
col1.metric("Total Abonnés", len(df))
col2.metric("Actifs", len(actifs))
col3.metric("Expirent (3 jours)", len(expire_3j))

st.divider()

# ==============================
# 📋 LISTE DES ABONNÉS
# ==============================
if menu == "📋 Liste des abonnés":

    st.subheader("📋 Liste complète")

    recherche = st.text_input("🔍 Rechercher un nom")

    df_filtre = df.copy()
    if recherche:
        df_filtre = df_filtre[df_filtre['Nom'].str.contains(recherche, case=False)]

    st.dataframe(df_filtre, use_container_width=True)

    st.download_button(
        "📥 Télécharger",
        df_filtre.to_csv(index=False),
        "liste_abonnes.csv"
    )

# ==============================
# ➕ GESTION (CRUD)
# ==============================
elif menu == "➕ Gestion des abonnés":

    action = st.radio("Choisir une action", ["Ajouter", "Modifier", "Supprimer"])

    # -------- AJOUTER --------
    if action == "Ajouter":
        st.subheader("➕ Ajouter un abonné")

        with st.form("add_form"):
            nom = st.text_input("Nom")
            tel = st.text_input("Téléphone")
            date_fin = st.date_input("Date de fin")
            type_ab = st.selectbox("Type", ["Mensuel", "Trimestriel", "Annuel"])

            submit = st.form_submit_button("Ajouter")

            if submit:
                new_row = pd.DataFrame([{
                    "Nom": nom,
                    "Téléphone": tel,
                    "Date_Fin": pd.to_datetime(date_fin),
                    "Type": type_ab
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                save_data(df)
                st.success("✅ Abonné ajouté avec succès")

    # -------- MODIFIER --------
    elif action == "Modifier":
        st.subheader("✏️ Modifier un abonné")

        nom_select = st.selectbox("Choisir un abonné", df['Nom'])

        data_select = df[df['Nom'] == nom_select].iloc[0]

        with st.form("edit_form"):
            new_nom = st.text_input("Nom", data_select['Nom'])
            new_tel = st.text_input("Téléphone", data_select['Téléphone'])
            new_date = st.date_input("Date fin", data_select['Date_Fin'])
            new_type = st.selectbox("Type", ["Mensuel", "Trimestriel", "Annuel"])

            submit = st.form_submit_button("Modifier")

            if submit:
                df.loc[df['Nom'] == nom_select, :] = [
                    new_nom, new_tel, pd.to_datetime(new_date), new_type
                ]
                save_data(df)
                st.success("✅ Modification réussie")

    # -------- SUPPRIMER --------
    elif action == "Supprimer":
        st.subheader("🗑️ Supprimer un abonné")

        nom_suppr = st.selectbox("Choisir à supprimer", df['Nom'])

        if st.button("Supprimer"):
            df = df[df['Nom'] != nom_suppr]
            save_data(df)
            st.warning("❌ Abonné supprimé")

# ==============================
# 📊 RAPPORT MENSUEL
# ==============================
elif menu == "📊 Rapport mensuel":

    st.subheader("📊 Rapport par mois")

    mois_dict = {
        "Janvier": 1, "Février": 2, "Mars": 3, "Avril": 4,
        "Mai": 5, "Juin": 6, "Juillet": 7, "Août": 8,
        "Septembre": 9, "Octobre": 10, "Novembre": 11, "Décembre": 12
    }

    mois = st.selectbox("Choisir le mois", list(mois_dict.keys()))

    mois_num = mois_dict[mois]

    rapport = df[df['Date_Fin'].dt.month == mois_num]

    st.dataframe(rapport, use_container_width=True)

    st.download_button(
        "📥 Télécharger rapport",
        rapport.to_csv(index=False),
        f"rapport_{mois}.csv"
    )

    st.info(f"Nombre d'abonnés pour {mois} : {len(rapport)}")
