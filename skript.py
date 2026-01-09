import streamlit as st
import pandas as pd
import plotly.express as px
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import io

# ======================================
# KONFIGURASI HALAMAN
# ======================================
st.set_page_config(
    page_title="Dashboard Bencana Aceh Tamiang 2024",
    page_icon="🌧️",
    layout="wide"
)

st.title("Dashboard Kejadian Bencana")
st.subheader("Kabupaten Aceh Tamiang - Tahun 2024")

# ======================================
# LOAD DATA
# ======================================
@st.cache_data
def load_data():
    df = pd.read_csv(
        "jumlah-kejadian-bencana-menurut-kecamatan-di-kabupaten-aceh-tamiang-tahun-2024.csv",
        on_bad_lines="skip"
    )

    df.columns = [  
        "kode_provinsi",
        "nama_provinsi",
        "kode_kabupaten",
        "nama_kabupaten",
        "kode_kecamatan",
        "nama_kecamatan",
        "kejadian_bencana",
        "jumlah",
        "satuan"
    ]



    # ======================================
    # HILANGKAN JENIS BENCANA TERTENTU
    # ======================================
    exclude_bencana = [
        "Evakuasi",
        "Orang Hilang",
        "Gagal Teknologi"
    ]

    df = df[~df["kejadian_bencana"].isin(exclude_bencana)]

    return df


df = load_data()

# ======================================
# SIDEBAR FILTER
# ======================================
st.sidebar.header("🔎 Filter Data")

kecamatan = st.sidebar.multiselect(
    "Kecamatan",
    options=df["nama_kecamatan"].unique(),
    default=df["nama_kecamatan"].unique()
)

bencana = st.sidebar.multiselect(
    "Jenis Bencana",
    options=df["kejadian_bencana"].unique(),
    default=df["kejadian_bencana"].unique()
)

filtered_df = df[
    (df["nama_kecamatan"].isin(kecamatan)) &
    (df["kejadian_bencana"].isin(bencana))
]

# ======================================
# METRICS
# ======================================
col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Kejadian",
    int(filtered_df["jumlah"].sum())
)

col2.metric(
    "Jumlah Kecamatan",
    filtered_df["nama_kecamatan"].nunique()
)

col3.metric(
    "Jenis Bencana",
    filtered_df["kejadian_bencana"].nunique()
)

st.divider()



# ======================================
# VISUALISASI
# ======================================
col4, col5 = st.columns(2)

# Bar Chart Kecamatan
with col4:
    kecamatan_chart = (
        filtered_df
        .groupby("nama_kecamatan")["jumlah"]
        .sum()
        .reset_index()
    )

    fig_bar = px.bar(
        kecamatan_chart,
        x="nama_kecamatan",
        y="jumlah",
        title="Jumlah Kejadian per Kecamatan",
        labels={"jumlah": "Jumlah Kejadian", "nama_kecamatan": "Kecamatan"}
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# Pie Chart Bencana
with col5:
    bencana_chart = (
        filtered_df
        .groupby("kejadian_bencana")["jumlah"]
        .sum()
        .reset_index()
    )

    fig_pie = px.pie(
        bencana_chart,
        names="kejadian_bencana",
        values="jumlah",
        title="Distribusi Jenis Bencana"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

st.divider()

# ======================================
# TABEL DATA
# ======================================
st.subheader("📄 Data Detail")
st.dataframe(filtered_df, use_container_width=True)
def generate_pdf(dataframe, total_kejadian, jumlah_kecamatan, jumlah_bencana):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(
        "<b>Dashboard Kejadian Bencana<br/>Kabupaten Aceh Tamiang 2024</b>",
        styles["Title"]
    ))

    elements.append(Paragraph("<br/>Ringkasan Data:", styles["Heading2"]))

    elements.append(Paragraph(
        f"""
        Total Kejadian: <b>{total_kejadian}</b><br/>
        Jumlah Kecamatan: <b>{jumlah_kecamatan}</b><br/>
        Jenis Bencana: <b>{jumlah_bencana}</b>
        """,
        styles["Normal"]
    ))

    elements.append(Paragraph("<br/>Detail Data:", styles["Heading2"]))

    table_data = [dataframe.columns.tolist()] + dataframe.values.tolist()

    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return buffer
