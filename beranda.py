import streamlit as st
from fungsi import (DAFTAR_BERITA, ambil_berita, berita_contoh, hitung_sumber, jadi_tabel, merge_sort, wajib_login)

wajib_login()

st.title("📰CETAR")
st.caption("(Cek Tren Teknologi Terbaru)")
st.markdown("##### Ringkasan tren berita teknologi, biar nggak perlu baca puluhan artikel satu per satu.")
st.subheader("Ambil berita terbaru")

kiri, tengah, kanan = st.columns(3)
with kiri:
    pilihan = st.selectbox("Jenis berita", list(DAFTAR_BERITA.keys()))
with tengah:
    topik = st.text_input("Topik (boleh kosong)", placeholder="contoh: AI, apple, security")
with kanan:
    jumlah = st.slider("Jumlah berita", min_value=10, max_value=50, value=30, step=5)

b1, b2 = st.columns(2)
with b1:
    tombol_ambil = st.button("Ambil Berita", type="primary")
with b2:
    tombol_contoh = st.button("Pakai data contoh (offline)")

if tombol_ambil:
    with st.spinner("Mengambil berita dari NewsAPI..."):
        try:
            hasil = ambil_berita(pilihan, topik, jumlah)
            if len(hasil) == 0:
                st.warning("Tidak ada berita yang ditemukan. Coba topik lain atau kosongkan topiknya.")
            else:
                st.session_state["berita"] = hasil
                st.session_state["sumber"] = "NewsAPI - " + pilihan
                if topik.strip() != "":
                    st.session_state["sumber"] = st.session_state["sumber"] + " (topik: " + topik.strip() + ")"
                st.session_state["hasil_ai"]["tren"] = None
                st.success("Berhasil mengambil " + str(len(hasil)) + " berita hanya dengan 1 request.")
        except Exception as e:
            st.error("Gagal mengambil data dari NewsAPI. Cek koneksi internet dan API key di secrets.toml.")
            st.caption("Detail error: " + str(e)[:200])
            st.info("Coba lagi sebentar, atau klik 'Pakai data contoh' supaya tetap bisa dicoba.")

if tombol_contoh:
    st.session_state["berita"] = berita_contoh()
    st.session_state["sumber"] = "Data contoh"
    st.session_state["hasil_ai"]["tren"] = None
    st.toast("Data contoh dipakai")

berita = st.session_state["berita"]

if len(berita) == 0:
    st.caption("Belum ada berita. Klik tombol Ambil Berita dulu ya.")
else:
    st.markdown("---")
    st.subheader("Sekilas hari ini")
    if st.session_state["sumber"] == "Data contoh":
        st.caption("Sedang memakai data contoh (bukan berita asli hari ini).")

    urut_waktu = merge_sort(berita, "waktu")       
    per_sumber = hitung_sumber(berita)

    semua_sumber = set()
    semua_penulis = set()
    for b in berita:
        semua_sumber.add(b["sumber"])
        if b["penulis"] != "-":
            semua_penulis.add(b["penulis"])

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Jumlah berita", len(berita))
    m2.metric("Jumlah sumber media", len(semua_sumber))
    m3.metric("Jumlah penulis", len(semua_penulis))
    m4.metric("Sumber terbanyak", per_sumber[0]["sumber"], str(per_sumber[0]["jumlah"]) + " berita", delta_color="off")

    st.write("**5 berita paling baru**")
    st.dataframe(jadi_tabel(urut_waktu[:5]),
                 column_config={"link": st.column_config.LinkColumn("link", display_text="buka")})

    if st.button("Lanjut: Cari Berita"):
        st.switch_page("pages/1_Cari_Berita.py")