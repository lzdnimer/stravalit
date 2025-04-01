import requests
import os
import urllib3
import time
import polars as pl
import streamlit as st
from millify import millify
from dotenv import load_dotenv
from datetime import datetime
from polars import col

import streamlit as st
import altair as alt
import pydeck as pdk
from geopy.distance import geodesic as gdsc
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv(override=True)

query="" \
"select a.*, i.kudos_count, i.comment_count " \
"from activities a " \
"left join interactions i on a.activity_id = i.activity_id " \
"order by a.start_date_local"

def get_db_data():
    db_df = pl.read_database_uri(
    query=query, uri=os.getenv("SUPABASE_URI"))
    return db_df

df = get_db_data().select("*").with_columns(
    cumulative_elevation_gain=pl.col("total_elevation_gain").cum_sum(),
    month_name=col("start_date_local").dt.strftime("%B"))

cumu_max = df.select(col("cumulative_elevation_gain")).max()["cumulative_elevation_gain"][0]
kudos_chart = get_db_data().filter(pl.col("activity_type").is_in(["Run", "Hike", "Walk"]))
total_kudos = df.select(col("kudos_count").sum())
last_kudos = df.sql("select kudos_count from self order by start_date_local desc limit 1")
recent_kudos = df.sql("select start_date_local, kudos_count from self order by start_date_local desc limit 2")
today_kudos = recent_kudos["kudos_count"][0]


ddf = df.select(col("start_date_local"),col("elapsed_time"), col("moving_time"), col("month_name")
    ).with_columns(standing_time=col("elapsed_time")-col("moving_time")
    ).group_by(col("start_date_local").dt.month()).agg(col("elapsed_time").sum(), col("moving_time").sum(), col("standing_time").sum(), col("month_name").max()
    ).sort("start_date_local")

ch = pl.DataFrame(ddf).unpivot(on=['moving_time', 'standing_time'], index=['month_name', "start_date_local"]).sort(by="variable", descending=True
    ).with_columns(pl.when(col("variable")=="standing_time").then(pl.lit("No")).otherwise(pl.lit("Yes")).alias("Moving"))

bar = alt.Chart(ch).mark_bar().encode(
    alt.Y('month_name:N').sort(field='start_date_local').title("Month"),
    alt.X('value:Q').stack("normalize").title("% of time spent moving/not moving"),
    alt.Color('Moving:N', scale=alt.Scale(domain=['Yes', 'No'], range=['#ffcbb5', '#fc4c02'])),
    alt.Order('Moving:N'),
)

wk = df.select(col("distance"), col("start_date_local"), col("elapsed_time")).with_columns(wk_num=col("start_date_local").dt.week())
print(wk)