import pandas as pd
import os
import uuid

DATA_PATH = "data/transactions.csv"
APP_PIN = "Nusrat1221"

def authenticate(pin):
    return pin == APP_PIN

def load_data():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.isfile(DATA_PATH):
        return pd.DataFrame(columns=["date", "id", "name", "job", "reason", "amount", "type"])
    return pd.read_csv(DATA_PATH, parse_dates=["date"])

def save_data(df):
    df.to_csv(DATA_PATH, index=False)

def generate_unique_id(df):
    while True:
        uid = str(uuid.uuid4())[:8]
        if uid not in df["id"].values:
            return uid

def get_summary_by_person(df):
    in_df = df[df["type"] == "In"].groupby("name")["amount"].sum().reset_index(name="In")
    out_df = df[df["type"] == "Out"].groupby("name")["amount"].sum().reset_index(name="Out")
    summary = pd.merge(in_df, out_df, on="name", how="outer").fillna(0)
    return summary

def filter_data(df, name="", person_id="", job="", tx_date=None):
    result = df.copy()
    if name:
        result = result[result["name"].str.contains(name, case=False, na=False)]
    if person_id:
        result = result[result["id"].str.contains(person_id, case=False, na=False)]
    if job:
        result = result[result["job"].str.contains(job, case=False, na=False)]
    if tx_date:
        result = result[result["date"] == pd.to_datetime(tx_date)]
    return result
