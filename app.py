import streamlit as st
import openai
import os
import pandas as pd
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import tempfile

# Passwortschutz
def check_password():
    def password_entered():
        if st.session_state["password"] == "LA2024":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Passwort", type="password", on_change=password_entered, key="password")
        st.stop()
    elif not st.session_state["password_correct"]:
        st.text_input("Passwort", type="password", on_change=password_entered, key="password")
        st.error("❌ Falsches Passwort")
        st.stop()

check_password()

st.set_page_config(page_title="Sanierungsfahrplan PRO", layout="centered", page_icon="🏡")
st.title("🏡 Sanierungsfahrplan PRO")

adresse = st.text_input("Adresse des Gebäudes", "Musterstraße 12, Beispielstadt")
baujahr = st.number_input("Baujahr", 1900, datetime.now().year, 1970)
heizung = st.selectbox("Heizsystem", ["Gas", "Öl", "Wärmepumpe", "Strom", "Fernwärme", "Pellet", "Sonstiges"])
wohnflaeche = st.number_input("Wohnfläche (m²)", 50, 1000, 120)
dach = st.checkbox("Dach gedämmt")
keller = st.checkbox("Kellerdecke gedämmt")
pv = st.checkbox("Photovoltaik vorhanden")

def check_foerderung(m):
    mapping = {
        "Dachdämmung": ("BEG EM", 20),
        "Heizung tauschen": ("KfW 261", 30),
        "Fenster erneuern": ("BEG EM", 15),
        "Photovoltaik": ("KfW 270", 10)
    }
    return mapping.get(m, ("Nicht förderfähig", 0))

@st.cache_data(show_spinner=False)
def gpt_analyse(daten):
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Du bist ein Energieberater."},
            {"role": "user", "content": f"""Analysiere folgendes Gebäude:
Adresse: {daten['adresse']}
Baujahr: {daten['baujahr']}
Heizung: {daten['heizung']}
Dachdämmung: {"ja" if daten['dach'] else "nein"}
Kellerdeckendämmung: {"ja" if daten['keller'] else "nein"}
PV-Anlage: {"ja" if daten['pv'] else "nein"}
Wohnfläche: {daten['wohnflaeche']} m²

Empfohlene Maßnahmen, CO₂-Einsparung, Förderungen, Zeitplan bitte als Liste.
"""}
        ],
        temperature=0.3
    )
    return res.choices[0].message.content

