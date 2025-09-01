# tasks/weather_task.py
from crewai import Task, Crew
from agents.weather_advisor_agent import weather_advisor

def run_weather_advice(user_prompt: str, context: dict):
    """
    Runs the Weather Advisor agent.
    Expects context to contain keys: destination, start_date, end_date
    Returns raw and structured placeholder.
    """
    description = (
        "Provide weather forecast and explicit safety assessment for given destination and dates. "
        "Use context.destination, context.start_date, context.end_date.. for {user_prompt} "
        "Output should include: quick_summary, daily_forecasts(list), activity_advice, travel_safety('Safe'/'Unsafe'), sources."
    )
    task = Task(description=description, agent=weather_advisor, expected_output="A valid paragraph format with listing Structured weather + safety info")
    crew = Crew(agents=[weather_advisor], tasks=[task], verbose=False)
    inputs = {"user_prompt": user_prompt, "context": context}
    result = crew.kickoff(inputs=inputs)
    return {"raw": result, "structured": None}
