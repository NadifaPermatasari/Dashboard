import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

# ========================
# DATABASE
# ========================
conn = sqlite3.connect("bahan_baku.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS stok (
tanggal TEXT,
bahan TEXT,
stok_awal REAL,
pemakaian REAL,
stok_masuk REAL
)
""")

# ========================
# MENU
# ========================
menu = st.sidebar.selectbox("Menu", ["Input Data", "Dashboard"])

# ========================
# INPUT DATA
# ========================
if menu == "Input Data":
    st.title("📥 Input Data Bahan Baku")

    tanggal = st.date_input("Tanggal")
    bahan = st.selectbox("Bahan Baku", ["Amonia", "Fosfat", "Kalium"])
    stok_awal = st.number_input("Stok Awal", 0)
    pemakaian = st.number_input("Pemakaian Harian", 0)
    stok_masuk = st.number_input("Stok Masuk", 0)

    if st.button("Simpan"):
        c.execute("INSERT INTO stok VALUES (?,?,?,?,?)",
                  (tanggal, bahan, stok_awal, pemakaian, stok_masuk))
        conn.commit()
        st.success("Data tersimpan!")

# ========================
# DASHBOARD
# ========================
if menu == "Dashboard":
    st.title("📊 Dashboard Monitoring")

    df = pd.read_sql("SELECT * FROM stok", conn)

    if df.empty:
        st.warning("Belum ada data.")
    else:
        df["tanggal"] = pd.to_datetime(df["tanggal"])
        df["stok_akhir"] = df["stok_awal"] + df["stok_masuk"] - df["pemakaian"]

        avg_consumption = df["pemakaian"].mean()
        max_consumption = df["pemakaian"].max()
        lead_time = 6

        safety_stock = max_consumption * lead_time
        rop = (avg_consumption * lead_time) + safety_stock
        current_stock = df["stok_akhir"].iloc[-1]
        doi = current_stock / avg_consumption

        # KPI
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Stok Saat Ini", f"{current_stock:,.0f}")
        col2.metric("DOI", f"{doi:.1f} hari")
        col3.metric("Safety Stock", f"{safety_stock:,.0f}")
        col4.metric("ROP", f"{rop:,.0f}")

        # Grafik
        fig, ax = plt.subplots()
        ax.plot(df["tanggal"], df["stok_akhir"], label="Stok")
        ax.plot(df["tanggal"], df["pemakaian"], label="Pemakaian")
        ax.axhline(y=safety_stock, linestyle="--", label="Safety Stock")
        ax.legend()
        st.pyplot(fig)
