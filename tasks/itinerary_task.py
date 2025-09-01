# tasks/itinerary_task.py
from crewai import Task, Crew
from agents.itinerary_builder import itinerary_planner

def run_itinerary_builder(user_prompt: str, context: dict):
    """
    Runs the Itinerary Builder agent.
    Context should include aggregated outputs from: travel_research, weather, transport, hotels, budget.
    The itinerary builder will create a day-by-day plan and return it in paragraph format (not JSON).
    """
    description = f"""
    You are creating a day-by-day travel itinerary.

    User Request:
    {user_prompt}

    Supporting Context:
    - Travel Research: {context.get("research")}
    - Weather: {context.get("weather")}
    - Transport: {context.get("transport")}
    - Hotels: {context.get("hotels")}
    - Budget: {context.get("budget")}

    Instructions:
    Write the complete itinerary in a natural, narrative style.
    Each day should be written in paragraph format, like a travel blog or guidebook.
    Do NOT use JSON, bullet points, or lists.
    Just write flowing text with transitions.
    """

    task = Task(
        description=description,
        agent=itinerary_planner,
        expected_output="A detailed day-by-day itinerary written as natural language paragraphs only"
    )

    crew = Crew(
        agents=[itinerary_planner],
        tasks=[task],
        verbose=False
    )

    inputs = {"user_prompt": user_prompt, **context}
    result = crew.kickoff(inputs=inputs)

    if isinstance(result, dict):
        # safely return "final_output" if present
        return str(result.get("final_output", result))
    elif hasattr(result, "final_output"):
        return str(result.final_output)
    else:
        return str(result)

