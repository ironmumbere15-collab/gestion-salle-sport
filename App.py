# ================= PAGE ADMIN =================
elif st.session_state.page == "Admin":
    if not st.session_state.logged:
        pwd = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            if pwd=="1980":
                st.session_state.logged = True
                st.rerun()
            else:
                st.error("❌ Mauvais code")
    else:
        afficher_logo(100)
        st.header("⚙️ Panneau Admin")

        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Inscriptions","📊 Membres","📣 Publier","⏳ Expirations J-3","❌ Expirés"])

        # -------- INSCRIPTIONS --------
        with tab1:
            df = charger_depuis_supabase()
            noms = ["--- NOUVEL ABONNÉ ---"] + df["nom"].tolist()
            choix = st.selectbox("Rechercher un membre", noms)
            v_nom, v_wa, v_statut, v_duree = "", "", "Actif", 1
            if choix != "--- NOUVEL ABONNÉ ---":
                l = df[df["nom"]==choix].iloc[0]
                v_nom, v_wa, v_statut, v_duree = l["nom"], l["WhatsApp"], l["statut"], int(l["duree_mois"])
            
            st.markdown("<div style='background-color:#0b1c2c;padding:20px;border-radius:15px;'>", unsafe_allow_html=True)
            with st.form("form_inscription", clear_on_submit=True):
                col_a, col_b = st.columns(2)
                with col_a:
                    nom = st.text_input("Nom", value=v_nom)
                    wa = st.text_input("WhatsApp", value=v_wa)
                    stt = st.selectbox("Statut", ["Actif","Inactif"], index=0 if v_statut=="Actif" else 1)
                with col_b:
                    debut = st.date_input("Début", datetime.now())
                    mois = st.number_input("Durée (mois)", min_value=1, value=v_duree)
                fin = debut + pd.DateOffset(months=mois)
                if st.form_submit_button("💾 ENREGISTRER"):
                    supabase.table("abonnes").upsert({
                        "nom": nom,
                        "date_debut": debut.strftime("%Y-%m-%d"),
                        "duree_mois": int(mois),
                        "date_fin": fin.strftime("%Y-%m-%d"),
                        "WhatsApp": wa,
                        "statut": stt
                    }, on_conflict="WhatsApp").execute()
                    st.success("✅ Enregistré !")
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # -------- MEMBRES --------
        with tab2:
            df = charger_depuis_supabase()
            for idx, r in df.iterrows():
                st.markdown("<div style='background-color:#0b1c2c;padding:10px;margin-bottom:10px;border-radius:10px;display:flex;justify-content:space-between;align-items:center;'>", unsafe_allow_html=True)
                st.markdown(f"**{r['nom']}** | {r['WhatsApp']} | Statut: {r['statut']} | Fin: {r['date_fin']}", unsafe_allow_html=True)
                col_btn = st.columns([1,1])
                with col_btn[0]:
                    if st.button(f"Modifier-{idx}"):
                        st.session_state.edit = r["WhatsApp"]
                        st.session_state.page = "Admin"
                        st.rerun()
                with col_btn[1]:
                    if st.button(f"Supprimer-{idx}"):
                        supabase.table("abonnes").delete().eq("WhatsApp", r["WhatsApp"]).execute()
                        st.success("✅ Supprimé !")
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        # -------- PUBLIER --------
        with tab3:
            t_pub = st.selectbox("Type", ["Photo","Vidéo","Message"])
            fichier = st.file_uploader("Choisir un média", type=["png","jpg","jpeg","mp4"])
            if fichier:
                if t_pub=="Photo": st.image(fichier, width=300)
                if t_pub=="Vidéo": st.video(fichier)
            st.markdown("<div style='background-color:#0b1c2c;padding:20px;border-radius:15px;'>", unsafe_allow_html=True)
            with st.form("form_pub", clear_on_submit=True):
                legende_txt = st.text_area("Légende")
                if st.form_submit_button("📢 PUBLIER"):
                    if fichier:
                        nom_f = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{fichier.name}"
                        supabase.storage.from_("medias").upload(nom_f, fichier.getvalue())
                        res_url = supabase.storage.from_("medias").get_public_url(nom_f)
                        url_final = res_url if isinstance(res_url,str) else res_url.public_url
                        supabase.table("publicite").insert({"type":t_pub,"url_media":url_final,"legende":legende_txt}).execute()
                    else:
                        supabase.table("publicite").insert({"type":"Message","url_media":"","legende":legende_txt}).execute()
                    st.success("✅ Publication réussie !")
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # -------- EXPIRATIONS J-3 --------
        with tab4:
            df_s = charger_depuis_supabase()
            if not df_s.empty:
                df_s['date_fin_dt'] = pd.to_datetime(df_s['date_fin'])
                df_s['restant'] = (df_s['date_fin_dt'] - pd.Timestamp(datetime.now().date())).dt.days
                alerte = df_s[(df_s['restant']<=3) & (df_s['restant']>=0) & (df_s['statut'].str.lower()=="actif")]
                for _, r in alerte.iterrows():
                    num_raw = "".join(filter(str.isdigit,str(r["WhatsApp"])))
                    num_final = "243" + (num_raw[1:] if num_raw.startswith("0") else num_raw if num_raw.startswith("243") else num_raw)
                    msg = f"Bonjour {r['nom']} ! Votre abonnement se termine le {r['date_fin']}."
                    wa_url = f"https://wa.me/{urllib.parse.quote(msg)}?phone={num_final}"
                    st.markdown(f"<div style='background-color:#ff6b2c;padding:10px;border-radius:10px;margin-bottom:10px;'>🔔 {r['nom']} | Fin: {r['date_fin']} 👉 <a href='{wa_url}' target='_blank'>Notifier WhatsApp</a></div>", unsafe_allow_html=True)

        # -------- EXPIRÉS --------
        with tab5:
            df_s = charger_depuis_supabase()
            if not df_s.empty:
                df_s['date_fin_dt'] = pd.to_datetime(df_s['date_fin'])
                df_s['restant'] = (df_s['date_fin_dt'] - pd.Timestamp(datetime.now().date())).dt.days
                exp = df_s[df_s['restant']<0]
                for idx, r in exp.iterrows():
                    st.markdown("<div style='background-color:#ff4c4c;padding:10px;border-radius:10px;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center;'>", unsafe_allow_html=True)
                    st.markdown(f"❌ {r['nom']} expiré depuis {abs(r['restant'])} jours", unsafe_allow_html=True)
                    col_btn = st.columns([1,1])
                    with col_btn[0]:
                        if st.button(f"Modifier-exp-{idx}"):
                            st.session_state.edit = r["WhatsApp"]
                            st.session_state.page = "Admin"
                            st.rerun()
                    with col_btn[1]:
                        if st.button(f"Supprimer-exp-{idx}"):
                            supabase.table("abonnes").delete().eq("WhatsApp", r["WhatsApp"]).execute()
                            st.success("✅ Supprimé !")
                            st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
