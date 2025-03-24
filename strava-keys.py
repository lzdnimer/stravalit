from dotenv import load_dotenv
import requests
import os
import urllib3
import time
import polars as pl

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv(override=True)

auth_url = "https://www.strava.com/oauth/token"
epoch = time.time()

latest_keys = pl.read_database_uri(
    query="select * from oauth_keys order by id desc limit 1",
    uri=os.getenv("SUPABASE_URI"))

expires_at = latest_keys["expires_at"][0]

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
