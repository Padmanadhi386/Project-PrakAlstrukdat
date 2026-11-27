import hashlib
import html
import json
import re
from datetime import datetime
 
import pandas as pd
import requests
import streamlit as st

URL_NEWSAPI = "https://newsapi.org/v2"
URL_GEMINI = "https://generativelanguage.googleapis.com/v1beta/models/"

# model cadangan jika model utama sibukk
MODEL_CADANGAN = "gemini-3.5-flash-lite"
FILE_AKUN = "data/akun.json"
FILE_RIWAYAT = "data/riwayat.json"


DAFTAR_BERITA = {
    "Berita utama teknologi": {"endpoint": "top-headlines", "urut": ""},
    "Paling baru": {"endpoint": "everything", "urut": "publishedAt"},
    "Paling populer": {"endpoint": "everything", "urut": "popularity"},
}

STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with", "at",
    "by", "from", "is", "are", "was", "be", "it", "its", "this", "that", "you",
    "your", "we", "our", "i", "my", "how", "what", "why", "when", "who", "can",
    "will", "not", "no", "do", "does", "has", "have", "about", "into", "over",
    "after", "than", "as", "new", "now", "all", "via", "vs", "using", "use",
    "just", "more", "one", "two", "get", "says", "said", "could", "would",
    "like", "again", "still", "every", "some", "other", "out", "up", "so",
    "here", "there", "they", "their", "s", "he", "she", "his", "her", "first",
    "yang", "dan", "di", "ke", "dari", "untuk", "dengan", "ini", "itu",
}

# === Bagian livirr ===
def siapkan_session():
    if "login" not in st.session_state:
        st.session_state["login"] = None         
    if "berita" not in st.session_state:
        st.session_state["berita"] = []          
    if "cache" not in st.session_state:
        st.session_state["cache"] = {}           
    if "riwayat" not in st.session_state:
        st.session_state["riwayat"] = []         
    if "antrean" not in st.session_state:
        st.session_state["antrean"] = []         
    if "hasil_ai" not in st.session_state:
        st.session_state["hasil_ai"] = {"tren": None, "ringkasan": [], "istilah": []}
    if "sumber" not in st.session_state:
        st.session_state["sumber"] = ""

def acak_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def baca_akun():
    try:
        with open(FILE_AKUN, "r") as datafile:
            return json.load(datafile)
    except FileNotFoundError:
        return {}

def simpan_akun(akun):
    with open(FILE_AKUN, "w") as datafile:
        json.dump(akun, datafile, indent=2)
 
 
def cek_login(username, password):
    akun = baca_akun()
    username = username.strip().lower()
    if username in akun and akun[username]["password"] == acak_password(password):
        return True
    return False

def daftar_akun(username, nama, password):
    akun = baca_akun()
    username = username.strip().lower()
    if len(username) < 3:
        return "Username minimal 3 huruf."
    if not username.isalnum():
        return "Username hanya boleh huruf dan angka."
    if username in akun:
        return "Username sudah dipakai, coba yang lain."
    if len(password) < 6:
        return "Password minimal 6 karakter."
    akun[username] = {"nama": nama.strip() or username, "password": acak_password(password)}
    simpan_akun(akun)
    return None
 
 
def baca_semua_riwayat():
    try:
        with open(FILE_RIWAYAT, "r") as datafile:
            return json.load(datafile)
    except FileNotFoundError:
        return {}
 
 
def simpan_riwayat(username, riwayat):
    semua = baca_semua_riwayat()
    semua[username] = riwayat[-20:]
    with open(FILE_RIWAYAT, "w") as datafile:
        json.dump(semua, datafile, indent=2)
 
 
def masuk(username):
    username = username.strip().lower()
    st.session_state["login"] = username
    st.session_state["riwayat"] = baca_semua_riwayat().get(username, [])
    if "aktif" in st.session_state:
        del st.session_state["aktif"]
 
 
def keluar():
    for kunci in list(st.session_state.keys()):
        del st.session_state[kunci]
    siapkan_session()
 
 
def wajib_login():
    siapkan_session()
    if st.session_state["login"] is None:
        st.switch_page("pages/0_Login.py")
    kiri, kanan = st.columns([5, 1])
    with kiri:
        st.caption("Login sebagai **" + st.session_state["login"] + "**")
    with kanan:
        if st.button("Logout"):
            keluar()
            st.switch_page("pages/0_Login.py")

# === Bagian mikey ===
def ambil_api_key():
    try:
        return st.secrets["NEWSAPI_KEY"]
    except Exception:
        return None
 
 
