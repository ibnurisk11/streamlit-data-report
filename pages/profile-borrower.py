import streamlit as st
from streamlit.components.v1 import html
import io
from PIL import Image, ImageDraw, ImageFont
import pandas as pd  # Tambahkan impor pandas

# Judul halaman
st.title("Profile Borrower")
st.write("Halaman ini menampilkan data profil peminjam.")

# Load data from CSV
@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv("dataset/borrower-profile.csv")
    df["tanggal_lahir"] = pd.to_datetime(df["tanggal_lahir"], errors='coerce').dt.date

    # Cleansing double spaces and removing extra newlines
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].str.replace(r'\s+', ' ', regex=True).str.strip()

    return df

df = load_data()

# Filter by borrower ID
borrower_option = st.selectbox(
    "Pilih Borrower untuk filter:",
    options=[""] + [f"{row['id_borrower']} - {row['nama_borrower']}" for _, row in df.iterrows()]
)
borrower_id = borrower_option.split(" - ")[0] if borrower_option else None
filtered_df = df[df["id_borrower"] == borrower_id] if borrower_id else None

if filtered_df is not None and not filtered_df.empty:
    # Display data in a card-like format
    for index, row in filtered_df.iterrows():
        st.markdown(
    f"""
    <style>
        .profile-card {{
            border: 1px solid #94B4C1;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            background-color: #213448;
            color: #94B4C1;
        }}
        .profile-card h4, .profile-card p {{
            margin: 5px 0;
        }}
        .profile-card img {{
            width: 100%;
            max-width: 300px;
            margin-top: 10px;
            border-radius: 5px;
            display: block;
        }}
    </style>
    
    <div class="profile-card">
        <h4>ID Borrower: {row['id_borrower']}</h4>
        <p><strong>Nama:</strong> {row['nama_borrower']}</p>
        <p><strong>Email:</strong> {row['email']}</p>
        <p><strong>Tempat Lahir:</strong> {row['tempat_lahir']}</p>
        <p><strong>Tanggal Lahir:</strong> {row['tanggal_lahir']}</p>
        <p><strong>No HP:</strong> {row['no_handphone']}</p>
        <p><strong>Status Pernikahan:</strong> {row['status_pernikahan']}</p>
        <p><strong>Nama Pasangan:</strong> {row['nama_pasangan']}</p>
        <p><strong>NIK KTP:</strong> {row['nik_ktp']}</p>
        <p><strong>Alamat:</strong> {row['alamat']}</p>
        <p><strong>Nama Perusahaan:</strong>{row['nama_perusahaan']}</p>
    </div>
    """,
    unsafe_allow_html=True
)
else:
    st.warning("Data tidak ditemukan atau masukkan ID Borrower.")

def create_image_from_data(data):
    # Create an image with a light blue background
    img = Image.new("RGB", (800, 400), color="#E6F7FF")
    draw = ImageDraw.Draw(img)

    # Load a default font
    font = ImageFont.load_default()

    # Write data onto the image with alternating colors
    y = 10
    for i, (key, value) in enumerate(data.items()):
        text_color = "#000000" if i % 2 == 0 else "#00509E"  # Alternate between black and blue
        draw.text((10, y), f"{key}: {value}", fill=text_color, font=font)
        y += 20

    return img

if filtered_df is not None and not filtered_df.empty:
    for index, row in filtered_df.iterrows():
        # Convert row data to dictionary
        data_dict = row.to_dict()

        # Create image
        img = create_image_from_data(data_dict)

        # Save image to a BytesIO buffer
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        # Provide download button
        st.download_button(
            label="Download Data as Image",
            data=buffer,
            file_name=f"borrower_{row['id_borrower']}.png",
            mime="image/png"
        )