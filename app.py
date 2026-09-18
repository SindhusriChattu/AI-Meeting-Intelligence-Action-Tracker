import streamlit as st
from datetime import date

from database import (
    init_db, add_meeting, add_action_items,
    get_all_meetings, get_action_items, update_status,
)
from ingestion import clean_transcript
from chains import summarize_transcript, extract_action_items

st.set_page_config(page_title="AI Meeting Intelligence & Action Tracker", layout="wide")
init_db()

st.title("🗂️ AI Meeting Intelligence & Action Tracker")

tab1, tab2 = st.tabs(["Upload Meeting", "Action Item Dashboard"])

with tab1:
    st.subheader("Upload a meeting transcript")
    title = st.text_input("Meeting title", placeholder="Sprint Planning - Sept 18")
    meeting_date = st.date_input("Meeting date", value=date.today())
    uploaded_file = st.file_uploader("Transcript file (.txt)", type=["txt"])
    pasted_text = st.text_area("...or paste transcript text here", height=200)

    if st.button("Process Meeting", type="primary"):
        raw_text = uploaded_file.read().decode("utf-8") if uploaded_file else pasted_text
        if not raw_text.strip():
            st.error("Upload a file or paste transcript text first.")
        elif not title.strip():
            st.error("Give the meeting a title.")
        else:
            with st.spinner("Cleaning transcript..."):
                transcript = clean_transcript(raw_text)

            with st.spinner("Summarizing meeting..."):
                summary = summarize_transcript(transcript)

            with st.spinner("Extracting action items..."):
                items = extract_action_items(transcript)

            meeting_id = add_meeting(title, str(meeting_date), summary)
            if items:
                add_action_items(meeting_id, items)

            st.success(f"Processed! Found {len(items)} action item(s).")
            st.markdown("### Summary")
            st.write(summary)
            st.markdown("### Action Items")
            for item in items:
                st.markdown(
                    f"- **{item['task']}** — {item['owner']} "
                    f"(Due: {item['deadline']}, Priority: {item['priority']})"
                )

with tab2:
    st.subheader("All Action Items")
    status_filter = st.selectbox("Filter by status", ["all", "pending", "done"])
    filter_arg = None if status_filter == "all" else status_filter
    items = get_action_items(status=filter_arg)

    if not items:
        st.info("No action items yet — process a meeting in the Upload tab first.")
    else:
        for item in items:
            col1, col2, col3 = st.columns([5, 2, 1])
            with col1:
                label = f"**{item['task']}**  \n_{item['meeting_title']}_"
                st.markdown(label)
            with col2:
                st.write(f"{item['owner']} · Due {item['deadline']} · {item['priority']}")
            with col3:
                done = st.checkbox("Done", value=(item["status"] == "done"), key=f"chk_{item['id']}")
                if done and item["status"] != "done":
                    update_status(item["id"], "done")
                    st.rerun()
                elif not done and item["status"] == "done":
                    update_status(item["id"], "pending")
                    st.rerun()

    st.divider()
    st.subheader("Meeting History")
    for m in get_all_meetings():
        with st.expander(f"{m['title']} — {m['date']}"):
            st.write(m["summary"])