def ambil_dari_newsapi(jenis, topik, jumlah):
    pengaturan = DAFTAR_BERITA[jenis]
    if pengaturan["endpoint"] == "top-headlines":
        parameter = {"category": "technology", "country": "us", "pageSize": jumlah}
        if topik != "":
            parameter["q"] = topik
    else:
        if topik == "":
            topik = "technology"
        parameter = {"q": topik, "language": "en", "sortBy": pengaturan["urut"], "pageSize": jumlah}
    kunci_cache = jenis + "|" + topik + "|" + str(jumlah)
    cache = st.session_state["cache"]
    if kunci_cache in cache:
        return cache[kunci_cache]
 
    api_key = ambil_api_key()
    if api_key is None:
        raise Exception("API key NewsAPI belum diisi di secrets.toml (NEWSAPI_KEY).")
 
    url = URL_NEWSAPI + "/" + pengaturan["endpoint"]
    response = requests.get(url, params=parameter, headers={"X-Api-Key": api_key}, timeout=10)
    data = response.json()
    if response.status_code != 200 or data.get("status") != "ok":
        raise Exception(data.get("code", "error") + ": " + data.get("message", "status " + str(response.status_code)))
 
    cache[kunci_cache] = data["articles"]
    return data["articles"]
 
 
def ubah_waktu(teks):
    try:
        teks = teks.replace("Z", "+00:00")
        return int(datetime.fromisoformat(teks).timestamp())
    except Exception:
        return 0
 
 
def rapikan_berita(data, nomor):
    if data is None or not data.get("title") or data["title"] == "[Removed]":
        return None
    judul = data["title"]
    sumber = (data.get("source") or {}).get("name") or "-"
    if judul.endswith(" - " + sumber):
        judul = judul[:-len(" - " + sumber)]
    return {
        "id": nomor,
        "judul": judul,
        "sumber": sumber,
        "penulis": data.get("author") or "-",
        "deskripsi": data.get("description") or "",
        "isi": data.get("content") or "",
        "waktu": ubah_waktu(data.get("publishedAt", "")),
        "link": data.get("url", ""),
    }
 
def olah_artikel(daftar_artikel):
    hasil = []
    sudah_ada = set()           
    for artikel in daftar_artikel:
        berita = rapikan_berita(artikel, len(hasil) + 1)
        if berita is not None and berita["judul"].lower() not in sudah_ada:
            sudah_ada.add(berita["judul"].lower())
            hasil.append(berita)
    return hasil
 
 
def ambil_berita(jenis, topik, jumlah):
    return olah_artikel(ambil_dari_newsapi(jenis, topik.strip(), jumlah))
 
 
def berita_contoh():
    with open("data/contoh_berita.json", "r") as datafile:
        data = json.load(datafile)
    return olah_artikel(data["articles"])
 
 
def jadi_tabel(daftar_berita):
    df = pd.DataFrame(daftar_berita)
    if len(df) == 0:
        return df
    df["terbit (WIB)"] = pd.to_datetime(df["waktu"], unit="s") + pd.Timedelta(hours=7)
    df["terbit (WIB)"] = df["terbit (WIB)"].dt.strftime("%d-%m %H:%M")
    df.index = range(1, len(df) + 1)     
    return df[["judul", "sumber", "penulis", "terbit (WIB)", "link"]]
 
def merge_sort(data, kunci, menurun=True):
    if len(data) <= 1:
        return data
    tengah = len(data) // 2
    kiri = merge_sort(data[:tengah], kunci, menurun)
    kanan = merge_sort(data[tengah:], kunci, menurun)
    return merge(kiri, kanan, kunci, menurun)
 
 
def nilai(item, kunci):
    if isinstance(item[kunci], str):
        return item[kunci].lower()
    return item[kunci]
 
 
def merge(kiri, kanan, kunci, menurun=True):
    hasil = []
    i = 0
    j = 0
    while i < len(kiri) and j < len(kanan):
        if menurun:
            kiri_duluan = nilai(kiri[i], kunci) >= nilai(kanan[j], kunci)
        else:
            kiri_duluan = nilai(kiri[i], kunci) <= nilai(kanan[j], kunci)
        if kiri_duluan:
            hasil.append(kiri[i])
            i = i + 1
        else:
            hasil.append(kanan[j])
            j = j + 1
    hasil = hasil + kiri[i:] + kanan[j:]
    return hasil

def bersihkan(teks):
    teks = teks.lower()
    for tanda in ",.:;!?()[]\"'|/‘’“”":
        teks = teks.replace(tanda, " ")
    return teks
 
def linear_search(data, kata_kunci, cek_deskripsi=False):
    dicari = " " + kata_kunci.lower().strip() + " "
    hasil = []
    for berita in data:
        teks = berita["judul"]
        if cek_deskripsi:
            teks = teks + " " + berita["deskripsi"]
        teks = " " + bersihkan(teks) + " "
        if dicari in teks:
            hasil.append(berita)
    return hasil

def hitung_sumber(daftar_berita):
    jumlah = {}
    for berita in daftar_berita:
        if berita["sumber"] in jumlah:
            jumlah[berita["sumber"]] = jumlah[berita["sumber"]] + 1
        else:
            jumlah[berita["sumber"]] = 1
    daftar = []
    for sumber in jumlah:
        daftar.append({"sumber": sumber, "jumlah": jumlah[sumber]})
    return merge_sort(daftar, "jumlah")