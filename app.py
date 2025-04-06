
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import io
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
def gpt_analyse(adresse, baujahr, wohnfläche, heizung, dach, keller, fenster, solar):
    prompt = (
        f"Erstelle eine professionelle und übersichtliche Sanierungsempfehlung für ein Gebäude mit folgenden Eigenschaften:\n"
        f"- Adresse: {adresse}\n"
        f"- Baujahr: {baujahr}\n"
        f"- Wohnfläche: {wohnfläche} m²\n"
        f"- Heizsystem: {heizung}\n"
        f"- Dach gedämmt: {'Ja' if dach else 'Nein'}\n"
        f"- Keller gedämmt: {'Ja' if keller else 'Nein'}\n"
        f"- Fensterzustand: {fenster}\n"
        f"- Photovoltaik: {'Ja' if solar else 'Nein'}\n\n"
        f"Formuliere den Text wie ein offizielles Dokument. Verwende eine klare Gliederung mit Absätzen und Zwischenüberschriften."
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

# === Analyse anzeigen ===
if abgeschickt:
    with st.spinner("🔍 Analyse läuft..."):
        analyse_text = gpt_analyse(adresse, baujahr, wohnfläche, heizung, dach, keller, fenster, solar)

    st.subheader("📊 Ergebnis der Analyse")
    st.markdown(analyse_text)

    # Beispiel-Diagramm
    fig, ax = plt.subplots()
    daten = pd.Series([3000, 2200, 1100], index=["Ist-Zustand", "Zwischenschritt", "Ziel"])
    daten.plot(kind="bar", ax=ax, color=["red", "orange", "green"])
    ax.set_ylabel("Energiekosten in €/Jahr")
    ax.set_title("🔋 Entwicklung der Energiekosten")
    st.pyplot(fig)

    # PDF-Erstellung (professioneller Stil)
    def create_pdf(text, adresse, baujahr, wohnfläche):
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

        pdf_bytes = pdf.output(dest='S').encode('latin1')
        return io.BytesIO(pdf_bytes)

    if st.button("📄 Professionelle PDF erstellen"):
        pdf_buffer = create_pdf(analyse_text, adresse, baujahr, wohnfläche)
        st.download_button("📥 PDF herunterladen", pdf_buffer, file_name="Sanierungsfahrplan.pdf")
