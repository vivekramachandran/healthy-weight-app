
import streamlit as st
import pandas as pd
import datetime as dt
import os
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns
import uuid

# Optional Cloudinary import (only used if configured)
try:
    import cloudinary
    import cloudinary.uploader
except Exception:
    cloudinary = None

st.set_page_config(page_title="Healthy Weight Dashboard", layout="wide")

st.title("🏋️ My Healthy Weight Dashboard (CSV + Cloudinary)")
st.markdown(
    "A simple, free Streamlit app to track meals, weight, habits and photos. "
    "Photos upload to Cloudinary if you add Cloudinary keys in Streamlit Secrets; otherwise images are saved locally."
)

# ------------------------------
# CHECK CLOUDINARY CONFIG
# ------------------------------
CLOUDINARY_AVAILABLE = False
if "cloudinary" in st.secrets:
    cfg = st.secrets["cloudinary"]
    if cfg.get("cloud_name") and cfg.get("api_key") and cfg.get("api_secret") and cloudinary is not None:
        try:
            cloudinary.config(
                cloud_name=cfg["cloud_name"],
                api_key=cfg["api_key"],
                api_secret=cfg["api_secret"]
            )
            CLOUDINARY_AVAILABLE = True
        except Exception:
            CLOUDINARY_AVAILABLE = False

if not CLOUDINARY_AVAILABLE:
    st.info("Cloudinary is NOT configured. Photos will be saved locally. To enable remote uploads, add Cloudinary keys in Streamlit Secrets.")

# ------------------------------
# FILE / DATA SETUP
# ------------------------------
DATA_DIR = "data"
IMAGES_DIR = os.path.join(DATA_DIR, "images")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

MEAL_FILE = os.path.join(DATA_DIR, "meal_logs.csv")
WEIGHT_FILE = os.path.join(DATA_DIR, "weight_logs.csv")
HABIT_FILE = os.path.join(DATA_DIR, "habit_logs.csv")

# Ensure CSVs exist with headers
def ensure_csv(path, headers):
    if not os.path.exists(path):
        df = pd.DataFrame(columns=headers)
        df.to_csv(path, index=False)

ensure_csv(MEAL_FILE, ["date","meal","portion","photo_url","food_quality","protein_g","fiber_g","mood_before","mood_after","hunger_before","hunger_after"])
ensure_csv(WEIGHT_FILE, ["date","weight","waist"])
ensure_csv(HABIT_FILE, ["date","walk","water","fruit","custom_habit","reflection"])

def load_csv(path):
    df = pd.read_csv(path)
    if "date" in df.columns and not df.empty:
        df["date"] = pd.to_datetime(df["date"])
    return df

def save_csv(df, path):
    df.to_csv(path, index=False)

# Load data
meal_logs = load_csv(MEAL_FILE)
weight_logs = load_csv(WEIGHT_FILE)
habit_logs = load_csv(HABIT_FILE)

# ------------------------------
# 1. CONSISTENT TRACKING WITHOUT OVERLOAD
# ------------------------------
st.header("1️⃣ Consistent Tracking Without Overload")

with st.form("meal_form", clear_on_submit=True):
    meal = st.text_input("Meal / Snack Description")
    portion = st.selectbox("Portion Estimate", ["Small", "Medium", "Large"])
    photo = st.file_uploader("Upload Meal Photo (optional)", type=["jpg","jpeg","png"])
    food_quality = st.selectbox("Food Quality", ["Whole food", "Minimally processed", "Ultra-processed"])
    protein = st.number_input("Protein intake (g)", min_value=0)
    fiber = st.number_input("Fiber intake (g)", min_value=0)
    mood_before = st.text_input("Mood before meal")
    mood_after = st.text_input("Mood after meal")
    hunger_before = st.slider("Hunger before meal (1-10)", 1, 10, 5)
    hunger_after = st.slider("Hunger after meal (1-10)", 1, 10, 5)
    submitted = st.form_submit_button("Log Meal")
    if submitted:
        photo_url = ""
        if photo is not None:
            try:
                img = Image.open(photo)
                # Save/upload
                if CLOUDINARY_AVAILABLE:
                    buffer = BytesIO()
                    img.save(buffer, format="JPEG")
                    buffer.seek(0)
                    upload_result = cloudinary.uploader.upload(buffer)
                    photo_url = upload_result.get("secure_url", "")
                else:
                    fname = f"{uuid.uuid4().hex}.jpg"
                    local_path = os.path.join(IMAGES_DIR, fname)
                    img.save(local_path, format="JPEG")
                    photo_url = local_path
            except Exception as e:
                st.error("Could not process image: " + str(e))
        new_row = {
            "date": dt.date.today().isoformat(),
            "meal": meal,
            "portion": portion,
            "photo_url": photo_url,
            "food_quality": food_quality,
            "protein_g": protein,
            "fiber_g": fiber,
            "mood_before": mood_before,
            "mood_after": mood_after,
            "hunger_before": hunger_before,
            "hunger_after": hunger_after
        }
        meal_logs = pd.concat([meal_logs, pd.DataFrame([new_row])], ignore_index=True)
        save_csv(meal_logs, MEAL_FILE)
        st.success("Meal logged!")

# Daily streak / quick metrics
st.subheader("Quick logging stats")
if not meal_logs.empty:
    unique_days = meal_logs['date'].dt.date.nunique() if "date" in meal_logs.columns else 0
