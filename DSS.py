import streamlit as st
import pandas as pd

# Konfigurasi Halaman Streamlit
st.set_page_config(page_title="DSS Tempat Kost - SAW", page_icon="🏠", layout="centered")

# Menggunakan CSS kustom (mirip dengan style.css sebelumnya)
st.markdown("""
    <style>
    .hero {
        background: linear-gradient(135deg, #0d1b2a, #1b263b);
        color: white;
        padding: 40px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# Header Aplikasi
st.markdown("""
    <div class="hero">
        <h1>Sistem Pendukung Keputusan</h1>
        <h3>Pemilihan Tempat Kost</h3>
        <p>Metode Simple Additive Weighting (SAW)</p>
    </div>
""", unsafe_allow_html=True)

# Inisialisasi Data Awal di Session State (agar data tidak hilang saat layar di-refresh)
if 'data_kost' not in st.session_state:
    st.session_state.data_kost = [
        {'Nama': 'Kost Mawar', 'Harga': 800.0, 'Jarak': 1.5, 'Fasilitas': 4, 'Keamanan': 5, 'WiFi': 4},
        {'Nama': 'Kost Melati', 'Harga': 1000.0, 'Jarak': 0.8, 'Fasilitas': 5, 'Keamanan': 4, 'WiFi': 5},
        {'Nama': 'Kost Anggrek', 'Harga': 700.0, 'Jarak': 2.0, 'Fasilitas': 3, 'Keamanan': 4, 'WiFi': 3},
        {'Nama': 'Kost Dahlia', 'Harga': 1200.0, 'Jarak': 0.5, 'Fasilitas': 5, 'Keamanan': 5, 'WiFi': 5},
        {'Nama': 'Kost Kenanga', 'Harga': 900.0, 'Jarak': 1.0, 'Fasilitas': 4, 'Keamanan': 4, 'WiFi': 4}
    ]

# -------------------------------------------------------------
# 1. BAGIAN INPUT DATA
# -------------------------------------------------------------
st.subheader("Input Data Kost")
with st.form("form_tambah_data"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        nama = st.text_input("Nama Kost")
        fasilitas = st.number_input("Fasilitas (1-5)", min_value=1, max_value=5, value=3)
    with col2:
        harga = st.number_input("Harga", min_value=1.0, step=50.0)
        keamanan = st.number_input("Keamanan (1-5)", min_value=1, max_value=5, value=3)
    with col3:
        jarak = st.number_input("Jarak (Km)", min_value=0.1, step=0.1)
        wifi = st.number_input("WiFi (1-5)", min_value=1, max_value=5, value=3)
        
    submit_btn = st.form_submit_button("Tambah Kost")
    
    if submit_btn:
        if nama.strip() == "":
            st.error("Nama kost tidak boleh kosong!")
        else:
            # Tambah ke session state
            st.session_state.data_kost.append({
                'Nama': nama, 
                'Harga': harga, 
                'Jarak': jarak, 
                'Fasilitas': fasilitas, 
                'Keamanan': keamanan, 
                'WiFi': wifi
            })
            st.success(f"Berhasil menambahkan {nama}!")

# -------------------------------------------------------------
# 2. BAGIAN TABEL DATA KOST
# -------------------------------------------------------------
st.subheader("Data Kost Saat Ini")
df_kost = pd.DataFrame(st.session_state.data_kost)
df_kost.index = df_kost.index + 1 # Memulai nomor tabel dari 1
st.dataframe(df_kost, use_container_width=True)

st.write("---")

# -------------------------------------------------------------
# 3. BAGIAN PERHITUNGAN SAW
# -------------------------------------------------------------
if st.button("Hitung Ranking SAW", type="primary", use_container_width=True):
    if len(df_kost) == 0:
        st.warning("Data kosong, tidak dapat menghitung.")
    else:
        # Bobot Kriteria
        bobot = {'Harga': 0.30, 'Jarak': 0.25, 'Fasilitas': 0.20, 'Keamanan': 0.15, 'WiFi': 0.10}
        
        # Penentuan Nilai Ekstrem (Cost & Benefit)
        # Harga & Jarak = Atribut Cost (Minimal lebih baik)
        min_harga = df_kost['Harga'].min()
        min_jarak = df_kost['Jarak'].min()
        
        # Fasilitas, Keamanan, WiFi = Atribut Benefit (Maksimal lebih baik)
        max_fas = df_kost['Fasilitas'].max()
        max_kea = df_kost['Keamanan'].max()
        max_wifi = df_kost['WiFi'].max()
        
        # Proses Normalisasi dan Perhitungan Skor
        hasil = []
        for index, row in df_kost.iterrows():
            skor_harga = (min_harga / row['Harga']) * bobot['Harga']
            skor_jarak = (min_jarak / row['Jarak']) * bobot['Jarak']
            skor_fasilitas = (row['Fasilitas'] / max_fas) * bobot['Fasilitas']
            skor_keamanan = (row['Keamanan'] / max_kea) * bobot['Keamanan']
            skor_wifi = (row['WiFi'] / max_wifi) * bobot['WiFi']
            
            total_skor = skor_harga + skor_jarak + skor_fasilitas + skor_keamanan + skor_wifi
            
            hasil.append({
                'Nama Kost': row['Nama'],
                'Nilai SAW': total_skor
            })
            
        # Mengubah hasil menjadi DataFrame, lalu urutkan (Ranking)
        df_hasil = pd.DataFrame(hasil)
        df_hasil = df_hasil.sort_values(by='Nilai SAW', ascending=False).reset_index(drop=True)
        df_hasil.index = df_hasil.index + 1
        
        # Format nilai agar hanya 4 angka di belakang koma untuk kerapian
        df_hasil['Nilai SAW'] = df_hasil['Nilai SAW'].apply(lambda x: f"{x:.4f}")
        
        st.subheader("Hasil Ranking")
        st.table(df_hasil)
        
        # Tampilkan Kost Terbaik
        kost_terbaik = df_hasil.iloc[0]
        st.success(f"🏆 Kost Terbaik: **{kost_terbaik['Nama Kost']}** dengan skor **{kost_terbaik['Nilai SAW']}**")