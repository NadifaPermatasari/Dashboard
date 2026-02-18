import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard Stok Bahan", layout="wide")

# ======================
# DATABASE SEMENTARA
# ======================
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(
        columns=["tanggal","bahan","stok_awal","pemakaian","stok_masuk","stok_akhir"]
    )

# ======================
# SIDEBAR MENU
# ======================
menu = st.sidebar.selectbox(
    "Menu",
    ["Dashboard", "Input Data", "Upload Data", "Rekapan", "Update Data"]
)

# ======================
# INPUT DATA MANUAL
# ======================
if menu == "Input Data":
    st.title("Input Data Stok")

    with st.form("form_input"):
        tanggal = st.date_input("Tanggal")
        bahan = st.text_input("Nama Bahan")
        stok_awal = st.number_input("Stok Awal", min_value=0)
        pemakaian = st.number_input("Pemakaian", min_value=0)
        stok_masuk = st.number_input("Stok Masuk", min_value=0)

        submit = st.form_submit_button("Simpan")

    if submit:
        stok_akhir = stok_awal + stok_masuk - pemakaian

        new_data = pd.DataFrame({
            "tanggal":[tanggal],
            "bahan":[bahan],
            "stok_awal":[stok_awal],
            "pemakaian":[pemakaian],
            "stok_masuk":[stok_masuk],
            "stok_akhir":[stok_akhir]
        })

        st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)
        st.success("Data berhasil ditambahkan")

# ======================
# UPLOAD DATA CSV
# ======================
elif menu == "Upload Data":
    st.title("Upload Data CSV")

    file = st.file_uploader("Upload file CSV", type=["csv"])

    if file:
        df = pd.read_csv(file)

        df["stok_akhir"] = df["stok_awal"] + df["stok_masuk"] - df["pemakaian"]

        st.session_state.data = pd.concat([st.session_state.data, df], ignore_index=True)
        st.success("Data berhasil diupload")

        st.dataframe(df)

# ======================
# REKAPAN DATA
# ======================
elif menu == "Rekapan":
    st.title("Rekapan Data")

    st.dataframe(st.session_state.data)

    st.subheader("Total Pemakaian per Bahan")
    rekap = st.session_state.data.groupby("bahan")["pemakaian"].sum()
    st.bar_chart(rekap)

# ======================
# UPDATE DATA
# ======================
elif menu == "Update Data":
    st.title("Edit / Update Data")

    if len(st.session_state.data) == 0:
        st.warning("Belum ada data")
    else:
        index = st.selectbox("Pilih index data", st.session_state.data.index)

        row = st.session_state.data.loc[index]

        stok_awal = st.number_input("Stok Awal", value=int(row["stok_awal"]))
        pemakaian = st.number_input("Pemakaian", value=int(row["pemakaian"]))
        stok_masuk = st.number_input("Stok Masuk", value=int(row["stok_masuk"]))

        if st.button("Update"):
            stok_akhir = stok_awal + stok_masuk - pemakaian

            st.session_state.data.loc[index,"stok_awal"] = stok_awal
            st.session_state.data.loc[index,"pemakaian"] = pemakaian
            st.session_state.data.loc[index,"stok_masuk"] = stok_masuk
            st.session_state.data.loc[index,"stok_akhir"] = stok_akhir

            st.success("Data berhasil diperbarui")

# ======================
# DASHBOARD VISUAL
# ======================
elif menu == "Dashboard":
    st.title("Dashboard Stok Bahan")

    if len(st.session_state.data) == 0:
        st.info("Belum ada data")
    else:
        col1, col2, col3 = st.columns(3)

        total_stok = st.session_state.data["stok_akhir"].sum()
        total_pemakaian = st.session_state.data["pemakaian"].sum()
        total_masuk = st.session_state.data["stok_masuk"].sum()

        col1.metric("Total Stok Akhir", total_stok)
        col2.metric("Total Pemakaian", total_pemakaian)
        col3.metric("Total Stok Masuk", total_masuk)

        st.subheader("Grafik Tren Stok")
        fig, ax = plt.subplots()
        st.session_state.data.groupby("tanggal")["stok_akhir"].sum().plot(ax=ax)
        st.pyplot(fig)

        st.subheader("Distribusi Pemakaian Bahan")
        fig2, ax2 = plt.subplots()
        st.session_state.data.groupby("bahan")["pemakaian"].sum().plot(kind="bar", ax=ax2)
        st.pyplot(fig2)
