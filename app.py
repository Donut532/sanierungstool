
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import io
import json
from fpdf import FPDF
from openai import OpenAI

# === OpenAI API Setup ===
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# === Konfiguration ===
st.set_page_config(page_title="Sanierungsfahrplan", page_icon="🏡", layout="centered")

# === Logo & Titel ===
st.image("image.png", width=150)
st.title("🏠 Sanierungsfahrplan")

# === Formular ===
with st.form("sanierungs_formular"):
    col1, col2 = st.columns(2)

    with col1:
        adresse = st.text_input("📍 Adresse des Gebäudes")
        wohnfläche = st.number_input("📐 Wohnfläche (m²)", min_value=20, max_value=1000, value=120)
        fenster = st.selectbox("🪟 Fensterzustand", ["Alt", "Teilweise erneuert", "Neu"])
        solar = st.checkbox("☀️ Photovoltaikanlage vorhanden")

    with col2:
        baujahr = st.number_input("🏗️ Baujahr", min_value=1900, max_value=2025, value=1980)
        heizung = st.selectbox("🔥 Aktuelles Heizsystem", ["Gas", "Öl", "Fernwärme", "Wärmepumpe", "Pellet", "Elektro"])
        dach = st.checkbox("🏠 Dach ist gedämmt")
        keller = st.checkbox("🏚️ Keller ist gedämmt")

    abgeschickt = st.form_submit_button("🚀 Analyse starten")

# === GPT-Analyse ===
def gpt_vollanalyse(adresse, baujahr, wohnfläche, heizung, dach, keller, fenster, solar):
    prompt = f'''
    Erstelle eine strukturierte, professionelle Sanierungsempfehlung inklusive JSON-Ausgabe für die Diagrammerstellung.
    Antworte in folgendem Format:

    [TEXT]
    <Hier eine formelle, gegliederte Analyse und Empfehlung, z.B. mit Zwischenüberschriften>

    [DIAGRAMM]
    {{
        "title": "Einsparungspotential in € pro Jahr",
        "ylabel": "Euro pro Jahr",
        "data": {{
            "Ist-Zustand": 3000,
            "Zwischenschritt": 2200,
            "Ziel": 1100
        }}
    }}

    Gebäudedaten:
    - Adresse: {adresse}
    - Baujahr: {baujahr}
    - Wohnfläche: {wohnfläche} m²
    - Heizsystem: {heizung}
    - Dach gedämmt: {'Ja' if dach else 'Nein'}
    - Keller gedämmt: {'Ja' if keller else 'Nein'}
    - Fensterzustand: {fenster}
    - Photovoltaik: {'Ja' if solar else 'Nein'}
    '''

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

# Ergebnisanzeige
if abgeschickt:
    with st.spinner("🔍 Analyse läuft..."):
        antwort = gpt_vollanalyse(adresse, baujahr, wohnfläche, heizung, dach, keller, fenster, solar)

    if "[TEXT]" in antwort and "[DIAGRAMM]" in antwort:
        textteil = antwort.split("[TEXT]")[1].split("[DIAGRAMM]")[0].strip()
        diagramm_json = antwort.split("[DIAGRAMM]")[1].strip()

        st.session_state.analyse_text = textteil
        st.session_state.diagramm_data = json.loads(diagramm_json)

        st.subheader("📊 Ergebnis der Analyse")
        st.markdown(st.session_state.analyse_text)

        # Diagramm erzeugen
        fig, ax = plt.subplots()
        daten = pd.Series(st.session_state.diagramm_data["data"])
        daten.plot(kind="bar", ax=ax, color=["red", "orange", "green"])
        ax.set_ylabel(st.session_state.diagramm_data["ylabel"])
        ax.set_title(st.session_state.diagramm_data["title"])
        st.pyplot(fig)

        # PDF-Erzeugung
        def create_pdf(text, diagrammdaten, adresse, baujahr, wohnfläche):
            pdf = FPDF()
            pdf.add_page()
            try:
                pdf.image("image.png", x=10, y=8, w=30)
            except:
                pass
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "Sanierungsfahrplan", ln=True, align="C")
            pdf.set_font("Arial", "", 12)
            pdf.ln(10)
            pdf.cell(0, 10, f"Adresse: {adresse}", ln=True)
            pdf.cell(0, 10, f"Baujahr: {baujahr}", ln=True)
            pdf.cell(0, 10, f"Wohnfläche: {wohnfläche} m²", ln=True)
            pdf.ln(5)
            pdf.multi_cell(0, 10, text)
            pdf.ln(10)

            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, diagrammdaten["title"], ln=True)
            pdf.set_font("Arial", "", 12)
            for k, v in diagrammdaten["data"].items():
                pdf.cell(0, 10, f"{k}: {v} €", ln=True)

            pdf_bytes = pdf.output(dest='S').encode('latin1')
            return io.BytesIO(pdf_bytes)

        if st.button("📄 PDF erstellen"):
            pdf_buffer = create_pdf(
                st.session_state.analyse_text,
                st.session_state.diagramm_data,
                adresse, baujahr, wohnfläche
            )
            st.download_button("📥 PDF herunterladen", pdf_buffer, file_name="Sanierungsfahrplan.pdf")
    else:
        st.error("❌ Analyse konnte nicht verarbeitet werden.")