else:
    unique_days = 0
st.metric("Days with logs", unique_days)

# ------------------------------
# 2. SHORT-TERM & LONG-TERM PROGRESS VIEW
# ------------------------------
st.header("2️⃣ Short-Term & Long-Term Progress View")

with st.form("weight_form", clear_on_submit=True):
    weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1)
    waist = st.number_input("Waist (cm)", min_value=0.0, step=0.1)
    added = st.form_submit_button("Add Measurement")
    if added:
        new_row = {"date": dt.date.today().isoformat(), "weight": weight, "waist": waist}
        weight_logs = pd.concat([weight_logs, pd.DataFrame([new_row])], ignore_index=True)
        save_csv(weight_logs, WEIGHT_FILE)
        st.success("Measurement logged!")

if not weight_logs.empty:
    st.subheader("3-Month Trend")
    st.line_chart(weight_logs.tail(90).set_index("date")[["weight","waist"]])
    st.subheader("12-Month Trend")
    st.line_chart(weight_logs.tail(365).set_index("date")[["weight","waist"]])

st.subheader("Motivation Notes (not saved automatically)")
motivation = st.text_area("Why am I doing this?")

# ------------------------------
# 3. COACHING OR GUIDED TIPS SECTION
# ------------------------------
st.header("3️⃣ Coaching or Guided Tips")
st.sidebar.header("Weekly Coach Corner")
st.sidebar.write("✅ Add one extra cup of veggies per day")
st.sidebar.write("💡 Eat protein at each meal for satiety")
st.sidebar.subheader("Monthly Goal Review Prompt")
st.sidebar.write("Reflect on progress and set next step.")

# ------------------------------
# 4. MULTI-METRIC MONITORING DASHBOARD
# ------------------------------
st.header("4️⃣ Multi-Metric Monitoring Dashboard")
c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Weight (last entry)", f"{weight if 'weight' in locals() else 'N/A'}")
c2.metric("Steps", "N/A")
c3.metric("Calories", "N/A")
c4.metric("Nutrient Balance", "N/A")
c5.metric("Sleep", "N/A")

# Consistency Heatmap
st.subheader("Consistency Heatmap")
if not meal_logs.empty:
    df = meal_logs.copy()
    df['day'] = pd.to_datetime(df['date']).dt.date
    df['count'] = 1
    heat = df.groupby('day')['count'].sum().reset_index()
    heat['dow'] = pd.to_datetime(heat['day']).dt.weekday
    heat['week'] = pd.to_datetime(heat['day']).dt.isocalendar().week
    pivot = heat.pivot(index='dow', columns='week', values='count').fillna(0)
    fig, ax = plt.subplots(figsize=(10,3))
    sns.heatmap(pivot, cmap='Greens', cbar=False, linewidths=.5, linecolor='grey')
    ax.set_yticks(range(7))
    ax.set_yticklabels(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"], rotation=0)
    st.pyplot(fig)
else:
    st.write("No meal logs yet — log some meals to populate the heatmap.")

# ------------------------------
# 5. MEAL PHOTO JOURNAL
# ------------------------------
st.header("5️⃣ Meal Photo Journal")
if not meal_logs.empty:
    for _, row in meal_logs[::-1].iterrows():
        photo_url = row.get("photo_url", "")
        caption = f\"{row.get('meal','')} - {row.get('date','')} ({row.get('portion','')})\"
        if isinstance(photo_url, str) and photo_url.startswith("http"):
            st.image(photo_url, caption=caption, use_column_width=True)
        elif isinstance(photo_url, str) and os.path.exists(photo_url):
            st.image(photo_url, caption=caption, use_column_width=True)
        else:
            # no image for this row
            st.write(caption)

# ------------------------------
# NUTRIENT BALANCE CHART
# ------------------------------
st.header("🍽 Nutrient Balance (Protein & Fiber)")
if not meal_logs.empty:
    df = meal_logs.copy()
    df['date'] = pd.to_datetime(df['date'])
    daily = df.groupby(df['date'].dt.date)[['protein_g','fiber_g']].sum().reset_index()
    daily = daily.set_index('date')
    st.bar_chart(daily)
else:
    st.write("No nutrient data yet — log meals with protein/fiber amounts.")

# ------------------------------
# HABITS & REFLECTION
# ------------------------------
st.header("💪 Habit Anchoring & Lifestyle")
with st.form("habit_form", clear_on_submit=True):
    habit_walk = st.checkbox("10-min walk")
    habit_water = st.checkbox("Drink 2L water")
    habit_fruit = st.checkbox("Eat 2+ servings of fruit")
    custom_habit = st.text_input("Custom Habit")
    reflection = st.text_area("Weekly Reflection")
    saved = st.form_submit_button("Save Habits")
    if saved:
        new_row = {"date": dt.date.today().isoformat(), "walk": habit_walk, "water": habit_water, "fruit": habit_fruit, "custom_habit": custom_habit, "reflection": reflection}
        habit_logs = pd.concat([habit_logs, pd.DataFrame([new_row])], ignore_index=True)
        save_csv(habit_logs, HABIT_FILE)
        st.success("Habits saved!")

st.markdown("---")
st.caption("Built with ❤️ — Your data is stored as CSV files in the app's `data/` folder. If you want remote image hosting, add Cloudinary keys in Streamlit Secrets.")
