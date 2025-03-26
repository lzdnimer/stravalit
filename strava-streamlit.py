import requests
import os
import urllib3
import time
import altair as alt
import polars as pl
import streamlit as st
from millify import millify
from dotenv import load_dotenv
from datetime import datetime
from polars import col

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv(override=True)

db_df = pl.read_database_uri(query="select * from activities order by start_date_local", uri=os.getenv("SUPABASE_URI"))


# streamlit app design
st.set_page_config(page_title="strava anti-stats", layout="wide")

left_img, mid_img, right_img = st.columns(3)
with mid_img:
    st.image("/home/lazaro/stravalit/strava-anti-stats-25-03-2025.png")

left_ttl, mid_ttl, right_ttl = st.columns([0.1,0.7,0.1], vertical_alignment="center")
with mid_ttl:
    st.markdown("# anti-stats: the chocolate teapots of statistical analysis")

st.divider()

left_sub, right_sub = st.columns([0.7,0.3], vertical_alignment="center")
with left_sub:
    st.caption("""### Made by Lazaro Nimer: funemployed [hobby jogger](https://www.strava.com/athletes/25016671) and [data analyst](https://github.com/lzdnimer)""")


with st.container():
    st.markdown("#### *VO2 Max. Lactate threshold. Relative Effort.* If you've succumbed to the pressure of running _(thanks, social media!)_, it's likely you've spent a fair amount of time on Strava looking at all the fancy data linked to your activities. While all of it is useful, I wanted to see how much meaningless data could be extracted from my activities in 2025. Enjoy!")

    st.divider()
    
    cumulative_gain = db_df.select(
        col("total_elevation_gain"),col("start_date_local")
        ).with_columns(cumulative_elevation_gain=pl.col("total_elevation_gain").cum_sum())
    cumu_max = cumulative_gain.select(col("cumulative_elevation_gain")).max()["cumulative_elevation_gain"][0]

    lcol, rcol = st.columns(2)
    with lcol:
        st.line_chart(
            cumulative_gain,
            x="start_date_local",
            y="cumulative_elevation_gain",
            x_label="date",
            y_label="cumulative elevation gain 2025 (metres)",
            color="#FC5200",
            height=500)
    with rcol:
        with st.container():

            met1, met2, met3 = st.columns(3)
            with met1:
                st.metric(label="total (metres)", value=cumu_max, border=True)
            with met2:
                st.metric(label="total (bananas)", value=millify(cumu_max/0.18), border=True) # the average length of a banana is 18cm
            with met3:
                st.metric(label="total (eiffel towers)", value=round(cumu_max/330,2), border=True) # the eiffel tower is 330m
            
            st.markdown("(description of chart)")
            
    lcol1, rcol1 = st.columns(2)
    with rcol1:
        acti_list = ["Run", "Hike", "Walk"]
        acti_selection = st.pills("activity", acti_list, selection_mode="multi", label_visibility="collapsed", default="Run")
        kudos_chart = db_df.filter(pl.col("activity_type").is_in(acti_selection))
        
        st.markdown("(description of chart)")
    with lcol1:
        st.scatter_chart(kudos_chart, x="distance", y="kudos_count", color="#FC5200", height=500)

# elapsed time vs moving time