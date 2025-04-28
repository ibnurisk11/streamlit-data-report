import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import re
# Load data from CSV
@st.cache_data(ttl=3600)
def load_data():
        df = pd.read_csv("dataset/personal-loan.csv")
        df["tanggal_pencairan"] = pd.to_datetime(df["tanggal_pencairan"], errors='coerce')
        return df

df = load_data()

# Filter
allowed_companies = [
    "PT. Kaldu Sari Nabati", "PT. Pinus Merah Abadi", "PT. Richeese Kuliner Indonesia",
    "PT. Kieber Propertindo", "PT. Enerlife Indonesia", "PT. Satustop Finansial Solusi (Sanders)",
    "PT. Nutribev Nabati Indonesia", "PT. Nutribev Synergi Indonesia"
]
allowed_marketers = [
    "Darsono", "Aditya Haryono", "Milda Noviyana", "Rizki Sitti Rachmawati",
    "Mentari Kusmana Dewi", "Mentari Kusmana Dewi", "Risma Julianti", "Ajeng Nurul Siti Fatimah", "Fahira Rahmi Nur Awaliah"
]

df = df[df["borrower_name_company"].isin(allowed_companies)]
df = df[(df["marketing_name"].isin(allowed_marketers)) | (df["marketing_name"].isna())]

# Sidebar filters
st.sidebar.header("Filter Data")

company_options = ["Semua Perusahaan"] + sorted(df["borrower_name_company"].dropna().unique())
selected_company = st.sidebar.selectbox("Pilih Perusahaan", company_options)

marketing_options = ["Semua Marketing"] + sorted(df["marketing_name"].dropna().unique())
selected_marketing = st.sidebar.selectbox("Pilih Marketing", marketing_options)

status_options = ["Semua Status"] + sorted(df["loan_status"].dropna().unique())
selected_status = st.sidebar.selectbox("Pilih Status", status_options)

tenor_options = ["Semua Tenor"] + sorted(df["tenor"].dropna().unique())
selected_tenor = st.sidebar.selectbox("Pilih Tenor", tenor_options)

min_date, max_date = df["tanggal_pencairan"].min(), df["tanggal_pencairan"].max()
selected_dates = st.sidebar.date_input("Rentang Tanggal", [min_date, max_date])

# Filter function
@st.cache_data
def filter_data(df, selected_company, selected_marketing, selected_status, selected_tenor, selected_dates):
    return df[
        ((df["borrower_name_company"] == selected_company) | (selected_company == "Semua Perusahaan")) &
        ((df["marketing_name"] == selected_marketing) | (selected_marketing == "Semua Marketing")) &
        ((df["loan_status"] == selected_status) | (selected_status == "Semua Status")) &
        ((df["tenor"] == selected_tenor) | (selected_tenor == "Semua Tenor")) &
        (df["tanggal_pencairan"] >= pd.to_datetime(selected_dates[0])) &
        (df["tanggal_pencairan"] <= pd.to_datetime(selected_dates[1]))
    ]

filtered_df = filter_data(df, selected_company, selected_marketing, selected_status, selected_tenor, selected_dates)

# Metrics
st.title("📊 Dashboard Personal Loan")

total_loan_amount = float(filtered_df["nominal_pinjaman"].sum())
total_loan_count = filtered_df["id_loan"].nunique()

col1, col2 = st.columns(2)
col1.metric("Jumlah Pinjaman", f"Rp {total_loan_amount:,.0f}")
col2.metric("Jumlah Loan", total_loan_count)

# Dataframe
st.subheader("Data Loan")
st.dataframe(filtered_df, use_container_width=True)

# Download
@st.cache_data
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='DataLoan')
    return output.getvalue()

# Fungsi untuk membersihkan nama agar aman dipakai sebagai nama file
def sanitize_filename(name):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name)

# Format tanggal jadi string dulu, lalu sanitize
date_range_str = f"{selected_dates[0].strftime('%Y%m%d')}_{selected_dates[1].strftime('%Y%m%d')}"
safe_date = sanitize_filename(date_range_str)

