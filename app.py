import json
import os
from datetime import datetime

import requests
import streamlit as st

st.set_page_config(page_title="TripMate AI", page_icon="✈️", layout="wide")

INTERESTS = ["Sightseeing", "Food", "Nature", "Adventure", "Culture", "Shopping"]
STYLES = ["Relaxed", "Balanced", "Packed"]

def demo_itinerary(destination, days, budget, interests, style):
    selected = interests or ["Sightseeing"]
    itinerary = []
    for day in range(1, days + 1):
        interest = selected[(day - 1) % len(selected)]
        itinerary.append({
            "day": day,
            "title": f"Day {day} — {interest}",
            "activities": [
                {"time": "09:00 AM", "name": f"Explore a popular attraction in {destination}", "type": "Sightseeing"},
                {"time": "12:30 PM", "name": f"Try local food in {destination}", "type": "Food"},
                {"time": "03:00 PM", "name": f"{interest} activity or local experience", "type": interest},
                {"time": "06:00 PM", "name": "Relax, take photos, and explore nearby streets", "type": "Leisure"},
            ],
        })
    return {
        "title": f"{days}-Day Trip to {destination}", "destination": destination,
        "days": days, "budget": float(budget), "style": style,
        "estimated_cost": round(float(budget) * 0.85, 2),
        "budget_note": "Demo estimate only; confirm current prices before travelling.",
        "itinerary": itinerary, "generated_by": "demo",
    }

def generate_with_gemini(destination, days, budget, interests, style, api_key, model):
    prompt = f"""Create a practical travel itinerary as valid JSON only, with no markdown.
Destination: {destination}
Number of days: {days}
Total budget in INR: {budget}
Interests: {", ".join(interests) if interests else "general sightseeing"}
Travel style: {style}
Return JSON with keys title, destination, days, budget, style, estimated_cost, budget_note,
itinerary (array with day, title, activities; each activity has time, name, type), generated_by.
Include 3-4 activities per day. Do not claim live availability, exact current prices, or verified travel times."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    response = requests.post(url, json={
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.7},
    }, timeout=45)
    response.raise_for_status()
    result = json.loads(response.json()["candidates"][0]["content"]["parts"][0]["text"])
    result["generated_by"] = "gemini"
    return result

if "saved_trips" not in st.session_state:
    st.session_state.saved_trips = []
if "trip" not in st.session_state:
    st.session_state.trip = None

st.title("✈️ TripMate AI")
st.caption("Your personal travel assistant — personalized day-by-day travel plans in minutes.")
st.divider()

with st.sidebar:
    st.header("🧭 Build your trip")
    with st.form("trip_form"):
        destination = st.text_input("Where do you want to go?", value="Jaipur", max_chars=100)
        days = st.selectbox("Duration", list(range(1, 8)), index=1, format_func=lambda n: f"{n} {'day' if n == 1 else 'days'}")
        budget = st.number_input("Total budget (₹)", min_value=1, max_value=10000000, value=8000, step=500)
        interests = st.multiselect("What are you into?", INTERESTS, default=["Sightseeing", "Food", "Culture"])
        style = st.radio("Your travel vibe", STYLES, index=1)
        generate = st.form_submit_button("✨ Generate my itinerary", use_container_width=True, type="primary")
    st.caption("Trip estimates are suggestions, not live quotes.")

if generate:
    if len(destination.strip()) < 2:
        st.error("Please enter a destination with at least 2 characters.")
    else:
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        with st.spinner("Planning your trip..."):
            if api_key:
                try:
                    st.session_state.trip = generate_with_gemini(destination.strip(), days, budget, interests, style, api_key, model)
                except Exception as exc:
                    st.warning(f"AI generation was unavailable; showing a demo itinerary instead. Details: {exc}")
                    st.session_state.trip = demo_itinerary(destination.strip(), days, budget, interests, style)
            else:
                st.session_state.trip = demo_itinerary(destination.strip(), days, budget, interests, style)

trip = st.session_state.trip
left, right = st.columns([1, 1.7], gap="large")
with left:
    st.subheader("🌍 Your trip preferences")
    st.write(f"**Destination:** {destination}")
    st.write(f"**Duration:** {days} days")
    st.write(f"**Budget:** ₹{budget:,.0f}")
    st.write(f"**Interests:** {', '.join(interests) if interests else 'General sightseeing'}")
    st.write(f"**Travel style:** {style}")
    st.info("The app works without an API key using a demo itinerary generator. Add a Gemini API key in Streamlit Secrets for AI-generated plans.")

with right:
    st.subheader("🗺️ Your itinerary")
    if not trip:
        st.info("Your personalized day-by-day plan will appear here. Choose your preferences in the sidebar and click Generate my itinerary.")
    else:
        st.header(trip.get("title", "Your trip"))
        c1, c2, c3 = st.columns(3)
        c1.metric("Days", trip.get("days", 0))
        c2.metric("Your budget", f"₹{float(trip.get('budget', 0)):,.0f}")
        c3.metric("Estimated spend", f"₹{float(trip.get('estimated_cost', 0)):,.0f}")
        st.caption(trip.get("budget_note", "Planning estimate only; verify details before travelling."))
        for day in trip.get("itinerary", []):
            with st.container(border=True):
                st.markdown(f"### Day {day.get('day', '')}: {day.get('title', '')}")
                for activity in day.get("activities", []):
                    st.markdown(f"**{activity.get('time', 'Flexible')}** · {activity.get('name', 'Activity')}")
                    if activity.get("type"):
                        st.caption(activity["type"])
        a, b = st.columns(2)
        with a:
            if st.button("🔖 Save trip", use_container_width=True):
                st.session_state.saved_trips.insert(0, {
                    "id": datetime.now().isoformat(timespec="seconds"),
                    "title": trip.get("title", "Saved trip"),
                    "destination": trip.get("destination", ""),
                    "trip_data": trip,
                })
                st.success("Trip saved for this app session.")
        with b:
            st.download_button("⬇️ Download itinerary JSON",
                data=json.dumps(trip, indent=2, ensure_ascii=False),
                file_name="tripmate_itinerary.json", mime="application/json",
                use_container_width=True)

st.divider()
st.subheader(f"📚 Saved trips ({len(st.session_state.saved_trips)})")
if not st.session_state.saved_trips:
    st.caption("Generate a plan and click Save trip. Saved trips are kept for the current app session.")
else:
    for i, record in enumerate(st.session_state.saved_trips):
        c1, c2, c3 = st.columns([4, 1, 1])
        c1.write(f"**{record['title']}**  \n{record['destination']}")
        if c2.button("Open", key=f"open_{i}"):
            st.session_state.trip = record["trip_data"]
            st.rerun()
        if c3.button("Delete", key=f"delete_{i}"):
            st.session_state.saved_trips.pop(i)
            st.rerun()

st.caption("Made for curious travelers ✦ Estimates are illustrative, not live travel quotes.")
