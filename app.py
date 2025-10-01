import streamlit as st
import pandas as pd

st.title("Proxy Email Generator")

# --- Load data from CSV ---
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    # Clean up headers by removing trailing colons
    df = df.rename(columns=lambda x: x.strip().rstrip(":"))
    return df

df = load_data()

# --- Dropdown for Issuer ---
issuer = st.selectbox("Select Issuer", sorted(df["Issuer"].unique()))
record = df[df["Issuer"] == issuer].iloc[0]

# --- Format dates ---
def fmt_date(val):
    try:
        return pd.to_datetime(val).strftime("%B %d, %Y")
    except Exception:
        return val  # fallback if it's not a date

record_date = fmt_date(record["Record Date"])
meeting_date = fmt_date(record["Meeting Date"])

# --- Build the email ---
email_body = f"""
Good afternoon,

I hope this email finds you well and thank you for your attention.

Sodali is working on the proxy below:

Invesco recommends you vote in Favor of the proposal.

Fund Name: {record['Fund Name']}
Record Date: {record_date}
Meeting Date: {meeting_date}
Cusip: {record['CUSIP']}
Broadridge Job Number: {record['Broadridge Job Number']}
Issuer: {record['Issuer']}
Broadridge Client Number: {record['Broadridge Client Number']}
Total Shares Held: {record['Total Shares Held via Broadridge Reports']}
Proxy Edge Accounts: {record['Number of Proxy Edge Accounts']}
Special Processing Accounts: {record['Number of Special Processing Accounts']}
"""

st.text_area("Generated Email", email_body, height=300)
st.download_button("Download Email", email_body, file_name="template_email.txt")

# --- Optional: show table for debugging ---
with st.expander("Preview data"):
    st.dataframe(df)
