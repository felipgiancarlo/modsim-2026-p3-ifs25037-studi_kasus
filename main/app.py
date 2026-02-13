import streamlit as st
import simpy
import random
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# ==============================
# KONFIGURASI HALAMAN
# ==============================
st.set_page_config(
    page_title="Simulasi Piket IT Del",
    page_icon="🍱",
    layout="wide"
)

# ==============================
# HERO SECTION
# ==============================
st.markdown("""
<style>
.hero {
    background: linear-gradient(90deg, #1f4037, #99f2c8);
    padding: 25px;
    border-radius: 15px;
    color: white;
}
.hero h1 {
    margin-bottom: 5px;
}
.hero p {
    font-size: 16px;
}
</style>

<div class="hero">
    <h1>🍱 Simulasi Piket IT Del</h1>
    <p>Discrete Event System (DES) – Proses Pengisian Ompreng Mahasiswa</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ==============================
# SIDEBAR PARAMETER
# ==============================
st.sidebar.header("⚙️ Parameter Simulasi")

TOTAL_OMPRENG = st.sidebar.number_input(
    "Jumlah Ompreng",
    min_value=1,
    value=180
)

JUMLAH_PETUGAS = st.sidebar.number_input(
    "Jumlah Mahasiswa Piket",
    min_value=1,
    value=7
)

START_TIME = datetime.strptime(
    st.sidebar.time_input("Jam Mulai", value=datetime.strptime("07:00", "%H:%M").time()).strftime("%H:%M"),
    "%H:%M"
)

st.sidebar.markdown("---")
st.sidebar.caption("📘 MODSIM – IT Del")

# ==============================
# MODEL SIMULASI
# ==============================
class PiketITDelDES:
    def __init__(self, total_ompreng, petugas):
        self.env = simpy.Environment()
        self.petugas = simpy.Resource(self.env, capacity=petugas)
        self.total_ompreng = total_ompreng
        self.data = []

    def isi_lauk(self):
        return random.randint(30, 60)

    def angkut_batch(self):
        return random.randint(20, 60)

    def isi_nasi(self):
        return random.randint(30, 60)

    def proses_ompreng(self, nomor):
        with self.petugas.request() as req:
            yield req
            mulai = self.env.now

            t_lauk = self.isi_lauk()
            yield self.env.timeout(t_lauk)

            t_angkut = self.angkut_batch()
            yield self.env.timeout(t_angkut)

            t_nasi = self.isi_nasi()
            yield self.env.timeout(t_nasi)

            selesai = self.env.now

            self.data.append({
                "Ompreng": nomor,
                "Isi Lauk (detik)": t_lauk,
                "Angkut (detik)": t_angkut,
                "Isi Nasi (detik)": t_nasi,
                "Durasi Total (detik)": selesai - mulai,
                "Mulai (detik)": mulai,
                "Selesai (detik)": selesai
            })

    def run(self):
        for i in range(1, self.total_ompreng + 1):
            self.env.process(self.proses_ompreng(i))

        self.env.run()
        return pd.DataFrame(self.data)

# ==============================
# JALANKAN SIMULASI
# ==============================
if st.button("▶️ Jalankan Simulasi", use_container_width=True):
    with st.spinner("⏳ Menjalankan simulasi DES..."):
        model = PiketITDelDES(TOTAL_OMPRENG, JUMLAH_PETUGAS)
        df = model.run()

    # ==============================
    # POST PROCESSING WAKTU
    # ==============================
    df["Jam Mulai"] = df["Mulai (detik)"].apply(
        lambda x: (START_TIME + timedelta(seconds=x)).time()
    )
    df["Jam Selesai"] = df["Selesai (detik)"].apply(
        lambda x: (START_TIME + timedelta(seconds=x)).time()
    )

    # ==============================
    # METRIC
    # ==============================
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🍱 Total Ompreng", len(df))

    with col2:
        st.metric(
            "⏱️ Rata-rata Durasi",
            f"{df['Durasi Total (detik)'].mean():.1f} detik"
        )

    with col3:
        st.metric(
            "🕖 Selesai Pukul",
            df["Jam Selesai"].max().strftime("%H:%M:%S")
        )

    st.markdown("<hr>", unsafe_allow_html=True)

    # ==============================
    # GRAFIK
    # ==============================
    colA, colB = st.columns(2)

    with colA:
        fig1 = px.histogram(
            df,
            x="Durasi Total (detik)",
            nbins=30,
            title="📊 Distribusi Waktu Proses Ompreng",
            color_discrete_sequence=["#2ecc71"],
            opacity=0.85
        )
        fig1.update_layout(title_x=0.5)
        st.plotly_chart(fig1, use_container_width=True)

    with colB:
        fig2 = px.line(
            df.sort_values("Selesai (detik)"),
            x="Ompreng",
            y="Selesai (detik)",
            title="📈 Progres Penyelesaian Ompreng",
            markers=True
        )
        fig2.update_layout(title_x=0.5)
        st.plotly_chart(fig2, use_container_width=True)

    # ==============================
    # TABEL DATA
    # ==============================
    st.subheader("📄 Data Hasil Simulasi")
    st.caption("Detail waktu proses setiap ompreng")

    st.dataframe(
        df.sort_values("Ompreng"),
        use_container_width=True,
        height=350
    )

    # ==============================
    # DOWNLOAD
    # ==============================
    st.download_button(
        "⬇️ Download Data Simulasi (CSV)",
        df.to_csv(index=False).encode(),
        "hasil_simulasi_piket_itdel.csv",
        "text/csv",
        use_container_width=True
    )

    # ==============================
    # FOOTER
    # ==============================
    st.markdown("---")
    st.caption(
        "📘 MODSIM – Discrete Event System | "
        "Simulasi Piket IT Del | "
        f"Dijalankan pada {datetime.now().strftime('%d %B %Y %H:%M')}"
    )
