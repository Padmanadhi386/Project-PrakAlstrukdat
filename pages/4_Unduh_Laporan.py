import streamlit as st
from fungsi import wajib_login

wajib_login()

st.title("Unduh Laporan")
st.write("Simpan hasil CETAR ke file PDF, Excel, atau JSON")

berita = st.session_state["berita"]
if len(berita) == 0:
    st.warning("Weitss... Belum ada berita nih. Ambil berita dulu di halaman Beranda yakk...")
    if st.button("Ke Beranda"):
        st.switch_page("beranda.py")
else:
    st.info("Ehe.. Tombol unduh PDF, Excel, dan JSON sedang dikerjakan.")