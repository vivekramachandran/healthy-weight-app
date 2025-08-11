
# Healthy Weight Dashboard (CSV + Cloudinary)

This is a ready-to-deploy Streamlit app that stores data in CSV files and uploads photos to Cloudinary (optional).

## What's included
- `healthy_weight_dashboard_csv.py` — the Streamlit app
- `requirements.txt` — Python packages
- `data/` — folder with three CSV files (empty initially)

## Quick steps (non-techie)
1. Download the zip file from the link provided.
2. Unzip it on your computer.
3. Sign up for a **free Cloudinary** account (optional, but recommended for image hosting).
4. Create a **GitHub** account (if you don't have one).
5. Upload the unzipped folder to a new GitHub repository (use the GitHub web UI - drag & drop).
6. Go to **https://share.streamlit.io/** and log in with GitHub.
7. Create a new app, pick your repo and the file `healthy_weight_dashboard_csv.py`.
8. In Streamlit Cloud app settings -> Secrets, add your Cloudinary keys:

```toml
[cloudinary]
cloud_name = "your_cloud_name"
api_key = "your_api_key"
api_secret = "your_api_secret"
```

9. Deploy. Open the app URL and start logging meals.

## Run locally (optional)
1. Install Python 3.8+ from https://www.python.org/.
2. Open Terminal / Command Prompt and `cd` into the unzipped folder.
3. Install packages:
```
pip install -r requirements.txt
```
4. Create a folder `.streamlit` and inside it a file `secrets.toml` with the Cloudinary keys as above (optional).
5. Run:
```
streamlit run healthy_weight_dashboard_csv.py
```

## Data persistence
- The app saves CSV files in the `data/` folder. Streamlit Cloud preserves these between runs for your app.

