import streamlit as st
from fungsi import baca_akun, cek_login, daftar_akun, siapkan_session

siapkan_session()

st.title("📰CETAR")
st.caption("(Cek Tren Teknologi Terbaru)")

if st.session_state["login"] is not None:
    akun = baca_akun()
    nama = st.session_state["login"]
    if nama in akun:
        nama = akun[nama]["nama"]
    st.success("Kamu sudah login sebagai **" + nama + "**.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Ke Beranda", type="primary"):
            st.switch_page("Beranda.py")
    with c2:
        if st.button("Logout"):
            st.session_state["login"] = None
            st.rerun()
else:
    st.write("Silakan login dulu untuk memakai CETAR. Belum punya akun? Pilih **Daftar akun**.")
    mode = st.radio("Pilih", ["Login", "Daftar akun"], horizontal=True, label_visibility="collapsed")

    if mode == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login", type="primary"):
            if username.strip() == "" or password == "":
                st.warning("Username dan password harus diisi.")
            elif cek_login(username, password):
                st.session_state["login"] = username.strip().lower()
                st.switch_page("Beranda.py")
            else:
                st.error("Username atau password salah.")
    else:
        nama_baru = st.text_input("Nama lengkap")
        username_baru = st.text_input("Username (huruf dan angka, minimal 3)")
        password_baru = st.text_input("Password (minimal 6 karakter)", type="password")
        ulangi = st.text_input("Ulangi password", type="password")
        if st.button("Daftar", type="primary"):
            if password_baru != ulangi:
                st.error("Password dan ulangi password tidak sama.")
            else:
                pesan = daftar_akun(username_baru, nama_baru, password_baru)
                if pesan is None:
                    st.success("Akun berhasil dibuat. Silakan pilih Login lalu masuk.")
                else:
                    st.error(pesan)