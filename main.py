import streamlit as st
import pandas as pd
import uuid
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import time
from supabase import create_client
import base64
import tempfile
import shutil
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# --- Page Configuration ---
st.set_page_config(
    page_title="Nusrat Furniture - Transaction Manager",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🏢"
)

# --- Ultra Modern CSS with Animations ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    * { font-family: 'Poppins', sans-serif !important; }
    .main { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); background-attachment: fixed; position: relative; overflow: hidden; }
    .stApp { background: transparent; }
    .main .block-container { background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 20px; margin: 1rem; padding: 2rem; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1); animation: slideInUp 0.8s ease-out; }
    .main::before { content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(255,255,255,0.1) 10%, transparent 10.01%); background-size: 20px 20px; animation: floatBackground 15s linear infinite; z-index: -1; }
    @keyframes floatBackground { 0% { transform: translate(0, 0); } 100% { transform: translate(-100px, -100px); } }
    .floating-plus { position: fixed; bottom: 30px; right: 30px; width: 60px; height: 60px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3); cursor: pointer; z-index: 1000; animation: pulsePlus 1.5s infinite; transition: transform 0.3s ease; }
    .floating-plus:hover { transform: scale(1.1); box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4); }
    @keyframes pulsePlus { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.1); } }
    .floating-plus span { font-size: 2rem; color: white; font-weight: 700; }
    @keyframes slideInUp { from { opacity: 0; transform: translateY(50px); } to { opacity: 1; transform: translateY(0); } }
    .animated-button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white !important; border: none !important; border-radius: 15px !important; padding: 0.8rem 2rem !important; font-weight: 600 !important; font-size: 1rem !important; transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important; box-shadow: 0 8px 30px rgba(102, 126, 234, 0.3) !important; position: relative !important; overflow: hidden !important; animation: fadeInScale 0.6s ease-out !important; }
    .animated-button::before { content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent); transition: left 0.5s; }
    .animated-button:hover::before { left: 100%; }
    .animated-button:hover { transform: translateY(-3px) scale(1.02) !important; box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4) !important; }
    .stButton > button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; color: white !important; border: none !important; border-radius: 15px !important; padding: 0.8rem 2rem !important; font-weight: 600 !important; font-size: 1rem !important; transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important; box-shadow: 0 8px 30px rgba(102, 126, 234, 0.3) !important; position: relative !important; overflow: hidden !important; }
    .stButton > button:hover { transform: translateY(-3px) scale(1.02) !important; box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4) !important; }
    .metric-card { background: #ffffff; border: 1px solid rgba(102, 126, 234, 0.2); padding: 1.5rem; border-radius: 15px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); margin: 0.5rem 0; transition: all 0.3s ease; animation: fadeInScale 0.6s ease-out; text-align: center; }
    .metric-card:hover { animation: glow 1.5s ease-in-out infinite alternate; transform: scale(1.02); }
    .success-card { background: #a8e6cf; color: #2d5016; border: 1px solid rgba(136, 216, 163, 0.5); }
    .danger-card { background: #fab1a0; color: #8b0000; border: 1px solid rgba(250, 177, 160, 0.5); }
    .neutral-card { background: #c7d2fe; color: #4c1d95; border: 1px solid rgba(199, 210, 254, 0.5); }
    .header-title { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; font-size: 3.5rem; font-weight: 800; margin-bottom: 2rem; animation: slideInUp 1s ease-out; position: relative; }
    .header-title::after { content: ''; position: absolute; bottom: -10px; left: 50%; transform: translateX(-50%); width: 100px; height: 4px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 2px; animation: expandWidth 1.5s ease-out 0.5s both; }
    @keyframes expandWidth { from { width: 0; } to { width: 100px; } }
    .sub-header { color: #2c3e50; font-weight: 700; font-size: 1.8rem; margin: 2rem 0 1rem 0; position: relative; animation: slideInLeft 0.8s ease-out; }
    .sub-header::before { content: ''; position: absolute; left: 0; bottom: -5px; width: 50px; height: 3px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 2px; animation: expandWidth 1s ease-out 0.3s both; }
    [data-baseweb="input"] input, [data-baseweb="input"] div > input { border-radius: 15px !important; border: 2px solid #667eea !important; background: linear-gradient(45deg, #5a67d8 0%, #6b46c1 100%) !important; padding: 0.7rem !important; color: #ffffff !important; transition: all 0.3s ease !important; position: relative; z-index: 1; }
    [data-baseweb="select"] div[role="button"], [data-baseweb="select"] div > div { border-radius: 15px !important; border: 2px solid #667eea !important; background: linear-gradient(45deg, #6b7280 0%, #7c3aed 100%) !important; padding: 0.8rem 1.5rem !important; color: #ffffff !important; font-size: 0.9rem !important; font-weight: 500 !important; transition: all 0.3s ease !important; position: relative; z-index: 1; line-height: 1.5 !important; width: 100% !important; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    [data-baseweb="input"] div, [data-baseweb="select"] div { position: relative; overflow: hidden; border-radius: 15px !important; }
    [data-baseweb="input"] div::before, [data-baseweb="select"] div::before { content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: linear-gradient(45deg, transparent 40%, rgba(255, 255, 255, 0.2) 50%, transparent 60%); animation: rotate 8s linear infinite; z-index: -1; }
    [data-baseweb="input"] input:focus, [data-baseweb="input"] div > input:focus { border-color: #8b5cf6 !important; box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.4) !important; transform: scale(1.02) !important; background: linear-gradient(45deg, #6b7280 0%, #7c3aed 100%) !important; }
    [data-baseweb="select"] div[role="button"]:focus, [data-baseweb="select"] div > div:focus { border-color: #8b5cf6 !important; box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.4) !important; transform: scale(1.02) !important; background: linear-gradient(45deg, #6b7280 0%, #7c3aed 100%) !important; }
    [data-baseweb="select"] div[role="listbox"] { background: #4c1d95 !important; border-radius: 8px !important; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4) !important; max-height: 200px !important; overflow-y: auto !important; z-index: 1000 !important; }
    [data-baseweb="select"] div[role="option"] { color: #ffffff !important; background: transparent !important; padding: 0.8rem 1rem !important; transition: background 0.2s ease !important; cursor: pointer !important; }
    [data-baseweb="select"] div[role="option"]:hover { background: linear-gradient(45deg, #667eea 0%, #764ba2 100%) !important; }
    [data-baseweb="select"] div[aria-selected="true"] { background: #6b46c1 !important; color: #ffffff !important; position: relative !important; }
    [data-baseweb="select"] div[aria-selected="true"]::before { content: '✓'; position: absolute; left: 0.5rem; color: #ffffff; font-weight: 700; }
    [data-baseweb="select"] div[role="listbox"]::-webkit-scrollbar { width: 6px; }
    [data-baseweb="select"] div[role="listbox"]::-webkit-scrollbar-track { background: rgba(255, 255, 255, 0.1); border-radius: 3px; }
    [data-baseweb="select"] div[role="listbox"]::-webkit-scrollbar-thumb { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 3px; }
    [data-baseweb="select"] div[role="listbox"]::-webkit-scrollbar-thumb:hover { background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%); }
    @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    .login-container { max-width: 450px; margin: 10vh auto; padding: 3rem; background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 25px; box-shadow: 0 30px 80px rgba(0, 0, 0, 0.15); border: 1px solid rgba(255, 255, 255, 0.3); animation: fadeInScale 1s ease-out; position: relative; overflow: hidden; }
    .login-container::before { content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: linear-gradient(45deg, transparent 30%, rgba(102, 126, 234, 0.1) 50%, transparent 70%); animation: rotate 10s linear infinite; z-index: -1; }
    .dataframe { border-radius: 20px !important; overflow: hidden !important; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1) !important; border: 1px solid rgba(255, 255, 255, 0.3) !important; backdrop-filter: blur(10px) !important; animation: slideInUp 0.8s ease-out !important; }
    .stExpander { border-radius: 20px !important; border: 1px solid rgba(102, 126, 234, 0.2) !important; box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08) !important; backdrop-filter: blur(10px) !important; background: rgba(0, 0, 0, 0.7) !important; animation: slideInUp 0.6s ease-out !important; overflow: hidden !important; position: relative; }
    .stExpander::before { content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: linear-gradient(45deg, transparent 40%, rgba(255, 255, 255, 0.1) 50%, transparent 60%); animation: rotate 8s linear infinite; z-index: -1; }
    .stExpander:hover { transform: translateY(-2px); box-shadow: 0 12px 35px rgba(0, 0, 0, 0.12) !important; }
    .positive-amount { color: #27ae60; font-weight: 700; animation: pulse 2s infinite; }
    .negative-amount { color: #e74c3c; font-weight: 700; animation: pulse 2s infinite; }
    .loading-animation { display: inline-block; width: 20px; height: 20px; border: 3px solid rgba(102, 126, 234, 0.3); border-radius: 50%; border-top-color: #667eea; animation: spin 1s ease-in-out infinite; }
    @keyframes spin { to { transform: rotate(360deg); } }
    .success-message { background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); border: 1px solid #b8daff; border-radius: 15px; padding: 1rem; margin: 1rem 0; color: #155724; animation: slideInUp 0.5s ease-out; box-shadow: 0 5px 15px rgba(40, 167, 69, 0.2); }
    .error-message { background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%); border: 1px solid #f5c6cb; border-radius: 15px; padding: 1rem; margin: 1rem 0; color: #721c24; animation: slideInUp 0.5s ease-out; box-shadow: 0 5px 15px rgba(220, 53, 69, 0.2); }
    .sidebar { background: rgba(255, 255, 255, 0.95) !important; backdrop-filter: blur(20px) !important; border-radius: 0 20px 20px 0 !important; animation: slideInLeft 0.8s ease-out !important; }
    .glow-effect { box-shadow: 0 0 20px rgba(102, 126, 234, 0.3); animation: glow 2s ease-in-out infinite alternate; }
    .chart-container { background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(20px); border-radius: 20px; padding: 1.5rem; margin: 1.5rem 0; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); border: 1px solid rgba(255, 255, 255, 0.3); animation: fadeInScale 0.8s ease-out; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin: 2rem 0; }
    .progress-bar { width: 100%; height: 8px; background: rgba(102, 126, 234, 0.2); border-radius: 4px; overflow: hidden; margin: 1rem 0; }
    .progress-fill { height: 100%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 4px; animation: progressAnimation 2s ease-out; }
    @keyframes progressAnimation { from { width: 0%; } to { width: var(--progress-width); } }
    .notification { position: fixed; top: 20px; right: 20px; background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 15px; padding: 1rem 1.5rem; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15); border: 1px solid rgba(255, 255, 255, 0.3); animation: slideInRight 0.5s ease-out; z-index: 1000; }
    .icon-bounce { animation: bounce 1s ease-in-out infinite; }
    @keyframes bounce { 0%, 20%, 50%, 80%, 100% { transform: translateY(0); } 40% { transform: translateY(-10px); } 60% { transform: translateY(-5px); } }
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: rgba(255, 255, 255, 0.1); border-radius: 4px; }
    ::-webkit-scrollbar-thumb { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%); }
</style>
""", unsafe_allow_html=True)

# --- Constants ---
PIN_CODE = "Nusrat1221"
JOBS = ["Polish Wala", "Driver", "Employee", "Other", "Wood Factory", "Wood Material", "Hardware Material", "Sheesha", "Ghar Kharacha", "Polish Material", "Kushion wala", "Sofa Factory", "Kapra"]
TABLE_NAME = "transactions"

# --- Supabase Setup ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# --- Initialize Supabase Client ---
@st.cache_resource
def init_supabase():
    try:
        if not SUPABASE_URL or not SUPABASE_KEY:
            st.error("Supabase credentials not found. Please configure secrets.toml.")
            return None
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Error connecting to Supabase: {e}")
        return None

# --- Loading Animation ---
def show_loading():
    loading_html = """
    <div style="display: flex; justify-content: center; align-items: center; height: 100px;">
        <div class="loading-animation"></div>
        <span style="margin-left: 1rem; color: #667eea; font-weight: 600;">Loading...</span>
    </div>
    """
    return st.markdown(loading_html, unsafe_allow_html=True)

# --- Load Data ---
@st.cache_data
def load_data():
    try:
        supabase = init_supabase()
        if not supabase:
            st.error("Failed to initialize Supabase client.")
            return pd.DataFrame(columns=["date", "id", "name", "job", "reason", "amount", "type"])
        response = supabase.table(TABLE_NAME).select("*").execute()
        df = pd.DataFrame(response.data)
        if df.empty:
            st.warning("No data returned from Supabase.")
            return pd.DataFrame(columns=["date", "id", "name", "job", "reason", "amount", "type"])
        df['date'] = pd.to_datetime(df['date'], errors='coerce', utc=True)
        if df['date'].isna().any():
            st.warning("Some dates could not be parsed. Check the 'date' column format in Supabase.")
            df = df.dropna(subset=['date'])
        df['date'] = df['date'].dt.tz_convert('Asia/Karachi')
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(columns=["date", "id", "name", "job", "reason", "amount", "type"])

# --- Normalize Job Values in Supabase ---
def normalize_jobs():
    try:
        supabase = init_supabase()
        if not supabase:
            return
        response = supabase.table(TABLE_NAME).select("*").execute()
        df = pd.DataFrame(response.data)
        for _, row in df.iterrows():
            if row['job'] not in JOBS:
                new_job = next((j for j in JOBS if j.lower() == row['job'].lower()), "Other")
                supabase.table(TABLE_NAME).update({"job": new_job}).eq("id", row["id"]).execute()
        st.cache_data.clear()
        st.success("Job values normalized in Supabase.")
    except Exception as e:
        st.error(f"Error normalizing jobs: {e}")

# --- Save Data to Supabase ---
def save_data_to_supabase(data, operation="insert", index=None):
    try:
        supabase = init_supabase()
        if not supabase:
            return False
        data['date'] = pd.Timestamp(data['date']).tz_convert('UTC').isoformat()
        if operation == "insert":
            response = supabase.table(TABLE_NAME).insert(data).execute()
        elif operation == "update" and index is not None:
            response = supabase.table(TABLE_NAME).update(data).eq("id", data["id"]).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error saving to Supabase: {e}")
        return False

# --- Generate or Get ID ---
def get_or_create_id(df, name):
    person = df[df['name'].str.lower() == name.lower()]
    if not person.empty:
        return person.iloc[0]['id']
    return str(uuid.uuid4())[:8]

# --- Add Transaction with Validation ---
def add_transaction(date, id_, name, job, reason, amount, type_):
    if job not in JOBS:
        st.error(f"Invalid job: {job}. Please select a valid job from {JOBS}.")
        return False
    data = {
        "date": date,
        "id": id_,
        "name": name,
        "job": job,
        "reason": reason,
        "amount": float(amount),
        "type": type_
    }
    return save_data_to_supabase(data, operation="insert")

# --- Edit Transaction with Validation ---
def edit_transaction(index, date, name, job, reason, amount, type_):
    if job not in JOBS:
        st.error(f"Invalid job: {job}. Please select a valid job from {JOBS}.")
        return False
    df = load_data()
    id_ = df.loc[index, 'id']
    data = {
        "date": date,
        "id": id_,
        "name": name,
        "job": job,
        "reason": reason,
        "amount": float(amount),
        "type": type_
    }
    return save_data_to_supabase(data, operation="update", index=index)

# --- Filter Data ---
def filter_data(df, name=None, id_=None, job=None, date_range=None):
    filtered_df = df.copy()
    if name:
        filtered_df = filtered_df[filtered_df['name'].str.contains(name, case=False, na=False)]
    if id_:
        filtered_df = filtered_df[filtered_df['id'].str.contains(id_, case=False, na=False)]
    if job and job != "All":
        filtered_df = filtered_df[filtered_df['job'] == job]
    if date_range:
        start_date, end_date = date_range
        start_date = pd.Timestamp(start_date, tz='Asia/Karachi')
        end_date = pd.Timestamp(end_date, tz='Asia/Karachi') + timedelta(days=1) - timedelta(seconds=1)
        filtered_df = filtered_df[(filtered_df['date'] >= start_date) & (filtered_df['date'] <= end_date)]
    return filtered_df

# --- Metric Card ---
def create_metric_card(title, value, card_type="neutral"):
    card_classes = {"success": "success-card", "danger": "danger-card", "neutral": "neutral-card"}
    card_class = card_classes.get(card_type, "neutral-card")
    html = f"""
    <div class="metric-card {card_class}">
        <h3 style="margin: 0; font-size: 1.2rem; font-weight: 500;">{title}</h3>
        <h2 style="margin: 0.5rem 0; font-size: 2rem; font-weight: 700;">Rs. {int(value)}</h2>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- Generate PDF Report ---
def generate_pdf_report(filtered_df, start_date, end_date):
    try:
        temp_dir = tempfile.mkdtemp()
        total_in = filtered_df[filtered_df['type'] == 'In']['amount'].sum()
        total_out = filtered_df[filtered_df['type'] == 'Out']['amount'].sum()
        net_balance = total_in - total_out
        report_df = filtered_df.copy()
        report_df['date'] = report_df['date'].dt.strftime('%Y-%m-%d')
        report_df['amount'] = report_df['amount'].apply(lambda x: f"Rs. {int(x)}")
        # Split into incoming and outgoing
        incoming_df = report_df[report_df['type'] == 'In'][['date', 'name', 'job', 'reason', 'amount', 'type']]
        outgoing_df = report_df[report_df['type'] == 'Out'][['date', 'name', 'job', 'reason', 'amount', 'type']]
        pdf_path = os.path.join(temp_dir, "transaction_report.pdf")
        doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
        elements = []
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], fontSize=24, leading=28, textColor=colors.HexColor('#2c3e50'), alignment=1, spaceAfter=12)
        subtitle_style = ParagraphStyle('SubtitleStyle', parent=styles['Normal'], fontSize=14, leading=16, textColor=colors.HexColor('#667eea'), alignment=1, spaceAfter=8)
        heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], fontSize=16, leading=20, textColor=colors.HexColor('#2c3e50'), spaceBefore=12, spaceAfter=8)
        elements.append(Paragraph("Nusrat Furniture Transaction Report", title_style))
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(Paragraph(f"Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}", subtitle_style))
        elements.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d')}", subtitle_style))
        elements.append(Paragraph("Enterprise Transaction Management System", subtitle_style))
        elements.append(Spacer(1, 1 * inch))
        elements.append(Paragraph("Transaction Summary", heading_style))
        summary_data = [
            ["Total Incoming:", f"Rs. {int(total_in)}", ""],
            ["Total Outgoing:", f"Rs. {int(total_out)}", ""],
            ["Net Balance:", f"Rs. {int(abs(net_balance))}", "Positive" if net_balance >= 0 else "Negative"]
        ]
        summary_table = Table(summary_data, colWidths=[2 * inch, 2 * inch, 2 * inch])
        summary_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica'), ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor('#27ae60')), ('TEXTCOLOR', (1, 1), (1, 1), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (1, 2), (1, 2), colors.HexColor('#27ae60' if net_balance >= 0 else '#e74c3c')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6), ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.5 * inch))
        # Incoming Transactions Table
        if not incoming_df.empty:
            elements.append(Paragraph("Incoming Transactions", heading_style))
            table_data = [["Date", "Name", "Job", "Reason", "Amount", "Type"]]
            for _, row in incoming_df.iterrows():
                table_data.append([row['date'], row['name'], row['job'], row['reason'], row['amount'], row['type']])
            incoming_table = Table(table_data, colWidths=[1.2 * inch, 1.5 * inch, 1.2 * inch, 2.2 * inch, 1.2 * inch, 0.9 * inch])
            incoming_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONT', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10), ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black), ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6), ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d4edda')),
                ('TEXTCOLOR', (5, 1), (5, -1), colors.HexColor('#27ae60'))
            ]))
            elements.append(incoming_table)
            elements.append(Spacer(1, 0.5 * inch))
        # Outgoing Transactions Table
        if not outgoing_df.empty:
            elements.append(Paragraph("Outgoing Transactions", heading_style))
            table_data = [["Date", "Name", "Job", "Reason", "Amount", "Type"]]
            for _, row in outgoing_df.iterrows():
                table_data.append([row['date'], row['name'], row['job'], row['reason'], row['amount'], row['type']])
            outgoing_table = Table(table_data, colWidths=[1.2 * inch, 1.5 * inch, 1.2 * inch, 2.2 * inch, 1.2 * inch, 0.9 * inch])
            outgoing_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONT', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10), ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black), ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6), ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8d7da')),
                ('TEXTCOLOR', (5, 1), (5, -1), colors.HexColor('#e74c3c'))
            ]))
            elements.append(outgoing_table)
            elements.append(Spacer(1, 0.5 * inch))
        doc.build(elements)
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                pdf_data = f.read()
            shutil.rmtree(temp_dir, ignore_errors=True)
            return pdf_data
        else:
            st.error("PDF file was not generated.")
            return None
    except Exception as e:
        st.error(f"Error generating PDF report: {e}")
        return None

