import streamlit as st
from fungsi import siapkan_gemini, wajib_login

wajib_login()

st.title("Asisten AI")
st.write("Gemini membaca data berita yang sudah diolah, lalu menjelaskannya dalam Bahasa Indonesia.")

berita = st.session_state["berita"]
model = siapkan_gemini()

if len(berita) == 0:
    st.warning("Belum ada berita nih. Ambil berita dulu di halaman Beranda yah.")
    if st.button("Ke Beranda"):
        st.switch_page("beranda.py")
elif model is None:
    st.error(" WOEEE API key Gemini belum diisi. Bikin file .streamlit/secrets.toml dulu kocak "
             "GEMINI_API_KEY = \"...\" lalu jalankan ulang aplikasi.")
else:
    st.info("Maaf, fitur ringkasan tren sedang dikerjakan.")