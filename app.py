import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard Bahan Baku Pupuk", layout="wide")

st.title("📊 Dashboard Monitoring Bahan Baku Pabrik Pupuk")

# ========================
# LOAD DATA
# ========================
df = pd.read_csv("C:/Magang/Magang Konversi SKS/Dashboard/Data bahan baku.csv")
df["tanggal"] = pd.to_datetime(df["tanggal"])

# Pilih bahan baku
bahan_list = df["bahan"].unique()
selected_bahan = st.sidebar.selectbox("Pilih Bahan Baku", bahan_list)

df = df[df["bahan"] == selected_bahan]

# Hitung stok akhir
df["stok_akhir"] = df["stok_awal"] + df["stok_masuk"] - df["pemakaian"]

# ========================
# PARAMETER
# ========================
lead_time = st.sidebar.slider("Lead Time Supplier (hari)", 1, 14, 6)

avg_consumption = df["pemakaian"].mean()
max_consumption = df["pemakaian"].max()

safety_stock = max_consumption * lead_time
rop = (avg_consumption * lead_time) + safety_stock

current_stock = df["stok_akhir"].iloc[-1]
doi = current_stock / avg_consumption

# Status
if current_stock < safety_stock:
    status = "KRITIS"
elif current_stock < rop:
    status = "WARNING"
else:
    status = "AMAN"

# ========================
# KPI
# ========================
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Stok Saat Ini", f"{current_stock:,.0f} ton")
col2.metric("Konsumsi Rata-rata", f"{avg_consumption:,.0f} ton/hari")
col3.metric("Days of Inventory", f"{doi:.1f} hari")
col4.metric("Safety Stock", f"{safety_stock:,.0f} ton")
col5.metric("Status", status)

st.divider()

# ========================
# GRAFIK STOK & KONSUMSI
# ========================
st.subheader("📈 Tren Stok & Konsumsi")

fig, ax = plt.subplots()

ax.plot(df["tanggal"], df["stok_akhir"], label="Stok")
ax.plot(df["tanggal"], df["pemakaian"], label="Konsumsi")
ax.axhline(y=safety_stock, linestyle="--", label="Safety Stock")

ax.legend()
st.pyplot(fig)

# ========================
# ESTIMASI HARI OPERASI
# ========================
st.subheader("⏳ Estimasi Hari Operasi Pabrik")

min_days = current_stock / max_consumption
normal_days = current_stock / avg_consumption
max_days = current_stock / df["pemakaian"].min()

c1, c2, c3 = st.columns(3)
c1.metric("Minimum", f"{min_days:.1f} hari")
c2.metric("Normal", f"{normal_days:.1f} hari")
c3.metric("Maksimum", f"{max_days:.1f} hari")

# ========================
# REORDER ALERT
# ========================
st.subheader("🚨 Reorder Alert")

if current_stock <= rop:
    st.error("Stok mendekati ROP! Segera pesan bahan baku.")
else:
    st.success("Stok masih aman.")

# ========================
# FORECAST
# ========================
st.subheader("🔮 Forecast Kebutuhan")

df["forecast"] = df["pemakaian"].rolling(3).mean()

fig2, ax2 = plt.subplots()
ax2.plot(df["tanggal"], df["pemakaian"], label="Aktual")
ax2.plot(df["tanggal"], df["forecast"], label="Forecast")
ax2.legend()

st.pyplot(fig2)
