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
    month=col("start_date_local").dt.strftime("%B"))

cumu_max = df.select(col("cumulative_elevation_gain")).max()["cumulative_elevation_gain"][0]
kudos_chart = get_db_data().filter(pl.col("activity_type").is_in(["Run", "Hike", "Walk"]))
total_kudos = df.select(col("kudos_count").sum())
last_kudos = df.sql("select kudos_count from self order by start_date_local desc limit 1")
recent_kudos = df.sql("select start_date_local, kudos_count from self order by start_date_local desc limit 2")
today_kudos = recent_kudos["kudos_count"][0]


ddf = df.select(col("start_date_local"),col("elapsed_time"), col("moving_time"), col("month")
    ).with_columns(standing_time=col("elapsed_time")-col("moving_time")
    ).group_by(col("start_date_local").dt.month()).agg(col("elapsed_time").sum(), col("moving_time").sum(), col("standing_time").sum(), col("month").max()
    ).sort("start_date_local")

ch = pl.DataFrame(ddf).unpivot(on=['moving_time', 'standing_time'], index=['month', "start_date_local"]).sort(by="variable", descending=True
    ).with_columns(pl.when(col("variable")=="standing_time").then(pl.lit("No")).otherwise(pl.lit("Yes")).alias("Moving"))

bar = alt.Chart(ch).mark_bar().encode(
    alt.Y('month:N').sort(field='start_date_local').title("Month"),
    alt.X('value:Q').stack("normalize").title("% of time spent moving/not moving"),
    alt.Color('Moving:N', scale=alt.Scale(domain=['Yes', 'No'], range=['#ffcbb5', '#fc4c02'])),
    alt.Order('Moving:N'),
)

wk = df.filter(col("activity_type")=="Run").select(col("distance").round(0), col("start_date_local")).group_by(col("start_date_local")).agg(col("distance").sum()).with_columns(weekday=col("start_date_local").dt.strftime("%A"), weekday_num=col("start_date_local").dt.day())

# print(wk)

box = alt.Chart(wk).configure(background="white").mark_boxplot(
).configure_axis(
    labelColor="black",
    titleColor="black",
    domainColor="black",
    gridOpacity=0.2
).encode(
    alt.X("distance:Q"),
    alt.Y("weekday:N").scale(zero=False).sort(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday  ']),
    alt.Color("weekday:N").legend(None),
)

# st.altair_chart(box, theme=None)

run = df.filter(col("activity_type")=="Run").select(col("distance"), col("start_date_local")).with_columns(rolling_volume_7day=pl.col("distance").rolling_sum(7).round(2)).filter((col("rolling_volume_7day").is_not_null()))

total = df.filter(col("activity_type")=="Run").select(col("distance").sum())["distance"][0]

map = pl.scan_csv("map_coords.csv").with_columns(
    color=pl.when(total>col("distance")).then(pl.lit("#07fc03")).otherwise(pl.lit("#fc0328"))).collect()

st.map(map, size=5000, zoom=4, color="color")

next_town = map.sql(query="select name from self where distance in (select min(distance) from self where color != '#07fc03')")
print(town)