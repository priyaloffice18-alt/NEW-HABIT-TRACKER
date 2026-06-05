import streamlit as st
import pandas as pd
import datetime
import os

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Productivity App", layout="wide")

# -----------------------------
# FILES
# -----------------------------
HABITS_FILE = "habits.csv"
SLEEP_FILE = "sleep.csv"
SCREEN_FILE = "screen.csv"

# -----------------------------
# SAFE LOAD FUNCTION
# -----------------------------
def load_csv(file, columns):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame(columns=columns)

def save_csv(df, file):
    df.to_csv(file, index=False)

# -----------------------------
# LOAD DATA
# -----------------------------
habits = load_csv(HABITS_FILE, ["Activity", "Date", "Time", "Duration", "Completed"])
sleep = load_csv(SLEEP_FILE, ["Date", "Sleep", "Wake"])
screen = load_csv(SCREEN_FILE, ["App", "Date", "Hours"])

# -----------------------------
# SESSION STATE
# -----------------------------
if "habits" not in st.session_state:
    st.session_state.habits = habits

# -----------------------------
# SAFE TIME FUNCTION (IMPORTANT FIX)
# -----------------------------
def safe_time(val):
    try:
        return datetime.datetime.strptime(str(val), "%H:%M:%S").time()
    except:
        try:
            return datetime.datetime.strptime(str(val), "%H:%M").time()
        except:
            return datetime.datetime.now().time()

# -----------------------------
# TITLE
# -----------------------------
st.title("📊 Productivity App (Habits + Sleep + Screen Time)")

tab1, tab2, tab3 = st.tabs(["🧠 Habits", "😴 Sleep", "📱 Screen Time"])

# =========================================================
# HABITS
# =========================================================
with tab1:
    st.header("🧠 Habit Tracker")

    # ---------------- ADD ----------------
    with st.form("add_habit"):
        col1, col2, col3 = st.columns(3)

        activity = col1.text_input("Activity")
        date = col2.date_input("Date", datetime.date.today())
        time = col3.time_input("Time")

        duration = st.number_input("Duration (min)", 1, 600, 30)

        submit = st.form_submit_button("Add Activity")

        if submit and activity:
            new_row = {
                "Activity": activity,
                "Date": str(date),
                "Time": time.strftime("%H:%M:%S"),
                "Duration": duration,
                "Completed": False
            }

            st.session_state.habits = pd.concat(
                [st.session_state.habits, pd.DataFrame([new_row])],
                ignore_index=True
            )

            save_csv(st.session_state.habits, HABITS_FILE)
            st.success("Added successfully!")

    df = st.session_state.habits.copy()

    if not df.empty:

        df["Date"] = pd.to_datetime(df["Date"])

        st.subheader("📅 Activities (Editable)")

        for i, row in df.iterrows():

            col1, col2, col3, col4 = st.columns([3,2,2,2])

            with col1:
                act = st.text_input("Activity", row["Activity"], key=f"act_{i}")

            with col2:
                d = st.date_input("Date", row["Date"].date(), key=f"date_{i}")

            with col3:
                t = st.time_input("Time", value=safe_time(row["Time"]), key=f"time_{i}")

            with col4:
                done = st.checkbox("Done", value=bool(row["Completed"]), key=f"done_{i}")

            c1, c2 = st.columns(2)

            with c1:
                if st.button("💾 Update", key=f"upd_{i}"):

                    st.session_state.habits.at[i, "Activity"] = act
                    st.session_state.habits.at[i, "Date"] = str(d)
                    st.session_state.habits.at[i, "Time"] = t.strftime("%H:%M:%S")
                    st.session_state.habits.at[i, "Completed"] = done

                    save_csv(st.session_state.habits, HABITS_FILE)
                    st.success("Updated!")

            with c2:
                if st.button("🗑 Delete", key=f"del_{i}"):

                    st.session_state.habits = st.session_state.habits.drop(i).reset_index(drop=True)
                    save_csv(st.session_state.habits, HABITS_FILE)
                    st.rerun()

        # ---------------- PROGRESS ----------------
        st.subheader("📈 Progress")

        progress = st.session_state.habits.copy()

        if not progress.empty:
            progress["Date"] = pd.to_datetime(progress["Date"])
            progress["Completed"] = progress["Completed"].astype(int)

            daily = progress.groupby("Date").agg(
                total=("Completed", "count"),
                done=("Completed", "sum")
            ).reset_index()

            daily["rate"] = daily["done"] / daily["total"]

            st.line_chart(daily.set_index("Date")["rate"])

# =========================================================
# SLEEP
# =========================================================
with tab2:
    st.header("😴 Sleep Tracker")

    with st.form("sleep"):
        col1, col2 = st.columns(2)

        sleep_t = col1.time_input("Sleep Time")
        wake_t = col2.time_input("Wake Time")

        date = st.date_input("Date", datetime.date.today())

        if st.form_submit_button("Save Sleep"):

            new = {
                "Date": str(date),
                "Sleep": sleep_t.strftime("%H:%M:%S"),
                "Wake": wake_t.strftime("%H:%M:%S")
            }

            sleep = pd.concat([sleep, pd.DataFrame([new])], ignore_index=True)
            save_csv(sleep, SLEEP_FILE)
            st.success("Saved!")

    if not sleep.empty:

        df = sleep.copy()
        df["Date"] = pd.to_datetime(df["Date"])

        df["Sleep"] = pd.to_datetime(df["Sleep"], format="%H:%M:%S")
        df["Wake"] = pd.to_datetime(df["Wake"], format="%H:%M:%S")

        df["Hours"] = (df["Wake"] - df["Sleep"]).dt.seconds / 3600

        st.bar_chart(df.set_index("Date")["Hours"])

# =========================================================
# SCREEN TIME
# =========================================================
with tab3:
    st.header("📱 Screen Time")

    with st.form("screen"):
        col1, col2 = st.columns(2)

        app = col1.text_input("App")
        hours = col2.number_input("Hours", 0.0, 24.0, 1.0)

        date = st.date_input("Date", datetime.date.today())

        if st.form_submit_button("Add") and app:

            new = {
                "App": app,
                "Date": str(date),
                "Hours": hours
            }

            screen = pd.concat([screen, pd.DataFrame([new])], ignore_index=True)
            save_csv(screen, SCREEN_FILE)
            st.success("Added!")

    if not screen.empty:

        df = screen.copy()
        df["Date"] = pd.to_datetime(df["Date"])

        st.subheader("App Usage")

        app_usage = df.groupby("App")["Hours"].sum()

        st.bar_chart(app_usage)

        st.subheader("Daily Usage")

        daily = df.groupby("Date")["Hours"].sum()

        st.line_chart(daily)
