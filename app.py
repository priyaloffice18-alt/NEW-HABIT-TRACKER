import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import os

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Productivity Tracker", layout="wide", page_icon="📊")

# -----------------------------
# FILES
# -----------------------------
HABITS_FILE = "habits.csv"
SLEEP_FILE = "sleep.csv"
SCREEN_FILE = "screen.csv"

# -----------------------------
# LOAD DATA
# -----------------------------
def load_csv(file, cols):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame(columns=cols)

habits = load_csv(HABITS_FILE, ["Activity", "Date", "Time", "Duration", "Completed"])
sleep = load_csv(SLEEP_FILE, ["Date", "Sleep", "Wake"])
screen = load_csv(SCREEN_FILE, ["App", "Date", "Hours"])

# -----------------------------
# SAVE DATA
# -----------------------------
def save(df, file):
    df.to_csv(file, index=False)

# -----------------------------
# SESSION STATE
# -----------------------------
if "habits" not in st.session_state:
    st.session_state.habits = habits

st.title("📊 Productivity Tracker (Habits + Sleep + Screen Time)")

tab1, tab2, tab3 = st.tabs(["🧠 Habits", "😴 Sleep", "📱 Screen Time"])

# =========================================================
# HABITS
# =========================================================
with tab1:
    st.header("🧠 Habit Tracker")

    with st.form("add_habit"):
        col1, col2, col3 = st.columns(3)

        activity = col1.text_input("Activity")
        date = col2.date_input("Date", datetime.date.today())
        time = col3.time_input("Time")

        duration = st.number_input("Duration (min)", 1, 600, 30)

        submitted = st.form_submit_button("Add")

        if submitted and activity:
            new = {
                "Activity": activity,
                "Date": str(date),
                "Time": str(time),
                "Duration": duration,
                "Completed": False
            }

            st.session_state.habits = pd.concat(
                [st.session_state.habits, pd.DataFrame([new])],
                ignore_index=True
            )

            save(st.session_state.habits, HABITS_FILE)

    df = st.session_state.habits.copy()

    if not df.empty:

        df["Date"] = pd.to_datetime(df["Date"])
        df["Completed"] = df["Completed"].astype(int)

        df = df.sort_values(["Date", "Time"])

        st.subheader("📅 Activities")

        for i, row in df.iterrows():
            c1, c2, c3, c4 = st.columns([4, 2, 2, 2])

            with c1:
                st.write(row["Activity"])

            with c2:
                st.write(row["Date"].date())

            with c3:
                st.write(f"{row['Duration']} min")

            with c4:
                val = st.checkbox("Done", value=bool(row["Completed"]), key=i)
                st.session_state.habits.at[i, "Completed"] = int(val)

        save(st.session_state.habits, HABITS_FILE)

        # ---------------- GRAPH ----------------
        st.subheader("📈 Habit Completion Trend")

        progress = df.groupby("Date").agg(
            total=("Completed", "count"),
            done=("Completed", "sum")
        ).reset_index()

        progress["rate"] = progress["done"] / progress["total"]

        fig = px.line(progress, x="Date", y="rate", markers=True)
        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# SLEEP TRACKER
# =========================================================
with tab2:
    st.header("😴 Sleep Tracker")

    with st.form("sleep_form"):
        col1, col2 = st.columns(2)

        sleep_time = col1.time_input("Sleep Time")
        wake_time = col2.time_input("Wake Time")

        date = st.date_input("Date", datetime.date.today())

        submit = st.form_submit_button("Save")

        if submit:
            new = {
                "Date": str(date),
                "Sleep": str(sleep_time),
                "Wake": str(wake_time)
            }

            sleep = pd.concat([sleep, pd.DataFrame([new])], ignore_index=True)
            save(sleep, SLEEP_FILE)

    if not sleep.empty:

        df = sleep.copy()
        df["Date"] = pd.to_datetime(df["Date"])

        df["Sleep"] = pd.to_datetime(df["Sleep"], format="%H:%M:%S")
        df["Wake"] = pd.to_datetime(df["Wake"], format="%H:%M:%S")

        df["Duration"] = (df["Wake"] - df["Sleep"]).dt.seconds / 3600

        st.subheader("📊 Sleep Trend")

        fig = px.bar(df, x="Date", y="Duration", color="Duration")
        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# SCREEN TIME
# =========================================================
with tab3:
    st.header("📱 Screen Time Tracker")

    with st.form("screen_form"):
        col1, col2 = st.columns(2)

        app = col1.text_input("App")
        hours = col2.number_input("Hours", 0.0, 24.0, 1.0)

        date = st.date_input("Date", datetime.date.today())

        submit = st.form_submit_button("Add")

        if submit and app:
            new = {
                "App": app,
                "Date": str(date),
                "Hours": hours
            }

            screen = pd.concat([screen, pd.DataFrame([new])], ignore_index=True)
            save(screen, SCREEN_FILE)

    if not screen.empty:

        df = screen.copy()
        df["Date"] = pd.to_datetime(df["Date"])

        st.subheader("📊 App Usage")

        app_usage = df.groupby("App")["Hours"].sum().reset_index()

        fig1 = px.pie(app_usage, names="App", values="Hours")
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("📈 Daily Screen Time")

        daily = df.groupby("Date")["Hours"].sum().reset_index()

        fig2 = px.line(daily, x="Date", y="Hours", markers=True)
        st.plotly_chart(fig2, use_container_width=True)