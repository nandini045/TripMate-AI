# TripMate AI — Streamlit Edition

A Python Streamlit version of TripMate AI, adapted from the original React + FastAPI starter.

## Features
- Destination, duration, budget, interests, and travel-style inputs
- Day-by-day itinerary generation
- Built-in demo mode (works without an API key)
- Optional Gemini-powered itinerary generation
- Save trips during the current app session
- Download itinerary as JSON

**Note:** This app does not check live opening hours, transport availability, exact prices, or real-time routes. Budget numbers are estimates only.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Optional: Enable Gemini
Set `GEMINI_API_KEY` and optionally `GEMINI_MODEL` as environment variables. Never commit API keys to GitHub.

For Streamlit Community Cloud, open **App settings → Secrets** and add:
```toml
GEMINI_API_KEY = "your-key-here"
GEMINI_MODEL = "gemini-2.5-flash"
```

The app works without these secrets using the demo itinerary generator.

## Deploy to Streamlit Community Cloud
1. Create a public GitHub repository and upload `app.py`, `requirements.txt`, and `README.md`.
2. Visit https://share.streamlit.io/ and sign in with GitHub.
3. Click **Create app**, select the repository, branch `main`, and main file path `app.py`.
4. Deploy. Copy the public app URL after it is published.

The original `frontend/` and `backend/` folders are not needed for this Streamlit deployment.
