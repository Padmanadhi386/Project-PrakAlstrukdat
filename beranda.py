import streamlit as st
from fungsi import(DAFTAR_BERITA)

st.title("📰CETAR")
st.caption("(Cek Tren Teknologi Terbaru)")
st.markdown("##### Ringkasan tren berita teknologi, biar nggak perlu baca puluhan artikel satu per satu.")
st.subheader("Ambil berita terbaru")

kiri, kanan = st.columns(2)
with kiri:
    pilihan = st.selectbox("Jenis berita", list(DAFTAR_BERITA.keys()))
with kanan:
    jumlah = st.slider("Jumlah berita", min_value=10, max_value=50, value=30, step=5)

b1, b2 = st.columns(2)
with b1:
    tombol_ambil = st.button("Ambil Berita", type="primary")
with b2:
    tombol_contoh = st.button("Pakai data contoh (offline)")


