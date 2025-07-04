import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime

# === Supabase Config ===
url = "https://tsvnbavjnqwwzqmiggpp.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRzdm5iYXZqbnF3d3pxbWlnZ3BwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE1MjUzNzksImV4cCI6MjA2NzEwMTM3OX0.thXYO7100gVM0bMkpmInB9vIiPAhtnELUO2TbnYqBAw"
supabase: Client = create_client(url, key)

# === Target URLs with order priority ===
video_urls = [
    "https://tv.garden/ca/NrTK4ahuPqgFRE",
    "https://tv.garden/ph/k6kILJ1P88D8yy",
    "https://tv.garden/ph/RhkfgHInexT7iQ",
    "https://tv.garden/ge/tB7WZ5Zyx0f84V",
    "https://tv.garden/id/M7YUqwqX3olagu"
]

# === Prewritten findings
findings_text = {
    "https://tv.garden/ca/NrTK4ahuPqgFRE": """
- Script ran 12 times (12-hour span), but one log is missing. I should've considered this error
- There is one instance where the status is marked as DOWN, but both the previous and upcoming times are UP — making it questionable. I might need to include a screenshot for manual verification in such cases.
""",
    "https://tv.garden/ph/k6kILJ1P88D8yy": "It seems that this channel operates only from 10 AM to 10 PM.",
    "https://tv.garden/ph/RhkfgHInexT7iQ": "Nothing is questionable here for me",
    "https://tv.garden/ge/tB7WZ5Zyx0f84V": "There is one instance where the status is marked as DOWN, but both the previous and upcoming times are UP — making it questionable. I might need to include a screenshot for manual verification in such cases.",
    "https://tv.garden/id/M7YUqwqX3olagu": "Nothing is questionable here for me"
}

# === Query Supabase ===
def get_video_status_by_url():
    response = supabase.table("video_status").select("*").in_("url", video_urls).execute()
    data = response.data
    df = pd.DataFrame(data)

    if df.empty:
        return {}

    df["sort_time"] = df["timestamp"].apply(
        lambda ts: datetime.strptime(ts, "%b. %d, %Y - %I:%M %p")
    )
    df = df.sort_values(by=["sort_time"], ascending=False)

    grouped = {
        url: df[df["url"] == url][["Channel", "timestamp", "status"]]
        for url in video_urls
        if url in df["url"].values
    }

    return grouped

# === Streamlit App ===
st.header("Automated Health Check System for 24-Hour Video Stream Monitoring")

grouped_data = get_video_status_by_url()

if not grouped_data:
    st.warning("No data found in Supabase.")
else:
    for i, (url, table) in enumerate(grouped_data.items()):
        channel = table["Channel"].iloc[0] if "Channel" in table.columns and not table["Channel"].isnull().all() else "Unknown Channel"

        st.subheader(channel)
        st.caption(url)

        df_display = table[["timestamp", "status"]].reset_index(drop=True)
        df_display.index += 1
        st.dataframe(df_display, use_container_width=True)

        st.markdown("**Findings:**")
        if i == 0:
            st.markdown(findings_text.get(url, "_No findings provided._"))
        else:
            st.markdown(f"- {findings_text.get(url, '_No findings provided._')}")
        st.markdown("---")