# --- Login UI ---
def login_ui():
    st.markdown("""
    <div class="login-container glow-effect">
        <div style="text-align: center; margin-bottom: 2.5rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;" class="icon-bounce">🏢</div>
            <h1 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.8rem; margin-bottom: 0.5rem; font-weight: 800;">Nusrat Furniture</h1>
            <p style="color: #6c757d; margin-top: 0.5rem; font-size: 1.1rem; font-weight: 500;">Enterprise Transaction Management System</p>
            <div class="progress-bar"><div class="progress-fill" style="--progress-width: 100%; width: 100%;"></div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    pin = st.text_input("🔐 Enter PIN", type="password", placeholder="Enter your secure PIN")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Login", use_container_width=True):
            if pin == PIN_CODE:
                st.session_state["authenticated"] = True
                st.success("✅ Login successful!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("❌ Invalid PIN! Please try again.")

# --- Cache Plotly Figures ---
@st.cache_data
def create_pie_chart(type_summary):
    fig = px.pie(type_summary, values='amount', names='type', title="💰 Transaction Distribution", color_discrete_map={'In': '#27ae60', 'Out': '#e74c3c'}, hole=0.4)
    fig.update_layout(font=dict(family="Poppins, sans-serif", size=12), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', title_font_size=16, title_font_color='#2c3e50', showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
    fig.update_traces(textposition='inside', textinfo='percent+label', hovertemplate='<b>%{label}</b><br>Amount: Rs. %{value:,.2f}<br>Percentage: %{percent}<extra></extra>')
    return fig

@st.cache_data
def create_bar_chart(pivot_df):
    fig = px.bar(pivot_df, x='name', y=['In', 'Out'], title="👥 Person-wise Transaction Summary", barmode='group', color_discrete_map={'In': '#27ae60', 'Out': '#e74c3c'})
    fig.update_layout(font=dict(family="Poppins, sans-serif", size=12), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis_title="Person", yaxis_title="Amount (Rs.)", xaxis=dict(tickangle=45), showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5))
    fig.update_traces(hovertemplate='<b>%{x}</b><br>%{fullData.name}: Rs. %{y:,.2f}<extra></extra>')
    return fig

@st.cache_data
def create_line_chart(daily_summary):
    fig = px.line(daily_summary, x='date', y='amount', color='type', title="📈 Transaction Trends Over Time", color_discrete_map={'In': '#27ae60', 'Out': '#e74c3c'}, markers=True)
    fig.update_layout(font=dict(family="Poppins, sans-serif", size=12), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis_title="Date", yaxis_title="Amount (Rs.)", title_font_size=16, title_font_color='#2c3e50', hovermode='x unified')
    fig.update_traces(line=dict(width=3), marker=dict(size=8), hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Amount: Rs. %{y:,.2f}<extra></extra>')
    return fig

@st.cache_data
def create_job_bar_chart(job_summary):
    fig = px.bar(job_summary, x='month', y=['In', 'Out'], color='job', title="💼 Job-wise Transactions by Month", barmode='stack', color_discrete_map={'Polish Wala': '#667eea', 'Driver': '#764ba2', 'Employee': '#6b46c1', 'Other': '#8b5cf6'})
    fig.update_layout(font=dict(family="Poppins, sans-serif", size=12), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis_title="Month", yaxis_title="Amount (Rs.)", xaxis=dict(tickangle=45), showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5), title_font_size=16, title_font_color='#2c3e50', bargap=0.2)
    fig.update_traces(hovertemplate='<b>%{fullData.name}</b><br>Month: %{x}<br>Amount: Rs. %{y:,.2f}<extra></extra>')
    return fig

# --- Main App UI ---
def app_ui():
    if "expand_transaction" not in st.session_state:
        st.session_state["expand_transaction"] = False
    if "expand_edit_transaction" not in st.session_state:
        st.session_state["expand_edit_transaction"] = False

    st.markdown("""
    <div class="header-title">
        <span class="icon-bounce" style="font-size: 1em;">📊</span>
        Nusrat Furniture Transaction Manager
    </div>
    """, unsafe_allow_html=True)

    df = load_data()
    #st.write("Unique jobs in DataFrame:", df['job'].unique().tolist())

    st.markdown("""
    <div class="floating-plus">
        <span>+</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("➕ Add Transaction", key="floating_plus_button"):
        st.session_state["expand_transaction"] = True

    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; margin-bottom: 2rem;">
            <div style="font-size: 3rem;" class="icon-bounce">🔍</div>
            <h2 style="color: #2c3e50; font-weight: 700; margin: 0.5rem 0;">Search & Filter</h2>
        </div>
        """, unsafe_allow_html=True)
        search_name = st.text_input("👤 Search by Name", placeholder="Enter person's name...", key="search_name")
        search_id = st.text_input("🆔 Search by ID", placeholder="Enter ID...", key="search_id")
        search_job = st.selectbox("💼 Filter by Job", ["All"] + JOBS, key="search_job")
        st.markdown("📅 **Date Range**")
        use_date_filter = st.checkbox("Apply Date Range Filter", value=False)
        col1, col2 = st.columns(2)
        with col1:
            default_start_date = datetime(2025, 1, 1) if df.empty else df['date'].min().date()
            start_date = st.date_input("From", value=default_start_date, key="start_date")
        with col2:
            end_date = st.date_input("To", value=datetime.today(), key="end_date")
        date_range = (start_date, end_date) if use_date_filter else None
        filtered_df = filter_data(df, search_name if search_name else None, search_id if search_id else None, search_job if search_job != "All" else None, date_range)
        if not filtered_df.empty:
            st.markdown("---")
            st.markdown("### 📈 Quick Stats")
            total_transactions = len(filtered_df)
            unique_people = filtered_df['name'].nunique()
            avg_transaction = filtered_df['amount'].mean()
            st.markdown(f"""
            <div class="metric-card success-card" style="margin: 0.5rem 0; padding: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div><h4 style="margin: 0; opacity: 0.8;">Transactions</h4><h3 style="margin: 0; font-weight: 700;">{total_transactions}</h3></div>
                    <div style="font-size: 1.5rem;">📝</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="metric-card neutral-card" style="margin: 0.5rem 0; padding: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div><h4 style="margin: 0; opacity: 0.8;">Unique People</h4><h3 style="margin: 0; font-weight: 700;">{unique_people}</h3></div>
                    <div style="font-size: 1.5rem;">👥</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="metric-card danger-card" style="margin: 0.5rem 0; padding: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div><h4 style="margin: 0; opacity: 0.8;">Avg Amount</h4><h3 style="margin: 0; font-weight: 700;">Rs. {int(avg_transaction)}</h3></div>
                    <div style="font-size: 1.5rem;">📊</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with st.expander("➕ Add New Transaction", expanded=st.session_state.expand_transaction):
        st.session_state.expand_transaction = False
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 3rem;" class="icon-bounce">📝</div>
            <h3 style="color: #ffffff; font-weight: 700;">Transaction Details</h3>
        </div>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input("👤 Person's Name*", placeholder="Enter full name", key="form_name")
            job = st.selectbox("💼 Job Role*", JOBS, key="form_job")
        with col2:
            reason = st.text_input("📄 Reason*", placeholder="Purpose of transaction", key="form_reason")
            amount = st.number_input("💰 Amount*", min_value=0.0, step=100.0, key="form_amount")
        with col3:
            type_ = st.selectbox("🔄 Transaction Type*", ["In", "Out"], key="form_type")
            date = st.date_input("📅 Date", value=datetime.today(), key="form_date")
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("💾 Submit Transaction", use_container_width=True, key="submit_btn"):
                if name and reason and amount > 0 and job in JOBS:
                    loading_placeholder = st.empty()
                    loading_placeholder.markdown('<div class="loading-animation" style="margin: 1rem auto;"></div>', unsafe_allow_html=True)
                    time.sleep(0.5)
                    id_ = get_or_create_id(df, name)
                    success = add_transaction(pd.Timestamp(date, tz='Asia/Karachi'), id_, name, job, reason, amount, type_)
                    loading_placeholder.empty()
                    if success:
                        st.markdown(f"""
                        <div class="success-message">
                            <div style="display: flex; align-items: center;">
                                <div style="font-size: 2rem; margin-right: 1rem;">✅</div>
                                <div><h4 style="margin: 0; color: #155724;">Transaction Successful!</h4><p style="margin: 0.5rem 0 0 0; opacity: 0.8;">Added for <strong>{name}</strong> ({type_}: Rs. {int(amount)})</p></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.markdown("""
                        <div class="error-message">
                            <div style="display: flex; align-items: center;">
                                <div style="font-size: 2rem; margin-right: 1rem;">⚠️</div>
                                <div><h4 style="margin: 0;">Error</h4><p style="margin: 0.5rem 0 0 0; opacity: 0.8;">Failed to add transaction. Please try again.</p></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="error-message">
                        <div style="display: flex; align-items: center;">
                            <div style="font-size: 2rem; margin-right: 1rem;">⚠️</div>
                            <div><h4 style="margin: 0;">Validation Error</h4><p style="margin: 0.5rem 0 0 0; opacity: 0.8;">Please fill all required fields marked with * and ensure a valid job is selected.</p></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    with st.expander("✏️ Edit Transaction", expanded=st.session_state.expand_edit_transaction):
        st.session_state.expand_edit_transaction = False
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 3rem;" class="icon-bounce">✏️</div>
            <h3 style="color: #ffffff; font-weight: 700;">Edit Transaction Details</h3>
        </div>
        """, unsafe_allow_html=True)
        if not df.empty:
            transaction_index = st.selectbox(
                "Select Transaction to Edit",
                options=range(len(df)),
                format_func=lambda x: f"{df.iloc[x]['name']} - {df.iloc[x]['reason']} ({df.iloc[x]['date'].strftime('%Y-%m-%d')})"
            )
            if transaction_index is not None:
                selected_transaction = df.iloc[transaction_index]
                col1, col2, col3 = st.columns(3)
                with col1:
                    edit_name = st.text_input("👤 Person's Name*", value=selected_transaction['name'], key="edit_form_name")
                    job_index = JOBS.index(selected_transaction['job']) if selected_transaction['job'] in JOBS else 0
                    edit_job = st.selectbox("💼 Job Role*", JOBS, index=job_index, key="edit_form_job")
                with col2:
                    edit_reason = st.text_input("📄 Reason*", value=selected_transaction['reason'], key="edit_form_reason")
                    edit_amount = st.number_input("💰 Amount*", min_value=0.0, step=100.0, value=float(selected_transaction['amount']), key="edit_form_amount")
                with col3:
                    edit_type = st.selectbox("🔄 Transaction Type*", ["In", "Out"], index=["In", "Out"].index(selected_transaction['type']), key="edit_form_type")
                    edit_date = st.date_input("📅 Date", value=selected_transaction['date'].date(), key="edit_form_date")
                st.markdown("---")
                col1, col2, col3 = st.columns([2, 1, 2])
                with col2:
                    if st.button("💾 Update Transaction", use_container_width=True, key="edit_submit_btn"):
                        if edit_name and edit_reason and edit_amount > 0 and edit_job in JOBS:
                            loading_placeholder = st.empty()
                            loading_placeholder.markdown('<div class="loading-animation" style="margin: 1rem auto;"></div>', unsafe_allow_html=True)
                            time.sleep(0.5)
                            success = edit_transaction(transaction_index, pd.Timestamp(edit_date, tz='Asia/Karachi'), edit_name, edit_job, edit_reason, edit_amount, edit_type)
                            loading_placeholder.empty()
                            if success:
                                st.markdown(f"""
                                <div class="success-message">
                                    <div style="display: flex; align-items: center;">
                                        <div style="font-size: 2rem; margin-right: 1rem;">✅</div>
                                        <div><h4 style="margin: 0; color: #155724;">Transaction Updated!</h4><p style="margin: 0.5rem 0 0 0; opacity: 0.8;">Updated for <strong>{edit_name}</strong> ({edit_type}: Rs. {int(edit_amount)})</p></div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                st.balloons()
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.markdown("""
                                <div class="error-message">
                                    <div style="display: flex; align-items: center;">
                                        <div style="font-size: 2rem; margin-right: 1rem;">⚠️</div>
                                        <div><h4 style="margin: 0;">Error</h4><p style="margin: 0.5rem 0 0 0; opacity: 0.8;">Failed to update transaction. Please try again.</p></div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div class="error-message">
                                <div style="display: flex; align-items: center;">
                                    <div style="font-size: 2rem; margin-right: 1rem;">⚠️</div>
                                    <div><h4 style="margin: 0;">Validation Error</h4><p style="margin: 0.5rem 0 0 0; opacity: 0.8;">Please fill all required fields marked with * and ensure a valid job is selected.</p></div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="error-message">
                <div style="display: flex; align-items: center;">
                    <div style="font-size: 2rem; margin-right: 1rem;">⚠️</div>
                    <div><h4 style="margin: 0;">No Transactions</h4><p style="margin: 0.5rem 0 0 0; opacity: 0.8;">No transactions available to edit.</p></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    if not filtered_df.empty:
        total_in = filtered_df[filtered_df['type'] == 'In']['amount'].sum()
        total_out = filtered_df[filtered_df['type'] == 'Out']['amount'].sum()
        net_balance = total_in - total_out
        st.markdown('<div class="stats-grid">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            create_metric_card("Total Incoming", total_in, "success")
        with col2:
            create_metric_card("Total Outgoing", total_out, "danger")
        with col3:
            card_type = "success" if net_balance >= 0 else "danger"
            create_metric_card("Net Balance", net_balance, card_type)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<h2 class="sub-header">📋 Transaction Records</h2>', unsafe_allow_html=True)
    if filtered_df.empty:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(20px); border-radius: 20px; margin: 2rem 0;">
            <div style="font-size: 5rem; opacity: 0.3;" class="icon-bounce">🔍</div>
            <h3 style="color: #6c757d; margin: 1rem 0;">No transactions found</h3>
            <p style="color: #6c757d; opacity: 0.8;">Try adjusting your search criteria or add a new transaction</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        display_df = filtered_df.copy()
        display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
        display_df['amount'] = display_df['amount'].apply(lambda x: f"Rs. {int(x)}")
        display_df = display_df[['date', 'name', 'job', 'reason', 'amount', 'type', 'id']]
        def style_dataframe(df):
            def color_type(val):
                if val == 'In':
                    return 'background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); color: #155724; font-weight: 600;'
                elif val == 'Out':
                    return 'background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%); color: #721c24; font-weight: 600;'
                return ''
            def highlight_amount(val):
                if 'Rs.' in str(val):
                    return 'font-weight: 700; color: #2c3e50;'
                return ''
            styled = df.style.applymap(color_type, subset=['type']).applymap(highlight_amount, subset=['amount'])
            return styled
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.dataframe(style_dataframe(display_df), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if not filtered_df.empty and len(filtered_df) > 1:
        st.markdown('<h2 class="sub-header">📊 Analytics Dashboard</h2>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            type_summary = filtered_df.groupby('type')['amount'].sum().reset_index()
            fig_pie = create_pie_chart(type_summary)
            st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            pivot_df = filtered_df.pivot_table(index=['name'], columns='type', values='amount', aggfunc='sum', fill_value=0).reset_index()
            if 'In' not in pivot_df.columns:
                pivot_df['In'] = 0
            if 'Out' not in pivot_df.columns:
                pivot_df['Out'] = 0
            fig_bar = create_bar_chart(pivot_df)
            st.plotly_chart(fig_bar, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        if len(filtered_df) > 5:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            daily_summary = filtered_df.groupby([filtered_df['date'].dt.date, 'type'])['amount'].sum().reset_index()
            fig_time = create_line_chart(daily_summary)
            st.plotly_chart(fig_time, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        if len(filtered_df) > 1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            job_summary = filtered_df.copy()
            job_summary['month'] = job_summary['date'].dt.to_period('M').astype(str)
            job_summary = job_summary.pivot_table(index=['month', 'job'], columns='type', values='amount', aggfunc='sum', fill_value=0).reset_index()
            if 'In' not in job_summary.columns:
                job_summary['In'] = 0
            if 'Out' not in job_summary.columns:
                job_summary['Out'] = 0
            fig_job = create_job_bar_chart(job_summary)
            st.plotly_chart(fig_job, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<h2 class="sub-header">💾 Data Export & Management</h2>', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("📥 Download Filtered Data", use_container_width=True, key="download_filtered"):
            if not filtered_df.empty:
                csv = filtered_df.copy()
                csv['date'] = csv['date'].dt.strftime('%Y-%m-%d')
                csv = csv.to_csv(index=False)
                st.download_button(label="⬇️ Download Filtered CSV", data=csv, file_name=f"filtered_transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv", use_container_width=True, key="download_filtered_btn")
            else:
                st.markdown("""
                <div class="error-message">
                    <div style="display: flex; align-items: center;">
                        <div style="font-size: 2rem; margin-right: 1rem;">⚠️</div>
                        <div><h4 style="margin: 0;">No Data</h4><p style="margin: 0.5rem 0 0 0; opacity: 0.8;">No filtered data available to download.</p></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    with col2:
        if st.button("📜 Download PDF Report", use_container_width=True, key="download_pdf"):
            if not filtered_df.empty:
                loading_placeholder = st.empty()
                loading_placeholder.markdown('<div class="loading-animation" style="margin: 1rem auto;"></div>', unsafe_allow_html=True)
                pdf_data = generate_pdf_report(filtered_df, start_date, end_date)
                loading_placeholder.empty()
                if pdf_data:
                    st.download_button(label="⬇️ Download PDF Report", data=pdf_data, file_name=f"transaction_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf", mime="application/pdf", use_container_width=True, key="download_pdf_btn")
                else:
                    st.markdown("""
                    <div class="error-message">
                        <div style="display: flex; align-items: center;">
                            <div style="font-size: 2rem; margin-right: 1rem;">⚠️</div>
                            <div><h4 style="margin: 0;">Error</h4><p style="margin: 0.5rem 0 0 0; opacity: 0.8;">Failed to generate PDF report.</p></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="error-message">
                    <div style="display: flex; align-items: center;">
                        <div style="font-size: 2rem; margin-right: 1rem;">⚠️</div>
                        <div><h4 style="margin: 0;">No Data</h4><p style="margin: 0.5rem 0 0 0; opacity: 0.8;">No filtered data available for PDF report.</p></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    with col3:
        if st.button("📊 Download Full Database", use_container_width=True, key="download_full"):
            csv = df.to_csv(index=False)
            st.download_button(label="⬇️ Download Full CSV", data=csv, file_name=f"all_transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv", use_container_width=True, key="download_full_btn")
    with col4:
        if st.button("🔄 Refresh Data", use_container_width=True, key="refresh"):
            st.cache_data.clear()
            st.success("Data refreshed successfully!")
            time.sleep(1)
            st.rerun()
    with col5:
        if st.button("🚪 Logout", use_container_width=True, key="logout"):
            st.session_state["authenticated"] = False
            st.success("Logged out successfully!")
            time.sleep(1)
            st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(20px); border-radius: 20px; margin: 2rem 0;">
        <div style="font-size: 2rem; margin-bottom: 1rem;" class="icon-bounce">🏢</div>
        <h3 style="color: #2c3e50; margin: 0.5rem 0; font-weight: 700;">Nusrat Furniture Transaction Manager</h3>
        <p style="color: #6c757d; margin: 0; font-weight: 500;">Enterprise-grade transaction management system</p>
        <div style="margin-top: 1rem; font-size: 0.9rem; color: #6c757d;">Made with ❤️ using Streamlit | Version 3.4 | Ultra Modern UI</div>
    </div>
    """, unsafe_allow_html=True)

# --- App Entry Point ---
def main():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        login_ui()
    else:
        normalize_jobs()  # Run once to clean up job values
        app_ui()

if __name__ == "__main__":
    main()
