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
    cumulative_elevation_gain=pl.col("total_elevation_gain").cum_sum())

cumu_max = df.select(col("cumulative_elevation_gain")).max()["cumulative_elevation_gain"][0]
kudos_chart = get_db_data().filter(pl.col("activity_type").is_in(["Run", "Hike", "Walk"]))
total_kudos = df.select(col("kudos_count").sum())
last_kudos = df.sql("select kudos_count from self order by start_date_local desc limit 1")
recent_kudos = df.sql("select start_date_local, kudos_count from self order by start_date_local desc limit 2")
today_kudos = recent_kudos["kudos_count"][0]

print(recent_kudos)