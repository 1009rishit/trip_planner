# tasks/itinerary_task.py
from crewai import Task, Crew
from agents.itinerary_builder import itinerary_planner

def run_itinerary_builder(user_prompt: str, context: dict):
    """
    Runs the Itinerary Builder agent.
    Context should include aggregated outputs from: travel_research, weather, transport, hotels, budget.
    The itinerary builder will create a day-by-day plan and return it as raw text (structured).
    """
    description = f"""
    You are creating a day-by-day itinerary.

    User Request:
    {user_prompt}

    Supporting Context:
    - Travel Research: {context.get("research")}
    - Weather: {context.get("weather")}
    - Transport: {context.get("transport")}
    - Hotels: {context.get("hotels")}
    - Budget: {context.get("budget")}

    Instructions:
    For each day include: Morning, Lunch, Afternoon, Evening, Dinner & Night, Daily Budget, Getting Around, Pro Tip.
    """
    task = Task(description=description, agent=itinerary_planner, expected_output="Detailed day-by-day itinerary not in the JSON but in the paragraph format")
    crew = Crew(agents=[itinerary_planner], tasks=[task], verbose=False)
    inputs = {"user_prompt": user_prompt, **context}
    result = crew.kickoff(inputs=inputs)
    return {"raw": result, "structured": None}
