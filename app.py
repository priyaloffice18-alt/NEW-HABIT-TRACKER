import streamlit as st
import pandas as pd
import datetime
import os

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Smart Habit Tracker", layout="wide")

FILE = "habits.csv"

# -----------------------------
# LOAD DATA
# -----------------------------
def load_data():
    if os.path.exists(FILE):
        return pd.read_csv(FILE)
    return pd.DataFrame(columns=[
        "ID", "Activity", "Date", "Time", "Duration", "Completed"
    ])

def save_data(df):
    df.to_csv(FILE, index=False)

df = load_data()

if "df" not in st.session_state:
    st.session_state.df = df

# -----------------------------
# TITLE
# -----------------------------
st.title("🧠 Smart Habit Tracker (Add / Edit / Delete / Save)")

# -----------------------------
# ADD NEW ACTIVITY
# -----------------------------
st.subheader("➕ Add New Activity")

with st.form("add_form"):
    col1, col2, col3 = st.columns(3)

    activity = col1.text_input("Activity Name")
    date = col2.date_input("Date", datetime.date.today())
    time = col3.time_input("Time")

    duration = st.number_input("Duration (minutes)", 1, 600, 30)

    submit = st.form_submit_button("Add Activity")

    if submit and activity:
        new_id = len(st.session_state.df) + 1

        new_row = {
            "ID": new_id,
            "Activity": activity,
            "Date": str(date),
            "Time": str(time),
            "Duration": duration,
            "Completed": False
        }

        st.session_state.df = pd.concat(
            [st.session_state.df, pd.DataFrame([new_row])],
            ignore_index=True
        )

        save_data(st.session_state.df)
        st.success("Activity Added Successfully!")

# -----------------------------
# EDIT / DELETE SECTION
# -----------------------------
st.subheader("✏️ Manage Activities")

df = st.session_state.df

if not df.empty:

    for i, row in df.iterrows():

        st.markdown("---")

        col1, col2, col3, col4 = st.columns([3,2,2,2])

        with col1:
            new_activity = st.text_input(
                "Activity",
                value=row["Activity"],
                key=f"act_{i}"
            )

        with col2:
            new_date = st.date_input(
                "Date",
                value=pd.to_datetime(row["Date"]),
                key=f"date_{i}"
            )

        with col3:
            new_time = st.time_input(
                "Time",
                value=datetime.datetime.strptime(row["Time"], "%H:%M:%S").time(),
                key=f"time_{i}"
            )

        with col4:
            completed = st.checkbox(
                "Done",
                value=bool(row["Completed"]),
                key=f"done_{i}"
            )

        colA, colB = st.columns(2)

        with colA:
            if st.button("💾 Update", key=f"update_{i}"):

                st.session_state.df.at[i, "Activity"] = new_activity
                st.session_state.df.at[i, "Date"] = str(new_date)
                st.session_state.df.at[i, "Time"] = str(new_time)
                st.session_state.df.at[i, "Completed"] = completed

                save_data(st.session_state.df)
                st.success("Updated Successfully!")

        with colB:
            if st.button("🗑 Delete", key=f"delete_{i}"):

                st.session_state.df = st.session_state.df.drop(i).reset_index(drop=True)
                save_data(st.session_state.df)
                st.warning("Deleted Successfully!")
                st.rerun()

# -----------------------------
# VIEW ALL (SORTED)
# -----------------------------
st.subheader("📅 All Activities (Chronological)")

if not st.session_state.df.empty:

    view = st.session_state.df.copy()
    view["DateTime"] = pd.to_datetime(view["Date"] + " " + view["Time"])
    view = view.sort_values("DateTime")

    st.dataframe(view, use_container_width=True)

# -----------------------------
# SIMPLE PROGRESS
# -----------------------------
st.subheader("📊 Progress Overview")

if not st.session_state.df.empty:

    progress = st.session_state.df.copy()
    progress["Completed"] = progress["Completed"].astype(int)

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Tasks", len(progress))

    with col2:
        st.metric("Completed", progress["Completed"].sum())

# -----------------------------
# SAVE BUTTON (EXTRA SAFETY)
# -----------------------------
st.subheader("💾 Save Data")

if st.button("Save All Changes"):
    save_data(st.session_state.df)
    st.success("All data saved successfully!")
