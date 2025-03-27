import streamlit as st

pages = {
    "strava anti-stats": [
        st.Page("strava_streamlit.py", title="data visualisations"),
        st.Page("etl_page.py", title="tools used"),
        st.Page("inspo_page.py", title="inspiration/ideas I stole")
    ]
}

pg = st.navigation(pages)
pg.run()