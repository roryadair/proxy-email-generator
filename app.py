import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
from docx.shared import Pt

st.title("Proxy Email Generator")

# --- Load fund/job data from CSV ---
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    # Clean up headers by removing trailing colons
    df = df.rename(columns=lambda x: x.strip().rstrip(":"))
    return df

# --- Load addresses from CSV (exported from 'Addresses of Bandb' tab) ---
@st.cache_data
def load_addresses():
    addresses = pd.read_csv("addresses.csv")
    addresses = addresses.rename(columns=lambda x: x.strip())
    return addresses

df = load_data()
addresses = load_addresses()

# --- Dropdown for Issuer ---
issuer = st.selectbox("Select Issuer", sorted(df["Issuer"].unique()))
record = df[df["Issuer"] == issuer].iloc[0]

# --- Format dates ---
def fmt_date(val):
    try:
        return pd.to_datetime(val).strftime("%B %d, %Y")
    except Exception:
        return val

record_date = fmt_date(record["Record Date"])
meeting_date = fmt_date(record["Meeting Date"])

# --- Editable Form ---
st.subheader("Additional Voting Details")

proxy_edge_shares = st.text_input("Number of Proxy Edge Shares Voting:", "")
special_proc_shares = st.text_input("Number of Special Processing Shares Voting:", "")
expected_date = st.text_input("Expected Date or Timeframe for Voting PE and SP Shares:", "")
recommendation = st.selectbox(
    "Following ISS, Glass Lewis or Egan Jones recommendations:",
    ["", "ISS", "Glass Lewis", "Egan Jones", "Other"]
)

# Instruction note
st.markdown(
    "<span style='color:#b58900'><b>Please fill in Number of Shares Voting for Each Yellow Bucket and Timing</b></span>",
    unsafe_allow_html=True
)

# --- Build the email body ---
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

--- Additional Voting Details ---
Number of Proxy Edge Shares Voting: {proxy_edge_shares}
Number of Special Processing Shares Voting: {special_proc_shares}
Expected Date or Timeframe for Voting PE and SP Shares: {expected_date}
Following ISS, Glass Lewis or Egan Jones recommendations: {recommendation}
"""

# --- Styled Preview ---
st.markdown(
    f"""
    <div style="background-color:#f9f9f9;padding:15px;border-radius:10px;border:1px solid #ddd;">
    <pre style="font-family:Arial;font-size:14px;white-space:pre-wrap;">{email_body}</pre>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Copy to Clipboard ---
st.code(email_body, language="text")

# --- Build Word doc ---
def build_doc(email_text):
    doc = Document()
    for line in email_text.strip().split("\n"):
        p = doc.add_paragraph(line)
        p.style.font.size = Pt(11)
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

doc_file = build_doc(email_body)

# --- Download as Word button ---
st.download_button(
    label="📄 Download as Word",
    data=doc_file,
    file_name="proxy_email.docx",
    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)

# --- Outlook integration ---
recipient_row = addresses[addresses["Institution"] == issuer]
recipient_email = recipient_row["Email"].iloc[0] if not recipient_row.empty else ""

if recipient_email:
    subject = f"Proxy Vote Request - {issuer}"
    mailto_link = f"mailto:{recipient_email}?subject={subject}&body={email_body.replace(chr(10), '%0A')}"
    st.markdown(f"[📧 Send Email in Outlook]({mailto_link})", unsafe_allow_html=True)
else:
    st.warning("No email address found for this Issuer in addresses.csv.")

# --- Optional: preview raw data ---
with st.expander("Preview fund/job data"):
    st.dataframe(df)

with st.expander("Preview Issuer addresses"):
    st.dataframe(addresses)
