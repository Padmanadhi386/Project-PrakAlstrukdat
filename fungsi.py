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

