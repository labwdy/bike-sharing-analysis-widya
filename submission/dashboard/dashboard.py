import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Konfigurasi Halaman (Harus di baris pertama setelah import)
st.set_page_config(page_title="Bike Sharing Analytics Dashboard", layout="wide")

# 1. Load data yang sudah dibersihkan
# Pastikan file all_data_clean.csv ada di folder yang sama
day_df = pd.read_csv("all_data_clean.csv")
day_df['dteday'] = pd.to_datetime(day_df['dteday'])

# --- 2. SIDEBAR (Pusat Kendali) ---
with st.sidebar:
    st.title("Bike Sharing Analysis 🚲")
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    st.write("Selamat Datang di Pusat Kendali Data!")
    
    # Filter A: Rentang Waktu
    min_date = day_df["dteday"].min()
    max_date = day_df["dteday"].max()
    
    start_date, end_date = st.date_input(
        label='Pilih Rentang Waktu:',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    # Filter B: Pilih Musim (Multi-select)
    season_options = day_df["season_label"].unique()
    selected_seasons = st.multiselect(
        label="Pilih Musim untuk Dianalisis:",
        options=season_options,
        default=season_options  # Default terpilih semua
    )

    # Informasi Profil Tambahan
    st.divider()
    st.markdown("### **Data Analyst Profile**")
    st.write("**Nama:** Widya")
    st.write("**ID Dicoding:** CDCC252D6X0841")
    st.write("**Proyek:** Analisis Data Bike-Sharing")

# --- 3. LOGIKA FILTER DATA ---
# Data difilter berdasarkan tanggal DAN musim yang dipilih di sidebar
main_df = day_df[(day_df["dteday"] >= str(start_date)) & 
                 (day_df["dteday"] <= str(end_date)) & 
                 (day_df["season_label"].isin(selected_seasons))]

# --- 4. MAIN PAGE (Visualisasi) ---
st.title("🚲 Dashboard Analisis Penyewaan Sepeda")
st.write(f"Menampilkan data dari rentang: **{start_date}** hingga **{end_date}**")

# A. METRIC CARDS (High-Level Summary)
col1, col2, col3 = st.columns(3)
with col1:
    total_rentals = main_df.cnt.sum()
    st.metric("Total Seluruh Penyewaan", value=f"{total_rentals:,}")

with col2:
    avg_temp = round(main_df.temp_actual.mean(), 1)
    st.metric("Rata-rata Suhu Harian", value=f"{avg_temp} °C")

with col3:
    avg_hum = round(main_df.hum_actual.mean(), 1)
    st.metric("Rata-rata Kelembapan", value=f"{avg_hum} %")

st.divider()

# B. TREN HARIAN (Pertanyaan 1 & 2 konteks waktu)
st.subheader("📈 Tren Dinamis Penyewaan Harian")
fig, ax = plt.subplots(figsize=(16, 6))
ax.plot(main_df["dteday"], main_df["cnt"], marker='o', linewidth=2, color="#2E86C1")
ax.set_title("Fluktuasi Penyewaan Sepeda per Hari", fontsize=20)
ax.set_xlabel(None)
ax.set_ylabel("Jumlah Penyewa", fontsize=15)
st.pyplot(fig)

# C. ANALISIS MUSIM & CUACA (Visualisasi Jawaban Pertanyaan)
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("📊 Performa Berdasarkan Musim")
    fig, ax = plt.subplots(figsize=(10, 8))
    # Grouping data berdasarkan pilihan filter
    season_data = main_df.groupby("season_label").cnt.sum().reset_index().sort_values(by="cnt", ascending=False)
    
    sns.barplot(
        y="cnt", 
        x="season_label",
        data=season_data,
        palette="viridis",
        hue="season_label", # Menghindari warning
        legend=False,
        ax=ax
    )
    ax.set_title("Total Penyewaan (Berdasarkan Musim Terpilih)", fontsize=18)
    ax.set_ylabel("Total Penyewa")
    ax.set_xlabel(None)
    st.pyplot(fig)

with col_b:
    st.subheader("🌡️ Korelasi Suhu terhadap Penyewa")
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.regplot(
        x=main_df["temp_actual"], 
        y=main_df["cnt"], 
        scatter_kws={'alpha':0.4, 'color':'#2E86C1'}, 
        line_kws={'color':'red'}
    )
    ax.set_title("Pola Hubungan Suhu vs Jumlah Penyewa", fontsize=18)
    ax.set_xlabel("Suhu Aktual (°C)")
    ax.set_ylabel("Jumlah Penyewa")
    st.pyplot(fig)

# D. ANALISIS LANJUTAN (Statistik Tabel)
st.divider()
st.subheader("📑 Tabel Ringkasan Statistik Strategis")
st.write("Gunakan tabel ini untuk melihat performa detail setiap musim.")

# Membuat rangkuman statistik
summary_table = main_df.groupby(by="season_label", as_index=False).agg({
    "cnt": ["count", "sum", "mean", "max", "min"]
})
# Mengatur nama kolom agar rapi
summary_table.columns = ["Musim", "Total Hari", "Total Penyewa", "Rata-rata Harian", "Penyewaan Tertinggi", "Penyewaan Terendah"]

# Menampilkan dataframe dengan highlight untuk nilai tertinggi
st.dataframe(summary_table.style.highlight_max(axis=0, color='#D4EFDF'))

# Penutup
st.caption(f'Copyright (c) Widya Analysis Project - 2026')