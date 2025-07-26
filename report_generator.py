import pandas as pd
from datetime import datetime
from fpdf import FPDF

CSV_FILE = "transactions.csv"

def generate_daily_pdf_report(output_path="daily_report.pdf"):
    df = pd.read_csv(CSV_FILE, parse_dates=["date"])
    today = pd.to_datetime(datetime.now().date())
    today_df = df[df['date'] == today]

    total_in = today_df[today_df['type'] == 'In']['amount'].sum()
    total_out = today_df[today_df['type'] == 'Out']['amount'].sum()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Nusrat Furniture Daily Report", ln=True, align="C")

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Date: {today.strftime('%Y-%m-%d')}", ln=True)
    pdf.cell(200, 10, f"Total Incoming: Rs. {total_in:,.2f}", ln=True)
    pdf.cell(200, 10, f"Total Outgoing: Rs. {total_out:,.2f}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(40, 10, "Name")
    pdf.cell(40, 10, "Job")
    pdf.cell(40, 10, "Reason")
    pdf.cell(30, 10, "Amount")
    pdf.cell(20, 10, "Type")
    pdf.ln()

    pdf.set_font("Arial", size=10)
    for _, row in today_df.iterrows():
        pdf.cell(40, 10, str(row['name']))
        pdf.cell(40, 10, str(row['job']))
        pdf.cell(40, 10, str(row['reason']))
        pdf.cell(30, 10, f"{row['amount']}")
        pdf.cell(20, 10, str(row['type']))
        pdf.ln()

    pdf.output(output_path)
    return output_path
