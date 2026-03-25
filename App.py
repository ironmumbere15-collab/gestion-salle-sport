import streamlit as st
from supabase import create_client

# Connexion à ta base Supabase via les secrets
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# Lire les abonnés depuis la base de données
def recuperer_abonnes():
    res = supabase.table("abonnes").select("*").execute()
    return res.data

st.header("Liste des membres en direct de la base")
membres = recuperer_abonnes()
st.write(membres)
