
import streamlit as st
from openai import OpenAI
import requests  # für mögliche Erweiterungen wie API-Validierung etc.

client = OpenAI(api_key=st.secrets["openai_api_key"])

st.set_page_config(page_title="Sanierungsfahrplan", page_icon="🏠")
st.title("🏠 KI-Sanierungsfahrplan")

adresse = st.text_input("Adresse", "Musterstraße 1")
baujahr = st.number_input("Baujahr", 1900, 2025, 1980)
heizung = st.selectbox("Heizung", ["Gas", "Öl", "Wärmepumpe"])
dach = st.checkbox("Dach gedämmt?")
keller = st.checkbox("Kellerdecke gedämmt?")
pv = st.checkbox("PV-Anlage vorhanden?")
wohnflaeche = st.number_input("Wohnfläche (m²)", 30, 500, 100)

def gpt_analyse(eingaben):
    prompt = (
        f"Adresse: {eingaben['adresse']}\n"
        f"Baujahr: {eingaben['baujahr']}\n"
        f"Heizung: {eingaben['heizung']}\n"
        f"Dachdämmung: {'ja' if eingaben['dach'] else 'nein'}\n"
        f"Kellerdeckendämmung: {'ja' if eingaben['keller'] else 'nein'}\n"
        f"PV-Anlage: {'ja' if eingaben['pv'] else 'nein'}\n"
        f"Wohnfläche: {eingaben['wohnflaeche']} m²\n\n"
        f"Gib empfohlene Sanierungsschritte mit Kosten, Förderprogrammen, CO2-Ersparnis und Zeitplan aus."
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Du bist ein Energieberater."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

if st.button("Fahrplan erstellen"):
    daten = {
        "adresse": adresse,
        "baujahr": baujahr,
        "heizung": heizung,
        "dach": dach,
        "keller": keller,
        "pv": pv,
        "wohnflaeche": wohnflaeche
    }
    st.markdown("⏳ Analyse läuft...")
    result = gpt_analyse(daten)
    st.success("Fertig!")
    st.text_area("Sanierungsfahrplan", result, height=300)
