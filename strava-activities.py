from dotenv import load_dotenv
import requests
import os
import urllib3
from datetime import datetime
import polars as pl
from polars import col

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv(override=True)

latest_keys = pl.read_database_uri(query="select * from oauth_keys order by id desc limit 1", uri=os.getenv("SUPABASE_URI"))
access_key = latest_keys["access_token"][0]
activities_url = "https://www.strava.com/api/v3/athlete/activities"
header = {'Authorization': 'Bearer ' + access_key}
param = {'per_page': 10, 'page': 1}
strava = requests.get(activities_url, headers=header, params=param).json()

# most recent activities from strava
api_activities = pl.DataFrame(strava).select([
    col("id").alias("activity_id"),
    "start_date_local",
    col("name").alias("activity_name"),
    "distance",
    "moving_time",
    "elapsed_time",
    "total_elevation_gain",
    col("type").alias("activity_type"),
    "kudos_count",
    "comment_count",
    "photo_count",
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

# ran once to add initial data into table 
# df.write_database(table_name="activities",  connection=os.getenv("SUPABASE_URI"), if_table_exists="append")

db_activities = pl.read_database_uri(query="select * from activities order by start_date_local", uri=os.getenv("SUPABASE_URI"))

# performing an anti join on the data from Strava's API and the data from Supabase
delta_activities = api_activities.join(db_activities, on="activity_id", how="anti")

if len(delta_activities) != 0:
    delta_activities.write_database(table_name="activities", connection=os.getenv("SUPABASE_URI"), if_table_exists="append")

