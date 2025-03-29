import requests
import os
import urllib3
import json
import time
import polars as pl
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime
from polars import col
from supabase import create_client

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv(override=True)

# if the access key has expired, run the strava_keys script to get a new one
epoch = time.time()
latest_keys = pl.read_database_uri(query="select * from oauth_keys order by id desc limit 1", uri=os.getenv("SUPABASE_URI"))
expires_at = latest_keys["expires_at"][0]
auth_url = "https://www.strava.com/oauth/token"

if epoch > expires_at:
    refresh_token = latest_keys["refresh_token"][0]
    payload = {
        'client_id': os.getenv("CLIENT_ID"),
        'client_secret': os.getenv("CLIENT_SECRET"),
        'refresh_token': refresh_token,
        'grant_type': "refresh_token",
        'f': 'json'
    }

    refresh_req = requests.post(auth_url, data=payload, verify=False).json()
    df = pl.DataFrame(
        {"access_token": refresh_req["access_token"],
        "refresh_token": refresh_req["refresh_token"],
        "expires_at": refresh_req["expires_at"]
        })
    
    df.write_database(table_name="oauth_keys",  connection=os.getenv("SUPABASE_URI"), if_table_exists="append")
    latest_keys = pl.read_database_uri(query="select * from oauth_keys order by id desc limit 1", uri=os.getenv("SUPABASE_URI"))
    access_key = latest_keys["access_token"][0]

# get the most recent 10 activities from Strava, and update the database with any new activities
# I requested 10 only because the cron job runs every 15 minutes anyways
activities_url = "https://www.strava.com/api/v3/athlete/activities"
access_key = latest_keys["access_token"][0]
header = {'Authorization': 'Bearer ' + access_key}
param = {'per_page': 200, 'page': 1}
strava = requests.get(activities_url, headers=header, params=param).json()
latest_activities = pl.DataFrame(strava).select([
    col("id").alias("activity_id"),
    "start_date_local",
    col("name").alias("activity_name"),
    "distance",
    "moving_time",
    "elapsed_time",
    "total_elevation_gain",
    col("type").alias("activity_type"),
    "average_speed",
    "max_speed",
    "average_heartrate",
    "max_heartrate",
    "elev_high",
    "elev_low"
    ]).with_columns(
        col("distance").cast(pl.Float32) / 1000,
        col("start_date_local").cast(pl.Datetime).cast(pl.Date),
        ).filter((col("start_date_local") >= datetime(2025, 1, 1))).sort("start_date_local")

# ran once to add initial data into activities table 
# latest_activities.write_database(table_name="activities",  connection=os.getenv("SUPABASE_URI"), if_table_exists="replace")

# I want the activites table to be static, with the interactions table dynamic as kudos/comments/photos count may change over time
interactions = pl.DataFrame(strava).select([
    col("id").alias("activity_id"),
    "start_date_local",
    "kudos_count",
    "comment_count",
    ]).with_columns(
        col("start_date_local").cast(pl.Datetime).cast(pl.Date),
        last_update=datetime.now()
            ).filter((col("start_date_local") >= datetime(2025, 1, 1))).sort("start_date_local")

# ran once to add initial data into interactions table 
# interactions.write_database(table_name="interactions",  connection=os.getenv("SUPABASE_URI"), if_table_exists="replace")


# performing an anti join on the data from Strava's API and the data from Supabase

db_activities = pl.read_database_uri(query="select * from activities order by start_date_local", uri=os.getenv("SUPABASE_URI"))
delta_activities = latest_activities.join(db_activities, on="activity_id", how="anti")
if len(delta_activities) != 0:
    delta_activities.write_database(table_name="activities", connection=os.getenv("SUPABASE_URI"), if_table_exists="append")

db_interactions = pl.read_database_uri(query="select * from interactions order by start_date_local", uri=os.getenv("SUPABASE_URI"))
delta_interactions = interactions.join(db_interactions, on="activity_id", how="anti")
if len(delta_interactions) != 0:
    delta_interactions.write_database(table_name="interactions", connection=os.getenv("SUPABASE_URI"), if_table_exists="append")

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
interactions_json = json.loads(interactions.write_json())
response = supabase.table("interactions").upsert(interactions_json, on_conflict=["activity_id"]).execute()
