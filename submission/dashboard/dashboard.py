import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# Set page config untuk mengganti icon dan layout jadi wide
st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")

# Gunakan style seaborn yang lebih clean
sns.set(style='whitegrid')

# --- Helper Functions ---
def create_workingday_rentals_df(df):
    return df.groupby(['workingday', 'hr'])['cnt'].mean().reset_index()

def create_weather_rentals_df(df):
    return df.groupby('weathersit')['cnt'].mean().reset_index()

# --- Load Data ---
# Pastikan file hour.csv ada di folder yang sama
current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir, "hour.csv")

all_df = pd.read_csv(file_path)

# --- Sidebar ---
with st.sidebar:
    st.title("🚲 Bike Sharing")
    # Kamu bisa ganti URL logo ini dengan logo tim WAT kamu kalau ada!
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    st.markdown("### Filter Data")
    min_date = all_df["dteday"].min()
    max_date = all_df["dteday"].max()

    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter dataframe berdasarkan input sidebar
main_df = all_df[(all_df["dteday"] >= str(start_date)) & 
                (all_df["dteday"] <= str(end_date))]

# Menyiapkan dataframe untuk visualisasi
workingday_rentals_df = create_workingday_rentals_df(main_df)
weather_rentals_df = create_weather_rentals_df(main_df)

# --- Main Page Layout ---
st.title("Bike Sharing Analysis Dashboard 📊")
st.markdown("Dashboard ini menampilkan insight dari dataset penyewaan sepeda.")

# Row 1: Metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Rentals", value=f"{main_df.cnt.sum():,}")
with col2:
    st.metric("Registered Users", value=f"{main_df.registered.sum():,}")
with col3:
    st.metric("Casual Users", value=f"{main_df.casual.sum():,}")

st.divider()

# Row 2: Charts
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("Pola Hari Kerja vs Hari Libur")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(
        data=workingday_rentals_df, 
        x='hr', y='cnt', hue='workingday', 
        hue_order=[1, 0], palette=['#2E86C1', '#A9CCE3'], # Kombinasi biru profesional
        marker='o', ax=ax
    )
    ax.set_xlabel("Jam", fontsize=12)
    ax.set_ylabel("Rata-rata Penyewaan", fontsize=12)
    ax.legend(title='Keterangan', labels=['Hari Kerja', 'Hari Libur'])
    st.pyplot(fig)

with right_col:
    st.subheader("Pengaruh Cuaca")
    weather_map = {1: 'Clear', 2: 'Misty', 3: 'Light Snow/Rain', 4: 'Heavy Rain'}
    weather_rentals_df['weathersit'] = weather_rentals_df['weathersit'].map(weather_map)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=weather_rentals_df.sort_values(by="cnt", ascending=False), 
        x="weathersit", y="cnt", hue="weathersit",
        palette="viridis", ax=ax, legend=False
    )
    ax.set_xlabel(None)
    ax.set_ylabel("Rata-rata Penyewaan", fontsize=12)
    st.pyplot(fig)

# Footer
st.divider()
st.markdown(f"**Insight Singkat:** Penyewaan memuncak pada jam komuter di hari kerja. Cuaca cerah sangat mendominasi volume penyewaan.")
st.caption('Analysis by Widya | Data Science Enthusiast')
