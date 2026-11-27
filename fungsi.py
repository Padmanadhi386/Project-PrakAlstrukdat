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
# === Bagian Mikeyy === 

# === Bagian Padmir ===

# === Bagian livirr ===