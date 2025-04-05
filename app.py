
import os

# Seitenwahl
st.sidebar.title("🔧 Einstellungen")
page = st.sidebar.radio("Navigieren", ["Sanierungsfahrplan", "API-Key prüfen", "API-Key bearbeiten"])

# API-Key aus secrets oder fallback auf Umgebungsvariable
api_key = st.secrets.get("openai_api_key") or os.getenv("OPENAI_API_KEY", "")

# API-Key Testfunktion
def check_openai_key(key):
    try:
        openai.api_key = key  # ersetzt
        test = openai.ChatCompletion.create  # ersetzt(
            model="standard-analyse",
            messages=[{"role": "user", "content": "Sag mir ein zufälliges deutsches Sprichwort"}],
            max_tokens=50
        )
        return test.choices[0].message.content
    except Exception as e:
        return f"❌ Fehler: {e}"

# Seite: Key prüfen
if page == "API-Key prüfen":
    st.subheader("🔐 Modulanbieter API-Key prüfen")
    if api_key:
        result = check_openai_key(api_key)
        st.write("Antwort von Modulanbieter:", result)
    else:
        st.warning("Kein API-Key gefunden.")

# Seite: Key bearbeiten
elif page == "API-Key bearbeiten":
    st.subheader("✏️ API-Key bearbeiten")
    new_key = st.text_input("Gib deinen Modulanbieter API-Key hier ein", value=api_key, type="password")
    if st.button("💾 Speichern"):
        secrets_path = Path(".streamlit/secrets.toml")
        with open(secrets_path, "w") as f:
            f.write(f'openai_api_key = "{new_key}"\n')
        st.success("API-Key wurde gespeichert. Bitte App neu starten.")

# Hauptseite bleibt bestehen
else:

    import webbrowser
    webbrowser.open('http://localhost:8501')
    
    
    import streamlit as st
    import openai
    from datetime import datetime
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    import tempfile
    
    # API-Key aus secrets
    openai.api_key = st.secrets.get("openai_api_key", "DEIN_OPENAI_KEY")
    
    st.set_page_config(page_title="Sanierungsfahrplan PRO", layout="centered")
    st.title("🏡 automatisierter Sanierungsfahrplan – PRO")
    
    # Eingabemaske
    adresse = st.text_input("🏠 Adresse des Gebäudes", "Musterstraße 12, Beispielstadt")
    baujahr = st.number_input("Baujahr", 1900, datetime.now().year, 1975)
    heizung = st.selectbox("Aktuelles Heizsystem", ["Öl", "Gas", "Wärmepumpe", "Pellet", "Fernwärme", "Strom", "Sonstiges"])
    dach = st.checkbox("✅ Dach ist gedämmt")
    keller = st.checkbox("✅ Kellerdecke ist gedämmt")
    pv = st.checkbox("✅ Photovoltaik-Anlage vorhanden")
    wohnflaeche = st.number_input("Wohnfläche (m²)", 50, 1000, 120)
    
    def gpt_analyse(daten):
        prompt = f"""
        Du bist ein Energieberater. Analysiere folgendes Gebäude:
        Adresse: {daten['adresse']}
        Baujahr: {daten['baujahr']}
        Heizung: {daten['heizung']}
        Dachdämmung: {'ja' if daten['dach'] else 'nein'}
        Kellerdeckendämmung: {'ja' if daten['keller'] else 'nein'}
        PV-Anlage: {'ja' if daten['pv'] else 'nein'}
        Wohnfläche: {daten['wohnflaeche']} m²
    
        Gib empfohlene Sanierungsschritte, geschätzte Kosten, mögliche Förderprogramme und CO₂-Einsparung als Liste mit Jahresplan zurück.
        """
        res = openai.ChatCompletion.create  # ersetzt(
            model="standard-analyse",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return res.choices[0].message.content
    
    def export_pdf_structured(text, adresse):
        path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
        doc = SimpleDocTemplate(path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        story.append(Paragraph(f"Sanierungsfahrplan für: {adresse}", styles['Title']))
        story.append(Paragraph("Generiert am: " + datetime.today().strftime("%d.%m.%Y"), styles['Normal']))
        story.append(Spacer(1, 12))
        for block in text.split("\n\n"):
            story.append(Paragraph(block.strip().replace("\n", "<br/>"), styles['Normal']))
            story.append(Spacer(1, 12))
        doc.build(story)
        return path
    
    if st.button("🚀 Fahrplan jetzt erstellen"):
        eingaben = {
            "adresse": adresse,
            "baujahr": baujahr,
            "heizung": heizung,
            "dach": dach,
            "keller": keller,
            "pv": pv,
            "wohnflaeche": wohnflaeche
        }
        with st.spinner("Analysemodul analysiert das Gebäude..."):
            text_out = gpt_analyse(eingaben)
    
        st.success("Analyse abgeschlossen!")
        st.markdown("### 📄 KI-Sanierungsplan")
        st.markdown(text_out)
    
        pdf_path = export_pdf_structured(text_out, adresse)
        with open(pdf_path, "rb") as f:
            st.download_button("📥 PDF herunterladen", f, file_name="Sanierungsfahrplan_Pro.pdf")