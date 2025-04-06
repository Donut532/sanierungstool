
# app.py – Sanierungstool v2 FINAL
# (Inklusive Diagramm, PDF-Export und LA-Branding)

import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import matplotlib.pyplot as plt
import tempfile
import os

# Branding
st.image("logo.png", width=150)
st.title("LA Sanierungen – KI-Sanierungsfahrplan")

# Eingabemaske
adresse = st.text_input("Adresse", "")
baujahr = st.number_input("Baujahr", 1900, 2025, 1970)
wohnflaeche = st.number_input("Wohnfläche (m²)", 50, 1000, 120)
stromverbrauch = st.number_input("Stromverbrauch (kWh/Jahr)", 500, 10000, 3000)
gasverbrauch = st.number_input("Gasverbrauch (kWh/Jahr)", 500, 20000, 9000)

ziel = st.selectbox("Fokus Ihrer Sanierung", ["CO₂-Reduktion", "Kosten sparen", "Effizienz erhöhen"])

# Auswertung
if st.button("Analyse starten"):
    # Platzhalter-Ausgabe
    st.success("Sanierungsanalyse abgeschlossen!")

    # Diagramm
    fig, ax = plt.subplots()
    ax.bar(["Strom", "Gas"], [stromverbrauch, gasverbrauch], color=["skyblue", "orange"])
    ax.set_title("Aktueller Energieverbrauch")
    st.pyplot(fig)

    # PDF Export
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as pdf_file:
        c = canvas.Canvas(pdf_file.name, pagesize=A4)
        c.drawImage("logo.png", 40, 750, width=100, preserveAspectRatio=True)
        c.drawString(150, 800, "Sanierungsfahrplan – LA Sanierungen")
        c.drawString(40, 730, f"Adresse: {adresse}")
        c.drawString(40, 710, f"Baujahr: {baujahr}")
        c.drawString(40, 690, f"Wohnfläche: {wohnflaeche} m²")
        c.drawString(40, 670, f"Strom: {stromverbrauch} kWh, Gas: {gasverbrauch} kWh")
        c.drawString(40, 650, f"Fokus: {ziel}")
        c.drawString(40, 620, "→ Maßnahmenempfehlung & Förderung folgen…")
        c.save()
        with open(pdf_file.name, "rb") as f:
            st.download_button("📄 PDF herunterladen", f, file_name="Sanierungsplan.pdf")
