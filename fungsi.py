import hashlib
import html
import json
import re
from datetime import datetime
 
import pandas as pd
import requests
import streamlit as st

import google.generativeai as genai

URL_NEWSAPI = "https://newsapi.org/v2"
URL_GEMINI = "https://generativelanguage.googleapis.com/v1beta/models/"

# model cadangan jika model utama sibukk
MODEL_CADANGAN = "gemini-3.5-flash-lite"
FILE_AKUN = "data/akun.json"
FILE_RIWAYAT = "data/riwayat.json"


DAFTAR_BERITA = {
    "Paling populer": "topstories",
    "Paling baru": "newstories",
    "Terbaik": "beststories",
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

# == padmir ==

def siapkan_gemini():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        return None
    genai.configure(api_key=api_key)
    nama_model = st.secrets.get("GEMINI_MODEL", "gemini-flash-latest")
    return genai.GenerativeModel(nama_model)

def tanya_gemini(model, prompt, format_json=False):
    batas_waktu = {"timeout": 30, "retry": None}
    pengaturan = None
    if format_json:
        pengaturan = {"response_mime_type": "application/json"}

    # coba model utama dulu, kalau gagal karena sibuk / tidak ada, coba MODEL_CADANGAN
    daftar = [model, genai.GenerativeModel(MODEL_CADANGAN)]

    pesan = ""
    for m in daftar:
        try:
            response = m.generate_content(prompt, generation_config=pengaturan,
                                          request_options=batas_waktu)
            return response.text
        except Exception as e:
            pesan = str(e)
            sibuk = ("503" in pesan or "504" in pesan or "Deadline" in pesan
                     or "timed out" in pesan.lower() or "overloaded" in pesan.lower())
            if sibuk or "404" in pesan:
                continue        # model ini sibuk / tidak ada, coba model berikutnya
            break               # error lain (kuota, API key) tidak beres dengan ganti model

    if "429" in pesan:
        st.error("Kuota Gemini untuk API key ini lagi habis (error 429). Tunggu kira-kira 1 menit, "
                 "atau kalau sudah dipakai seharian, coba lagi besok.")
    elif "404" in pesan:
        st.error("Model Gemini tidak ditemukan. Ganti GEMINI_MODEL di secrets.toml dengan model yang masih tersedia.")
    elif "API key" in pesan or "400" in pesan or "403" in pesan:
        st.error("API key Gemini tidak valid. Cek lagi isi secrets.toml.")
    else:
        st.error("Semua model Gemini sedang sibuk (error 503 dari server Google). "
                 "Tunggu 1-2 menit lalu tekan tombolnya lagi.")
    st.caption("Detail error: " + pesan[:200])
    return None


def daftar_judul_teks(daftar_berita, n=15):
    teks = ""
    for i in range(min(n, len(daftar_berita))):
        b = daftar_berita[i]
        teks = teks + str(i + 1) + ". " + b["judul"] + " (" + b["sumber"] + ")\n"
    return teks