# app.py
import streamlit as st
from orchestration import orchestrate

st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 AI Travel Planner")
st.markdown("Plan your trip with AI agents for research, weather, hotels, transport, budget, and itinerary.")

# User Input
with st.form("trip_form"):
    user_prompt = st.text_area(
        "Describe your trip details:",
        placeholder="Example: I want to travel from Delhi to Manali on 01/09/2025 to 03/09/2025. "
                    "I want to travel by my car, My budget is 20000 and we are travelling 2 persons."
    )
    submitted = st.form_submit_button("Plan My Trip ✈️")

if submitted and user_prompt.strip():
    st.info("🔍 Parsing your request and running agents... Please wait.")

    try:
        results = orchestrate(user_prompt)

        # Display Results
        with st.expander("🗺️ Travel Research", expanded=True):
            st.write(results["travel_research"]["raw"])

        with st.expander("🌦️ Weather Advisor", expanded=True):
            st.write(results["weather_advice"]["raw"])

        with st.expander("🚗 Transport Advisor", expanded=True):
            st.write(results["transport_advice"]["raw"])

        with st.expander("🏨 Hotel Recommendations", expanded=True):
            st.write(results["hotel_recommendation"]["raw"])

        with st.expander("💰 Budget Optimizer", expanded=True):
            st.write(results["budget_optimizer"]["raw"])

        with st.expander("📅 Itinerary Builder", expanded=True):
            st.write(results["itinerary"]["raw"])

        st.success("✅ Trip plan generated successfully!")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
