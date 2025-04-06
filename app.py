# Beispielcode zur Integration des neuen PDF-Exports im Streamlit-Tool

import matplotlib.pyplot as plt
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import os

class PDF(FPDF):
    def header(self):
        if os.path.exists("logo.png"):
            self.image("logo.png", 170, 8, 30)
        self.set_font("Arial", 'B', 14)
        self.cell(0, 10, 'Sanierungsfahrplan', ln=True, align='L')
        self.set_font("Arial", '', 10)
        self.cell(0, 10, f'Erstellt am: {datetime.now().strftime("%d.%m.%Y")}', ln=True, align='L')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Seite {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 10, body)
        self.ln()

    def add_table(self, data, col_widths):
        self.set_font("Arial", size=10)
        for i, row in enumerate(data):
            for j, datum in enumerate(row):
                self.cell(col_widths[j], 10, str(datum), border=1)
            self.ln()

    def add_image(self, image_path, x=10, y=None, w=180):
        self.image(image_path, x, y, w)

def create_diagram(einsparung):
    fig, ax = plt.subplots()
    jahre = list(einsparung.keys())
    werte = list(einsparung.values())
    ax.bar(jahre, werte)
    ax.set_title('CO2-Einsparung pro Jahr')
    ax.set_ylabel('kg CO2')
    plt.tight_layout()
    diagramm_path = "diagramm.png"
    plt.savefig(diagramm_path)
    plt.close()
    return diagramm_path

def export_full_report(adresse, daten):
    pdf = PDF()
    pdf.add_page()

    # Deckblatt
    pdf.chapter_title(f"Sanierungsfahrplan für: {adresse}")
    pdf.chapter_body("Individuell KI-generiert, übersichtlich, förderfähig.")

    # Zusammenfassung
    pdf.chapter_title("Zusammenfassung")
    pdf.chapter_body("Diese Seite enthält eine Übersicht der Sanierungsziele und Kernmetriken.")
    pdf.add_table([
        ["Energiekosten vorher", "Energiekosten nachher", "CO2-Ersparnis", "Förderanteil"],
        ["2.800 €/Jahr", "1.100 €/Jahr", "5.200 kg", "30%"]
    ], [50, 50, 45, 45])

    # Jahresplan
    pdf.chapter_title("Sanierungsfahrplan - Zeitlicher Ablauf")
    jahresplan = [
        ["2024", "Dachdämmung", "12.000 €", "BEG EM 20%", "2.300 kg"],
        ["2025", "Wärmepumpe + Fenster", "25.000 €", "KfW 261 30%", "4.500 kg"],
        ["2026", "PV-Anlage", "8.000 €", "KfW 270 10%", "n/a"]
    ]
    pdf.add_table([
        ["Jahr", "Maßnahme", "Kosten", "Förderung", "CO2-Ersparnis"]
    ] + jahresplan, [20, 60, 30, 40, 40])

    # Diagramm einfügen
    einsparung = {"2024": 2300, "2025": 4500}
    diagramm = create_diagram(einsparung)
    pdf.add_page()
    pdf.chapter_title("Diagramm: CO2-Einsparung")
    pdf.add_image(diagramm)

    # Hinweis
    pdf.add_page()
    pdf.chapter_title("Hinweis")
    pdf.chapter_body("Dieses Dokument dient zur Unterstützung bei Förderanträgen. Alle Angaben ohne Gewähr. Für verbindliche Daten konsultieren Sie bitte einen Energieberater.")

    # Speichern
    filename = f"Sanierungsfahrplan_{adresse.replace(' ', '_')}.pdf"
    pdf.output(filename)
    return filename
