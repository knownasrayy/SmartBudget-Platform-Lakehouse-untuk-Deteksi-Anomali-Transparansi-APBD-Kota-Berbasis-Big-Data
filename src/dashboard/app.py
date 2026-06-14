import streamlit as st
import pandas as pd
import numpy as np

# Konfigurasi Halaman
st.set_page_config(page_title="SmartBudget Lakehouse", layout="wide")

# Sidebar Navigasi
st.sidebar.title("Navigasi Dasbor")
st.sidebar.radio("Pilih Halaman:", ["Ringkasan Anggaran", "Deteksi Anomali", "Analisis Lakehouse"])

# Judul Utama
st.title("SmartBudget Platform: Deteksi Anomali APBD Surabaya")
st.markdown("Dasbor interaktif untuk transparansi dan deteksi anomali anggaran berbasis Big Data Lakehouse.")

# Kartu Metrik
st.subheader("Ringkasan Metrik Anggaran")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Anggaran Janggal", value="Rp 45.2 M", delta="12% dari tahun lalu", delta_color="inverse")
with col2:
    st.metric(label="Jumlah Proyek Berisiko", value="14 Proyek", delta="-2 Proyek", delta_color="normal")
with col3:
    st.metric(label="Total Anggaran Terpantau", value="Rp 2.1 T")

st.divider()

# Visualisasi Peta Persebaran (Titik Acak Area Surabaya)
st.subheader("Peta Persebaran Proyek (Simulasi Surabaya)")
# Koordinat tengah Surabaya: Latitude -7.250445, Longitude 112.768845
# Kita buat 15 titik acak di sekitar Surabaya
map_data = pd.DataFrame(
    np.random.randn(15, 2) / [50, 50] + [-7.250445, 112.768845],
    columns=['lat', 'lon']
)
st.map(map_data)

st.divider()

# Visualisasi Grafik Distribusi Anggaran (Data Acak)
st.subheader("Distribusi Anggaran per Dinas (Simulasi)")
chart_data = pd.DataFrame(
    np.random.randn(20, 3) * 100 + 500,
    columns=['Dinas Pendidikan', 'Dinas Kesehatan', 'Dinas Pekerjaan Umum']
)
st.line_chart(chart_data)
