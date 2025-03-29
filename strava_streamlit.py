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

# streamlit app design
st.set_page_config(page_title="strava anti-stats", layout="wide")

query="" \
"select a.*, i.kudos_count, i.comment_count " \
"from activities a " \
"left join interactions i on a.activity_id = i.activity_id " \
"order by a.start_date_local"

@st.cache_data
def get_db_data():
    db_df = pl.read_database_uri(
    query=query, uri=os.getenv("SUPABASE_URI"))
    return db_df

df = get_db_data().select("*").with_columns(
    cumulative_elevation_gain=pl.col("total_elevation_gain").cum_sum())

left_img, mid_img, right_img = st.columns(3)
with mid_img:
    st.image("strava-anti-stats-25-03-2025.png")

left_ttl, mid_ttl, right_ttl = st.columns([0.1,0.7,0.1], vertical_alignment="center")
with mid_ttl:
    st.markdown("# anti-stats: the chocolate teapots of statistical analysis")

st.divider()

left_sub, right_sub = st.columns([0.7,0.3], vertical_alignment="center")
with left_sub:
    st.caption("""### Made by Lazaro Nimer: funemployed [hobby jogger](https://www.strava.com/athletes/25016671) and [sql monkey](https://github.com/lzdnimer)""")

st.markdown("##### *VO2 Max. Lactate Threshold. Relative Effort.* If you've succumbed to the pressure of running _(thanks, social media!)_, it's likely you've spent a fair amount of time on Strava browsing the fancy charts and analyses linked to your activities. While it's useful, I wanted to see how _useless_ my analysis could be.")
st.markdown("##### I analysed my data using [Strava's API](https://developers.strava.com/docs/reference/) to create _anti-stats_ - statistics that bear no relevance on athlete performance. Sure, VO2 Max may predict your race times, but wouldn't you want to know how to get more kudos instead?")

st.divider()

st.markdown("## cumulative gain - all activities")

cumu_max = df.select(col("cumulative_elevation_gain")).max()["cumulative_elevation_gain"][0]

lcol, rcol = st.columns(2)
with lcol:
    st.line_chart(
        df,
        x="start_date_local",
        y="cumulative_elevation_gain",
        x_label="date",
        y_label="cumulative elevation gain 2025 (metres)",
        color="#FC5200",
        height=500)
with rcol:
    with st.container():

        st.metric(label="total (metres)", value=round(cumu_max,2), border=True)

        met1, met2, met3 = st.columns(3)
        with met1:
            st.metric(label="total (bananas)", value=millify(cumu_max/0.18), border=True) # the average length of a banana is 18cm
        with met2:
            st.metric(label="total (eiffel towers)", value=round(cumu_max/330,2), border=True) # the eiffel tower is 330m
        with met3:
            st.metric(label="total (mt. everests)", value=round(cumu_max/8850,2), border=True)
        
        st.markdown("This chart tracks the total amount of elevation gained across all activities.")
        st.markdown("More importantly, this shows the equivalent of the height I climbed using the average length of a banana, plus the height of the Eiffel Tower and Mount Everest for scale.")

st.markdown("## distance vs. kudos count")

lcol1, rcol1 = st.columns(2)
with rcol1:
    met4, met5, met6 = st.columns([0.3,0.2,0.5])
    with met4:
        acti_list = ["Run", "Hike", "Walk"]
        acti_selection = st.pills("activity", acti_list, selection_mode="multi", label_visibility="collapsed", default="Run")
        kudos_chart = get_db_data().filter(pl.col("activity_type").is_in(acti_selection))
    with met5:
        total_kudos = df.select(col("kudos_count").sum())
        last_kudos = df.sql("select kudos_count from self order by start_date_local desc limit 1")
        st.metric(label="total kudos", value=total_kudos, border=True)
    with met6:
        recent_kudos = df.sql("select start_date_local, kudos_count from self order by start_date_local desc limit 2")
        today_kudos = recent_kudos["kudos_count"][0]

        if today_kudos - recent_kudos["kudos_count"][1] < 0:
            delta = f"{abs(today_kudos - recent_kudos["kudos_count"][1])} fewer kudos than last activity"
            delta_colour = "inverse"
        else:
            delta = f"{abs(today_kudos - recent_kudos["kudos_count"][1])} more kudos than last activity"
            delta_colour = "normal"
        
        st.metric(label="most recent activity kudos", value=today_kudos, delta=delta, delta_color=delta_colour, border=True)
            
    corr = get_db_data().select(pl.corr("distance", "kudos_count", method="pearson"))["distance"][0]
    st.markdown(f"This scatter chart plots activities along with the kudos received for each activity. The activity type is filtered to running, walking, and hiking. If you aren't on Strava (good for you!), think of kudos as a 'like' on a post.")
    st.markdown(f"Crucially, this plot shows a generally positive relationship between the distance I ran/walked/hiked and the number of kudos received for each post, with a Pearson's correlation coefficient of `{round(corr,2)}`. As kudos is an important social currency in today's society, I intend to run a marathon every day to boost the number of kudos I have.")

with lcol1:
    st.scatter_chart(kudos_chart, x="distance", y="kudos_count", color="#FC5200", height=500)

st.markdown("## elapsed time vs. moving time")

# # elapsed time vs moving time
