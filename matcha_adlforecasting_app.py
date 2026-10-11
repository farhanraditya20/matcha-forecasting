import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Forecasting - Artisanal Matcha",
    page_icon="🍵",
    layout="wide"
)

# ============================================================
# TITLE & INTRODUCTION
# ============================================================
st.title("🍵 Hikaru Matcha Bar & Factory")
st.subheader("Chapter 3: Demand Forecasting Application (Operations Management)")

st.markdown("""
Aplikasi ini mensimulasikan peramalan permintaan pasar untuk produk tren **Artisanal Matcha Series** (satuan botol/pack per minggu) 
guna merencanakan kebutuhan bahan baku bubuk matcha Uji Jepang dan susu segar di modul *Inventory/Purchasing* ERP.

Metode peramalan yang digunakan:
1. **Simple Moving Average (SMA)**
2. **Weighted Moving Average (WMA)**
3. **Exponential Smoothing**
""")

# ============================================================
# SIDEBAR - PARAMETERS
# ============================================================
st.sidebar.header("⚙️ Parameter Peramalan")

alpha = st.sidebar.slider(
    "Alpha (α) untuk Exponential Smoothing",
    min_value=0.01,
    max_value=1.00,
    value=0.30,
    step=0.05,
    help="Semakin tinggi alpha, semakin cepat ramalan merespons lonjakan tren matcha."
)

st.sidebar.markdown("---")
st.sidebar.subheader("Bobot Weighted Moving Average (WMA)")

w_4w = st.sidebar.number_input("4 Minggu Lalu", min_value=0.0, max_value=1.0, value=0.10, step=0.05)
w_3w = st.sidebar.number_input("3 Minggu Lalu", min_value=0.0, max_value=1.0, value=0.20, step=0.05)
w_2w = st.sidebar.number_input("2 Minggu Lalu", min_value=0.0, max_value=1.0, value=0.30, step=0.05)
w_1w = st.sidebar.number_input("Minggu Lalu", min_value=0.0, max_value=1.0, value=0.40, step=0.05)

total_weight = w_4w + w_3w + w_2w + w_1w
if abs(total_weight - 1.0) > 0.0001:
    st.sidebar.error(f"Total bobot = {total_weight:.2f}. Harus persis 1.00!")
else:
    st.sidebar.success("Total bobot = 1.00 ✓")

# ============================================================
# HISTORICAL DATA
# ============================================================
matcha_variants = [
    "Ceremonial Uji Matcha Latte (1L)",
    "Hojicha Roasted Milk Tea (1L)",
    "Matcha Strawberry Layer (Botol)",
    "Pure Matcha Powder Refill (Bag)",
    "Sea Salt Matcha Cream (Cup)",
    "Matcha Artisanal Drip Bag",
    "Jasmine Green Tea Blend",
    "Signature Matcha Bundle Box"
]

# Data historis permintaan dalam 4 minggu ke belakang
data = {
    "4 Minggu Lalu": [500, 300, 450, 200, 600, 350, 250, 800],
    "3 Minggu Lalu": [550, 320, 480, 220, 650, 380, 270, 850],
    "2 Minggu Lalu": [600, 350, 520, 250, 700, 400, 300, 920],
    "Last Week":     [700, 400, 600, 280, 800, 450, 340, 1050]
}

df = pd.DataFrame(data, index=matcha_variants)

st.header("1. Data Historis Permintaan (Unit)")
st.info("Silakan ubah angka di tabel bawah secara interaktif jika ingin mensimulasikan lonjakan tren musiman (*trend spike*).")
edited_df = st.data_editor(df, use_container_width=True)

edited_df = edited_df.rename(columns={"Last Week": "Minggu Lalu"})

# ============================================================
# SECTION 2 - SIMPLE MOVING AVERAGE (SMA)
# ============================================================
st.header("2. Part A — Simple Moving Average (SMA)")
st.markdown("Merata-ratakan permintaan dari 4 periode sebelumnya dengan bobot yang setara.")

edited_df["SMA Forecast"] = edited_df[["4 Minggu Lalu", "3 Minggu Lalu", "2 Minggu Lalu", "Minggu Lalu"]].mean(axis=1)

st.dataframe(edited_df[["SMA Forecast"]].style.format("{:,.1f}"), use_container_width=True)

# ============================================================
# SECTION 3 - WEIGHTED MOVING AVERAGE (WMA)
# ============================================================
st.header("3. Part B — Weighted Moving Average (WMA)")
st.markdown("Memberikan bobot lebih besar pada minggu terakhir untuk menangkap tren kenaikan pasar dengan cepat.")

if abs(total_weight - 1.0) <= 0.0001:
    edited_df["WMA Forecast"] = (
        w_4w * edited_df["4 Minggu Lalu"] +
        w_3w * edited_df["3 Minggu Lalu"] +
        w_2w * edited_df["2 Minggu Lalu"] +
        w_1w * edited_df["Minggu Lalu"]
    )
else:
    edited_df["WMA Forecast"] = 0

st.dataframe(edited_df[["WMA Forecast"]].style.format("{:,.1f}"), use_container_width=True)

# ============================================================
# SECTION 4 - VISUALIZATION COMPARISON
# ============================================================
st.header("4. Grafik Perbandingan SMA vs WMA")

chart_data = edited_df[["SMA Forecast", "WMA Forecast"]].reset_index().rename(columns={"index": "Varian Matcha"})
melted_chart = chart_data.melt(id_vars="Varian Matcha", value_vars=["SMA Forecast", "WMA Forecast"], var_name="Metode", value_name="Forecast Unit")

fig = px.bar(melted_chart, x="Varian Matcha", y="Forecast Unit", color="Metode", barmode="group",
             title="Perbandingan Hasil Peramalan Permintaan Artisanal Matcha")
st.plotly_chart(fig, use_container_width=True)

# ============================================================
# SECTION 5 - EXPONENTIAL SMOOTHING
# ============================================================
st.header("5. Part C & D — Exponential Smoothing")

col1, col2 = st.columns(2)
with col1:
    prev_forecast = st.number_input("Forecast Minggu Lalu (Unit)", value=1000.0, step=10.0)
with col2:
    actual_demand = st.number_input("Actual Demand Minggu Lalu (Unit)", value=1050.0, step=10.0)

exp_forecast = prev_forecast + alpha * (actual_demand - prev_forecast)

st.success(f"📌 **Hasil Peramalan untuk Minggu Ini:** {exp_forecast:,.1f} unit")

with st.expander("🔎 Lihat Rumus & Detail Perhitungan"):
    st.latex(r"F_t = F_{t-1} + \alpha (A_{t-1} - F_{t-1})")
    st.latex(rf"F_t = {prev_forecast} + {alpha} ({actual_demand} - {prev_forecast}) = {exp_forecast:,.1f}")