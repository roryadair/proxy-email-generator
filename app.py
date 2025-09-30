import streamlit as st
import pandas as pd
import sqlalchemy

# --- Connect to DB2 ---
db_conf = st.secrets["db2"]

conn_str = (
    f"db2+ibm_db://{db_conf['user']}:{db_conf['password']}"
    f"@{db_conf['host']}:{db_conf['port']}/{db_conf['database']}"
)
engine = sqlalchemy.create_engine(conn_str)

# --- Your SQL query ---
QUERY = """
SELECT
    CLIENTNAME AS "Fund Name",
    CAST(
        SUBSTR(DIGITS(RECDATE),1,4) || '-' ||
        SUBSTR(DIGITS(RECDATE),5,2) || '-' ||
        SUBSTR(DIGITS(RECDATE),7,2)
    AS DATE) AS "Record Date",
    CAST(
        SUBSTR(DIGITS(MEETDATE),1,4) || '-' ||
        SUBSTR(DIGITS(MEETDATE),5,2) || '-' ||
        SUBSTR(DIGITS(MEETDATE),7,2)
    AS DATE) AS "Meeting Date",
    CUSIP,
    RTRIM(ICSJOB) || ', ' || RTRIM(MCNUMBER) AS "Broadridge Job Number",
    BROKERNAME AS "Issuer",
    BROKERID AS "Broadridge Client Number",
    SHARES AS "Total Shares Held via Broadridge Reports",
    PROXYEDGE AS "Number of Proxy Edge Accounts",
    SPECIALPRO AS "Number of Special Processing Accounts"
FROM ICS.IPMSCRAPEN
"""

@st.cache_data
def load_data():
    return pd.read_sql(QUERY, engine)

# --- App UI ---
st.title("Proxy Email Generator")

df = load_data()

# Dropdown for Issuer
issuer = st.selectbox("Select Issuer", sorted(df["Issuer"].unique()))
record = df[df["Issuer"] == issuer].iloc[0]

# Email template
email_body = f"""
Good afternoon,

I hope this email finds you well and thank you for your attention.

Sodali is working on the proxy below:

Invesco recommends you vote in Favor of the proposal.

Fund Name: {record['Fund Name']}
Record Date: {record['Record Date']}
Meeting Date: {record['Meeting Date']}
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
