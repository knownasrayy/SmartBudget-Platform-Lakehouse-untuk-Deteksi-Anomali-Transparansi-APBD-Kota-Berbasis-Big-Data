import streamlit as st
import pandas as pd
import numpy as np
import os

# Konfigurasi Halaman
st.set_page_config(page_title="SmartBudget Lakehouse", layout="wide")

# Setup Path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GOLD_DIR = os.path.join(BASE_DIR, "data", "gold")
ANOMALY_FILE = os.path.join(GOLD_DIR, "gold_anomaly_transactions.csv")
SUMMARY_FILE = os.path.join(GOLD_DIR, "gold_skpd_summary.csv")

# Sidebar Navigasi
st.sidebar.title("Navigasi Dasbor")
halaman = st.sidebar.radio("Pilih Halaman:", ["Ringkasan Anggaran", "Deteksi Anomali", "Analisis Lakehouse"])

# Judul Utama
st.title("SmartBudget Platform: Deteksi Anomali APBD")
st.markdown("Dasbor interaktif untuk transparansi dan deteksi anomali anggaran berbasis Big Data Lakehouse.")

# Cek keberadaan file Gold
if not os.path.exists(ANOMALY_FILE) or not os.path.exists(SUMMARY_FILE):
    st.warning("⚠️ **Data Gold belum tersedia.** Silakan jalankan ML Pipeline (`python src/ml_engine/pipeline.py`) terlebih dahulu untuk menghasilkan data analitik di folder `data/gold/`.")
else:
    # Load Data
    @st.cache_data
    def load_data():
        df_anomali = pd.read_csv(ANOMALY_FILE)
        df_summary = pd.read_csv(SUMMARY_FILE)
        return df_anomali, df_summary
        
    df_anomali, df_summary = load_data()
    
    # Hitung Metrik Utama
    total_anggaran = df_summary['total_pagu'].sum() if 'total_pagu' in df_summary.columns else 0
    df_is_flagged = df_anomali[df_anomali['is_flagged'] == True] if 'is_flagged' in df_anomali.columns else df_anomali
    total_janggal = df_is_flagged['pagu_anggaran'].sum() if not df_is_flagged.empty else 0
    jumlah_proyek_risiko = len(df_is_flagged)
    
    # Format mata uang
    def format_rupiah(angka):
        if angka >= 1e12:
            return f"Rp {angka/1e12:.2f} T"
        elif angka >= 1e9:
            return f"Rp {angka/1e9:.2f} M"
        elif angka >= 1e6:
            return f"Rp {angka/1e6:.2f} Jt"
        return f"Rp {angka:,.0f}"

    # Kartu Metrik
    st.subheader("Ringkasan Metrik Anggaran")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Anggaran Janggal (Anomali)", value=format_rupiah(total_janggal), delta=f"{jumlah_proyek_risiko} Proyek Terindikasi", delta_color="inverse")
    with col2:
        st.metric(label="Jumlah Proyek Berisiko", value=f"{jumlah_proyek_risiko} Proyek", delta_color="normal")
    with col3:
        st.metric(label="Total Anggaran Terpantau", value=format_rupiah(total_anggaran))

    st.divider()
    
    if halaman == "Ringkasan Anggaran":
        st.subheader("Peta Persebaran Proyek (Berdasarkan Kecamatan)")
        koordinat_kecamatan = {
            "Tambaksari": {"lat": -7.251, "lon": 112.766},
            "Gubeng": {"lat": -7.279, "lon": 112.753},
            "Rungkut": {"lat": -7.322, "lon": 112.784},
            "Wonokromo": {"lat": -7.299, "lon": 112.736},
            "Tenggilis Mejoyo": {"lat": -7.325, "lon": 112.759},
            "Sukolilo": {"lat": -7.290, "lon": 112.784},
            "Mulyorejo": {"lat": -7.270, "lon": 112.793},
            "Bulak": {"lat": -7.234, "lon": 112.788},
            "Kenjeran": {"lat": -7.221, "lon": 112.775},
            "Semampir": {"lat": -7.215, "lon": 112.744}
        }
        
        if 'kecamatan' in df_anomali.columns:
            df_map = df_anomali.groupby('kecamatan').size().reset_index(name='jumlah_proyek')
            df_map['lat'] = df_map['kecamatan'].map(lambda x: koordinat_kecamatan.get(x, {}).get('lat', -7.250445))
            df_map['lon'] = df_map['kecamatan'].map(lambda x: koordinat_kecamatan.get(x, {}).get('lon', 112.768845))
            st.map(df_map, latitude='lat', longitude='lon')
        else:
            st.info("💡 Data 'kecamatan' belum tersedia di data Gold untuk menampilkan peta.")

        st.divider()

        st.subheader("Distribusi Anggaran per SKPD (10 Teratas)")
        if 'nama_skpd' in df_summary.columns and 'total_pagu' in df_summary.columns:
            st.bar_chart(df_summary.set_index('nama_skpd')['total_pagu'].sort_values(ascending=False).head(10))
            
    elif halaman == "Deteksi Anomali":
        st.subheader("Daftar Proyek Terindikasi Anomali")
        st.markdown("Tabel di bawah ini menampilkan transaksi yang dilabeli 'Anomali' oleh model **Isolation Forest & Z-Score** milik Raya.")
        
        if not df_is_flagged.empty:
            kolom_tampil = ['id_transaksi', 'nama_skpd', 'uraian_belanja', 'pagu_anggaran', 'realisasi', 'nama_vendor', 'is_flagged']
            kolom_tersedia = [c for c in kolom_tampil if c in df_is_flagged.columns]
            st.dataframe(df_is_flagged[kolom_tersedia].sort_values(by='pagu_anggaran', ascending=False), use_container_width=True)
        else:
            st.success("🎉 Tidak ada anomali yang terdeteksi saat ini.")
            
    elif halaman == "Analisis Lakehouse":
        st.subheader("Data Gold: Ringkasan SKPD")
        st.dataframe(df_summary, use_container_width=True)