safe_company = sanitize_filename(selected_company)
safe_marketing = sanitize_filename(selected_marketing)

# Tombol download
st.download_button(
    label="Download Excel",
    data=to_excel(filtered_df),
    file_name=f"data_loan_{safe_company}_{safe_marketing}_{safe_date}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Chart loan status
st.subheader("Distribusi Loan Berdasarkan Perusahaan")
pie_data = filtered_df.groupby("borrower_name_company")["id_loan"].nunique().reset_index(name="jumlah_loan")
fig_pie = px.pie(pie_data, names="borrower_name_company", values="jumlah_loan")
st.plotly_chart(fig_pie)

# Top company
st.subheader("Top 5 Perusahaan")
top_companies = pie_data.sort_values("jumlah_loan", ascending=False).head(5)
fig_top = px.bar(top_companies, x="borrower_name_company", y="jumlah_loan", text_auto=True)
st.plotly_chart(fig_top)

# Marketing capaian
st.subheader("Capaian Marketing Harian")
selected_multimarketer = st.multiselect(
    "Pilih Marketing", options=filtered_df["marketing_name"].dropna().unique(),
    default=filtered_df["marketing_name"].dropna().unique()
)

filtered_marketing_df = filtered_df[filtered_df["marketing_name"].isin(selected_multimarketer)]
daily_count = filtered_marketing_df.groupby(["tanggal_pencairan", "marketing_name"])["id_loan"] \
    .nunique().reset_index(name="jumlah_loan")

fig_line = px.line(
    daily_count, x="tanggal_pencairan", y="jumlah_loan", color="marketing_name",
    title="Jumlah Loan per Hari", markers=True
)
st.plotly_chart(fig_line)
st.dataframe(daily_count, use_container_width=True)
# Top Marketing
st.subheader("Top 5 Marketing")
top_marketing = daily_count.groupby("marketing_name")["jumlah_loan"].sum().reset_index()
top_marketing = top_marketing.sort_values("jumlah_loan", ascending=False).head(5)
fig_top_marketing = px.bar(top_marketing, x="marketing_name", y="jumlah_loan", text_auto=True)
st.plotly_chart(fig_top_marketing)

## Download Capaian Harian Marketing
st.subheader("Download Capaian Harian Marketing")
# Fungsi untuk membersihkan nama file
# Fungsi aman nama file
def sanitize_filename(name):
    name = name.replace(" ", "_")
    return re.sub(r'[^a-zA-Z0-9_]', '', name)

# Gabungkan marketing
marketing_str = "_".join(selected_marketing)
safe_marketing = sanitize_filename(marketing_str)

# Format tanggal
date_range_str = f"{selected_dates[0].strftime('%Y%m%d')}_{selected_dates[1].strftime('%Y%m%d')}"

# Excel export
@st.cache_data
def to_excel_daily(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='CapaianHarian')
    return output.getvalue()

# Tombol download
st.download_button(
    "Download Capaian Harian",
    to_excel_daily(daily_count),
    file_name=f"capaian_harian_{safe_marketing}_{date_range_str}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Top Marketing Performance
st.subheader("📊 Capaian Bulanan Marketing")

filtered_df["bulan"] = filtered_df["tanggal_pencairan"].dt.to_period("M").astype(str)
monthly_summary = filtered_df.groupby(["bulan", "marketing_name"]).agg(
    jumlah_loan=("id_loan", "nunique"),
    total_pinjaman=("nominal_pinjaman", "sum")
).reset_index()

st.dataframe(monthly_summary, use_container_width=True)

fig_monthly = px.bar(
    monthly_summary,
    x="bulan",
    y="jumlah_loan",
    color="marketing_name",
    text_auto=True,
    title="Capaian Bulanan Marketing"
)
st.plotly_chart(fig_monthly)

@st.cache_data
def to_excel_monthly_summary(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='CapaianBulanan')
    return output.getvalue()

st.download_button(
    "Download Capaian Bulanan",
    to_excel_monthly_summary(monthly_summary),
    file_name=f"capaian_bulanan_{date_range_str}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)