def export_pdf(text, adresse):
    path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    doc = SimpleDocTemplate(path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [Paragraph(f"Sanierungsfahrplan für: {adresse}", styles['Title']),
             Spacer(1, 12),
             Paragraph("Erstellt am: " + datetime.today().strftime("%d.%m.%Y"), styles['Normal']),
             Spacer(1, 12)]
    for block in text.split("\n\n"):
        story.append(Paragraph(block.replace("\n", "<br/>"), styles['Normal']))
        story.append(Spacer(1, 12))
    doc.build(story)
    return path

if st.button("🚀 Fahrplan erstellen"):
    eingaben = {
        "adresse": adresse,
        "baujahr": baujahr,
        "heizung": heizung,
        "dach": dach,
        "keller": keller,
        "pv": pv,
        "wohnflaeche": wohnflaeche
    }
    with st.spinner("Analyse wird durchgeführt..."):
        ergebnis = gpt_analyse(eingaben)
    st.success("✅ Analyse abgeschlossen!")
    st.markdown("### 📄 Sanierungsfahrplan")
    st.markdown(ergebnis)
    pdf_path = export_pdf(ergebnis, adresse)
    with open(pdf_path, "rb") as f:
        st.download_button("📥 PDF herunterladen", f, file_name="Sanierungsfahrplan.pdf")

import matplotlib.pyplot as plt

def berechne_kosten_und_co2():
    return [
        {"Jahr": "2024", "Maßnahme": "Dachdämmung", "Kosten": 12000, "CO2_Einsparung": 1.2},
        {"Jahr": "2025", "Maßnahme": "Heizung tauschen", "Kosten": 18000, "CO2_Einsparung": 2.1},
        {"Jahr": "2026", "Maßnahme": "Fenster erneuern", "Kosten": 8000, "CO2_Einsparung": 0.8},
        {"Jahr": "2027", "Maßnahme": "PV-Anlage installieren", "Kosten": 10000, "CO2_Einsparung": 1.6}
    ]

if st.button("📊 Maßnahmen & Diagramm anzeigen"):
    daten = berechne_kosten_und_co2()
    df = pd.DataFrame(daten)
    st.session_state["analyse_df"] = df
    st.markdown("### 💸 Maßnahmenübersicht")
    st.dataframe(df)

    st.markdown("### 📈 CO₂-Einsparung nach Jahr")
    fig, ax = plt.subplots()
    ax.bar(df["Jahr"], df["CO2_Einsparung"], color='green')
    ax.set_ylabel("Einsparung (t/Jahr)")
    st.pyplot(fig)

    st.markdown("### 💰 Investitionen")
    fig2, ax2 = plt.subplots()
    ax2.bar(df["Jahr"], df["Kosten"], color='orange')
    ax2.set_ylabel("Kosten (€)")
    st.pyplot(fig2)

if "kosten" not in st.session_state:
    st.session_state["kosten"] = {
        "Dachdämmung": st.slider("Kosten Dachdämmung (€)", 5000, 20000, 12000),
        "Heizung tauschen": st.slider("Kosten Heizung (€)", 8000, 25000, 18000),
        "Fenster erneuern": st.slider("Kosten Fenster (€)", 4000, 15000, 8000),
        "PV-Anlage installieren": st.slider("Kosten PV (€)", 5000, 20000, 10000)
    }

if "co2" not in st.session_state:
    st.session_state["co2"] = {
        "Dachdämmung": st.slider("CO₂-Einsparung Dach (t)", 0.5, 3.0, 1.2),
        "Heizung tauschen": st.slider("CO₂-Einsparung Heizung (t)", 1.0, 4.0, 2.1),
        "Fenster erneuern": st.slider("CO₂-Einsparung Fenster (t)", 0.3, 2.0, 0.8),
        "PV-Anlage installieren": st.slider("CO₂-Einsparung PV (t)", 1.0, 3.0, 1.6)
    }

def generate_interactive_data():
    jahre = ["2024", "2025", "2026", "2027"]
    massnahmen = ["Dachdämmung", "Heizung tauschen", "Fenster erneuern", "PV-Anlage installieren"]
    return [
        {"Jahr": jahr, "Maßnahme": m, "Kosten": st.session_state["kosten"][m], "CO2_Einsparung": st.session_state["co2"][m]}
        for jahr, m in zip(jahre, massnahmen)
    ]

if st.button("📊 Interaktive Analyse anzeigen"):
    daten = generate_interactive_data()
    df = pd.DataFrame(daten)
    st.session_state["analyse_df"] = df
    st.dataframe(df)

    st.markdown("### 📉 CO₂-Einsparung")
    fig, ax = plt.subplots()
    ax.bar(df["Jahr"], df["CO2_Einsparung"], color='green')
    ax.set_ylabel("CO₂-Einsparung (t)")
    st.pyplot(fig)

    st.markdown("### 💰 Investitionen")
    fig2, ax2 = plt.subplots()
    ax2.bar(df["Jahr"], df["Kosten"], color='orange')
    ax2.set_ylabel("Kosten (€)")
    st.pyplot(fig2)

    st.success("Daten aktualisiert. Beim PDF-Export werden Diagramme eingebettet.")

def export_pdf_with_charts(text, adresse, df):
    path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    doc = SimpleDocTemplate(path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [Paragraph(f"Sanierungsfahrplan für: {adresse}", styles['Title']),
             Spacer(1, 12),
             Paragraph("Erstellt am: " + datetime.today().strftime("%d.%m.%Y"), styles['Normal']),
             Spacer(1, 12)]
    for block in text.split("\n\n"):
        story.append(Paragraph(block.replace("\n", "<br/>"), styles['Normal']))
        story.append(Spacer(1, 12))

    # Diagramm: CO₂-Einsparung
    d = Drawing(400, 200)
    chart = VerticalBarChart()
    chart.data = [df["CO2_Einsparung"].tolist()]
    chart.categoryAxis.categoryNames = df["Jahr"].tolist()
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max(df["CO2_Einsparung"]) + 1
    chart.barWidth = 10
    chart.width = 350
    chart.height = 150
    chart.x = 25
    chart.y = 25
    d.add(chart)
    story.append(d)
    story.append(Spacer(1, 24))

    doc.build(story)
    return path

# Überschreibe PDF-Funktion
if "export_pdf" in globals():
    export_pdf = export_pdf_with_charts
