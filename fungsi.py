import json
import re

import pandas as pd
import requests
import streamlit as st
import google.generativeai as genai

URL_HN = "https://hacker-news.firebaseio.com/v0"


DAFTAR_BERITA = {
    "Paling populer": "topstories",
    "Paling baru": "newstories",
    "Terbaik": "beststories",
}