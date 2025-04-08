import streamlit as st

pages = {
    "strava anti-stats": [
        st.Page("pages/strava_streamlit.py", title="charts"),
        st.Page("pages/notes.py", title="notes"),
    ]
}

pg = st.navigation(pages)
pg.run()