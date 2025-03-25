import requests
import os
import urllib3
import time
import polars as pl
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime
from polars import col

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv(override=True)

db_activities = pl.read_database_uri(query="select * from activities order by start_date_local", uri=os.getenv("SUPABASE_URI"))

# streamlit app design
st.set_page_config(page_title="strava anti-stats", layout="wide")

left_img, mid_img, right_img = st.columns(3)
with mid_img:
    st.image("/home/lazaro/stravalit/strava-anti-stats-25-03-2025.png")

tagline, author_notes = st.columns(spec=[0.55, 0.45], gap="medium", vertical_alignment="top")
tagline.markdown("# anti-stats: the chocolate teapots of statistical analysis")
author_notes.markdown("""### Made by Lazaro Nimer: funemployed [hobby jogger](https://www.strava.com/athletes/25016671) and [data analyst](https://github.com/lzdnimer)""")

with st.container():
    st.markdown("#### *VO2 Max. Lactate threshold. Aerobic Capacity.* If you've succumbed to the pressure of running _(thanks, social media!)_, it's likely you're "
    "just as much on Strava as you are on Instagram. If so, you've probably spent a fair amount of time reviewing your activities ... ")