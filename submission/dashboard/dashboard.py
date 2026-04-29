import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# Set page title and icon
st.set_page_config(
    page_title="Bike Sharing Dashboard Analysis",
    page_icon="🚲",
    layout="wide"
)

# --- HELPER FUNCTIONS ---
def create_daily_rent_df(df):
    daily_rent_df = df.resample(rule='D', on='dteday').agg({
        "cnt": "sum"
    }).reset_index()
    return daily_rent_df

def create_byseason_df(df):
    byseason_df = df.groupby(by="season").cnt.mean().reset_index()
    season_names = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
    byseason_df['season'] = byseason_df['season'].map(season_names)
    return byseason_df

def create_byweather_df(df):
    byweather_df = df.groupby(by="weathersit").cnt.mean().reset_index()
    weather_names = {1: "Clear", 2: "Misty", 3: "Light Snow/Rain", 4: "Heavy Rain"}
    byweather_df['weathersit'] = byweather_df['weathersit'].map(weather_names)
    return byweather_df

# --- LOAD DATA ---
@st.cache_data
def load_data():
    # 1. Tentukan nama file
    file_name = "hour.csv"
    
    # 2. Cek beberapa lokasi kemungkinan file berada
    # Lokasi A: Di folder yang sama dengan dashboard.py
    path_a = os.path.join(os.path.dirname(__file__), file_name)
    # Lokasi B: Di dalam folder 'dashboard' (jika dijalankan dari root)
    path_b = os.path.join("dashboard", file_name)
    # Lokasi C: Langsung di root
    path_c = file_name
    
    if os.path.exists(path_a):
        df = pd.read_csv(path_a)
    elif os.path.exists(path_b):
        df = pd.read_csv(path_b)
    elif os.path.exists(path_c):
        df = pd.read_csv(path_c)
    else:
        # Jika semua gagal, pakai URL GitHub Raw kamu (PASTIKAN REPO PUBLIC)
        url = "https://raw.githubusercontent.com/widya/bike-sharing-analysis-widya/main/dashboard/hour.csv"
        df = pd.read_csv(url)
        
    df['dteday'] = pd.to_datetime(df['dteday'])
    return df

all_df = load_data()

# --- SIDEBAR FILTER ---
with st.sidebar:
    st.header("Filter Analisis")
    
    # 1. Filter Rentang Waktu (Date Filter)
    min_date = all_df['dteday'].min()
    max_date = all_df['dteday'].max()
    
    try:
        start_date, end_date = st.date_input(
            label='Pilih Rentang Waktu',
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )
    except ValueError:
        st.error("Pilih rentang tanggal yang valid (Mulai - Selesai)")
        st.stop()

    # 2. Filter Musim (Multiselect)
    season_map = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
    selected_seasons = st.multiselect(
        label="Pilih Musim",
        options=list(season_map.keys()),
        default=list(season_map.keys()),
        format_func=lambda x: season_map[x]
    )

    # 3. Filter Kondisi Cuaca (Multiselect) - TAMBAHAN BIAR MAKIN DINAMIS
    weather_map = {1: 'Clear', 2: 'Misty', 3: 'Light Snow/Rain', 4: 'Heavy Rain'}
    selected_weather = st.multiselect(
        label="Kondisi Cuaca",
        options=list(weather_map.keys()),
        default=list(weather_map.keys()),
        format_func=lambda x: weather_map[x]
    )

# --- MENERAPKAN FILTER UTAMA ---
main_df = all_df[
    (all_df['dteday'] >= pd.to_datetime(start_date)) & 
    (all_df['dteday'] <= pd.to_datetime(end_date)) &
    (all_df['season'].isin(selected_seasons)) &
    (all_df['weathersit'].isin(selected_weather))
]

# Menyiapkan dataframe untuk visualisasi
daily_rent_df = create_daily_rent_df(main_df)
byseason_df = create_byseason_df(main_df)
byweather_df = create_byweather_df(main_df)

# --- MAIN PAGE ---
st.title("🚲 Bike Sharing Analysis Dashboard")
st.markdown(f"Menampilkan statistik dari **{start_date}** hingga **{end_date}**")

# Section 1: Metrics (Responsif terhadap filter)
col1, col2, col3 = st.columns(3)
with col1:
    total_rentals = main_df.cnt.sum()
    st.metric("Total Penyewaan", value=f"{total_rentals:,}")

with col2:
    # Denormalisasi suhu (berdasarkan info dataset)
    avg_temp = round(main_df.temp.mean() * 41, 1) 
    st.metric("Rata-rata Suhu", value=f"{avg_temp} °C")

with col3:
    avg_hum = round(main_df.hum.mean() * 100, 1)
    st.metric("Kelembapan Udara", value=f"{avg_hum}%")

st.divider()

# Section 2: Tren Harian
st.subheader("Tren Penyewaan Harian")
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_rent_df["dteday"],
    daily_rent_df["cnt"],
    marker='o', 
    linewidth=2,
    color="#1f77b4"
)
ax.set_ylabel("Jumlah Penyewaan")
ax.grid(axis='y', linestyle='--', alpha=0.7)
st.pyplot(fig)

# Section 3: Analisis Cuaca & Musim
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Penyewaan Berdasarkan Musim")
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(
        y="cnt", 
        x="season",
        data=byseason_df.sort_values(by="cnt", ascending=False),
        hue="season",
        palette="Blues_d",
        legend=False,
        ax=ax
    )
    ax.set_title("Rata-rata Penyewaan per Musim", fontsize=20)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    st.pyplot(fig)

with col_b:
    st.subheader("Penyewaan Berdasarkan Cuaca")
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(
        y="cnt", 
        x="weathersit",
        data=byweather_df.sort_values(by="cnt", ascending=False),
        hue="weathersit",
        palette="viridis",
        legend=False,
        ax=ax
    )
    ax.set_title("Rata-rata Penyewaan per Kondisi Cuaca", fontsize=20)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    st.pyplot(fig)

# Section 4: Insight Otomatis (Fitur Berguna Tambahan)
st.divider()
st.subheader("💡 Ringkasan Analisis")
col_ins1, col_ins2 = st.columns(2)

with col_ins1:
    if not byweather_df.empty:
        best_weather = byweather_df.sort_values(by="cnt", ascending=False).iloc[0]['weathersit']
        st.info(f"Dalam filter ini, performa penyewaan tertinggi terjadi pada kondisi cuaca: **{best_weather}**")
    else:
        st.warning("Data tidak tersedia untuk kombinasi filter ini.")

with col_ins2:
    peak_hour = main_df.groupby("hr")["cnt"].mean().idxmax()
    st.info(f"Secara rata-rata, jam puncak penggunaan sepeda dalam filter ini adalah pukul **{peak_hour}:00**.")

st.caption("Copyright © Widya Analysis 2026")