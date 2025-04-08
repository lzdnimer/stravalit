import streamlit as st

pages = {
    "strava anti-stats": [
        st.Page("strava_streamlit.py", title="charts"),
        st.Page("notes.py", title="notes"),
    ]
}

pg = st.navigation(pages)
pg.run()