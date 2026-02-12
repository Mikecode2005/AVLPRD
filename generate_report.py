import pandas as pd
import matplotlib.pyplot as plt
import os
import glob
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as PDFImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime

# --- CONFIGURATION ---
EXCEL_FILE = "batch_results_log.xlsx"
EVIDENCE_FOLDER = "test_results/evidence_plates"
REPORT_FILENAME = "ALPR & Data Logging.pdf"

# --- 1. PREPARE DATA & CHARTS ---
print("1. Reading Data & Generating Charts...")
df = pd.read_excel(EXCEL_FILE)

# Create a temporary folder for charts
if not os.path.exists("temp_charts"): os.makedirs("temp_charts")

# Chart A: Model Distribution (Pie)
plt.figure(figsize=(4, 4))
df['Model'].value_counts().plot.pie(autopct='%1.1f%%', colors=['#66bb6a', '#ef5350'])
plt.title("Nigerian vs International Detections")
plt.tight_layout()
plt.savefig("temp_charts/chart_model.png")
plt.close()

# Chart B: Top States (Bar)
plt.figure(figsize=(5, 4))
valid_states = df[~df['State_Origin'].isin(['Unknown', 'International', 'N/A'])]
if not valid_states.empty:
    valid_states['State_Origin'].value_counts().head(5).plot.bar(color='#42a5f5')
    plt.title("Top 5 Detected States")
    plt.tight_layout()
    plt.savefig("temp_charts/chart_states.png")
plt.close()

# --- 2. BUILD PDF ---
print("2. Building PDF Document...")
doc = SimpleDocTemplate(REPORT_FILENAME, pagesize=A4, rightMargin=15, leftMargin=15, topMargin=20, bottomMargin=20)
elements = []
styles = getSampleStyleSheet()

# -- Title Page --
title_style = ParagraphStyle(name='Title', parent=styles['Title'], fontSize=24, spaceAfter=20)
elements.append(Paragraph("AUTOMATED VEHICLE LICENSE PLATE RECOGNITION (ALPR) & DATA LOGGING SYSTEM REPORT", title_style))
elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
elements.append(Spacer(1, 20))

# -- Summary Section --
elements.append(Paragraph("<b>EXECUTIVE SUMMARY</b>", styles['Heading2']))
total_cars = len(df)
nigerian_cars = len(df[df['Model'] == 'Nigeria'])
intl_cars = len(df[df['Model'] == 'International'])
summary_text = f"""
This report summarizes the results of the automated License Plate Recognition scan.<br/><br/>
<b>Total Vehicles Processed:</b> {total_cars}<br/>
<b>Nigerian Plates Identified:</b> {nigerian_cars}<br/>
<b>International/Other Plates:</b> {intl_cars}<br/>
"""
elements.append(Paragraph(summary_text, styles['Normal']))
elements.append(Spacer(1, 10))

# -- Visuals (Stacked Vertically) --
chart1 = PDFImage("temp_charts/chart_model.png", width=300, height=300) # Increased size for better visibility
elements.append(chart1)
elements.append(Spacer(1, 10)) # Add small space between charts

try:
    chart2 = PDFImage("temp_charts/chart_states.png", width=350, height=250) # Increased size
    elements.append(chart2)
except:
    pass # If chart 2 fails, just skip it

elements.append(Spacer(1, 20))

# -- DETAILED EVIDENCE LOG --
elements.append(Paragraph("<b>DETAILED EVIDENCE LOG</b>", styles['Heading2']))
elements.append(Spacer(1, 10))

# Define Table Header
table_data = [['Date/Time', 'Model', 'State', 'Plate Number', 'Confidence', 'Evidence']]

# Loop through rows to find evidence and add to table
for index, row in df.iterrows():
    # Try to find the matching evidence image
    # We look for a file that contains the original Image_Name in the evidence folder
    evidence_img = "No Image"
    search_pattern = os.path.join(EVIDENCE_FOLDER, f"*{row['Image_Name']}")
    found_files = glob.glob(search_pattern)
    
    if found_files:
        # Found the cropped plate image!
        img_path = found_files[0]
        evidence_img = PDFImage(img_path, width=100, height=40) # Small thumbnail
    
    # Add row to table data
    table_data.append([
        str(row['Time_Stamp']),
        str(row['Model']),
        str(row['State_Origin']),
        str(row['Plate_Number']),
        str(row['Confidence']),
        evidence_img
    ])

# Create the fancy table
table = Table(table_data, colWidths=[100, 60, 70, 130, 70, 100])
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
]))

elements.append(table)

# --- 3. GENERATE ---
doc.build(elements)
print(f"3. SUCCESS! Report generated: {REPORT_FILENAME}")