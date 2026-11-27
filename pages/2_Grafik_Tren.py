# Halaman 3: grafik tren (visualisasi pakai matplotlib)
import streamlit as st
from fungsi import wajib_login

wajib_login()

st.title("Grafik Tren")
st.write("Gambaran cepat topik dan berita yang paling ramai dari berita yang sudah diambil.")

berita = st.session_state["berita"]
if len(berita) == 0:
    st.warning("Belum ada berita. Ambil berita dulu di halaman Beranda.")
    if st.button("Ke Beranda"):
        st.switch_page("Beranda.py")
else:
    st.info("Grafik sedang dikerjakan (Tahap 2).")