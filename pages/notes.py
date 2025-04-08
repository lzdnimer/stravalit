import streamlit as st

st.page_link("pages/strava_streamlit.py", label="back to the charts", icon="📊")

lcol0, rcol0 = st.columns([0.4, 0.6], vertical_alignment="center")

with lcol0:
    st.image("strava-anti-stats-25-03-2025.png")
with rcol0:
    st.markdown("This is a simple Extract Transform Load (ETL) project which automates the process of taking my Strava data, performing a few light transformations/aggregations, and visualising my analysis.")
    st.markdown("I started this project to try and come up with stupid ways to analyse my own data, and to ensure my data skills don't atrophy while [funemployed here in Melbourne](https://www.linkedin.com/posts/lazaronimer1798_after-3-years-of-working-in-fcc-data-analytics-activity-7294544600336125952-f10S?utm_source=share&utm_medium=member_desktop&rcm=ACoAACR9vN8B5dpVHTueFtpOF5Df_XDNkXY9e80). I also wanted to work on a project that covered the ETL process from source to target.")
    st.markdown("I'm pretty happy with where my project is at, but I'd love feedback on my code, the charts, anything! Feel free to send a message on [LinkedIn](https://www.linkedin.com/in/lazaronimer1798/).")

st.divider()

st.markdown("""## :robot_face: Tech used
* Python and [Polars](https://pola.rs/): Used to poll Strava's API, transform & aggregate the data, then load it to Supabase. I use Polars rather than Pandas ~~because I want to be different~~ because the syntax is simple and is [more performant](https://blog.jetbrains.com/pycharm/2024/07/polars-vs-pandas/) when working with larger datasets.
* [Supabase](https://supabase.com/): I needed a platform to host my database and Supabase was perfect as it's free for the duration of my project and uses PostgreSQL. Connecting to the database is also super easy.
* [Streamlit](https://streamlit.io/): I wanted to make my project accessible and not hidden in a GitHub repo and I'm so glad I found Streamlit. I was hesitant at first as learning a new tool can often take time, but Streamlit's docs made picking up the syntax a walk in the park.
* [GitHub Actions](https://github.com/features/actions): I wanted to automate the process of updating the data presented on Streamlit and GitHub Actions worked well as it connected directly to my repository. There was definitely a bigger learning curve here compared to the other tools in this list, especially with the construction of the `.yaml` file needed to set up automation, and figuring out how to handle environment secrets.""")

st.divider()
st.markdown("## :repeat: ETL")
lcol1, mcol1, rcol1 = st.columns([0.2, 0.8, 0.2])
with mcol1:
    st.image("streamlit_etl.png", caption="ETL flow for my project")
st.markdown("""### Extract
This project uses my activity data which I access through Strava's API. After creating an app on Strava, I got an access key which I used in all my requests for data. This access key expires after 6 hours, and I have to use a refresh key to get a new access key.
            
My script checks if the access key has expired - if so, it POSTs a request for a new access key. Access token responses are loaded directly to Supabase.

### Transform
Once the data is retrieved, I make a few light transformations and aggregations, including:
* Filtering and renaming some columns
* Converting the `distance` column from metres to kilometres
* Casting the `start_date_local` column to a date column
* Creating a cumulative sum column for `elevation_gain` and a 7-day rolling window for `distance`

### Load
Data is then loaded into Supabase for storage, and charts are presented on Streamlit. Using GitHub Actions, I run this process every 15 minutes.""")

st.divider()
st.markdown("## :computer: Schema Design")

lcol2, mcol2, rcol2 = st.columns([0.2, 0.8, 0.2])
with mcol2:
    st.image("schema.png", caption="tables used for the project")
st.markdown("""I only needed 3 tables here:

1. `interactions`: stores kudos and comment counts. As these are slowly changing dimensions, I wanted these columns to be stored in a separate table from activities. `activity_id` here is a foreign key and references the `activities` table.
2. `activities`: where all other data related to an activity is stored. `activity_id` is the primary key.
3. `oauth_keys`: where my access and refresh keys are stored, along with the epoch value representing when the latest access key will expire.
            
### Loading data to tables
I ran a full load onto my Supabase DB the first time (to store any activities I recorded before the project). Any activities after that are then incrementally loaded.
            
For the `interactions` table, I get the most recent data from Strava's API and upsert any new changes via Supabase's API. For the `activities` table, I used an anti-join on my `activities` table in my Supabase DB and the latest activities gained from Strava's API to end up with a delta table of activities that are not yet in my Supabase DB.""")

st.divider()
st.markdown("## :building_construction: WIP")
st.markdown("""I'm pretty happy with where I'm at with this project (if I do say so myself), but here's a few things I want to add over time:

1. Enabling other Strava users to get their own charts - will do this once I wrap my head around oauth fully!
2. Webhook service - rather than polling the API every 15 minutes, I think a webhook would work better. Probably overkill, but good to learn.

Again, feedback always welcome :sunglasses:""")

st.divider()
st.markdown("## :books: Resources")
st.markdown("""If this has inspired you to start your own project using Strava's API, firstly, you're welcome. Secondly, use these links to get started:

* [My project repo](https://github.com/lzdnimer/stravalit): fork this repo!
* [Jessica Salbert - Holding your hand through Strava's API](https://jessicasalbert.medium.com/holding-your-hand-through-stravas-api-e642d15695f2): the best guide I found on using Strava's API and handling access/refresh tokens.
* [Tyler Richards' Goodreads Streamlit App](https://goodreads.streamlit.app/?ref=streamlit-io-gallery-data-visualization): I pretty much stole their Streamlit design - their github repo is a great resource. 
* [Polars](https://docs.pola.rs/) and [Streamlit](https://docs.streamlit.io/): very user-friendly docs.
""")