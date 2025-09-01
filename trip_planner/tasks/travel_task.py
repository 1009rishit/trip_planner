# tasks/travel_task.py
from crewai import Task, Crew
from agents.travel_researcher import travel_researcher

def run_travel_research(user_prompt: str, context: dict):
    """
    Runs the Travel Researcher agent.
    Args:
        user_prompt: The main query string (e.g., "Plan a 3-day trip to Manali")
        context: Dict with any additional info (e.g., {"theme": "cultural and food experiences"})
    Returns:
        dict with raw output and placeholder for structured JSON.
    """
    description = (
        "Research attractions and local tips for the given trip. "
        "Main request: {query}. "
        "Additional context: {context}. "
        "Output should be structured JSON-like with keys: "
        "summary, top_attractions (list), hidden_gems (list), "
        "practical_tips (list), sources (list)."
    )
    
    task = Task(
        description=description,
        agent=travel_researcher,
        expected_output="Structured JSON-like listing of attractions, hidden gems, tips and sources."
    )
    
    crew = Crew(
        agents=[travel_researcher],
        tasks=[task],
        verbose=False
    )
    
    inputs = {"query": user_prompt, "context": context}
    result = crew.kickoff(inputs=inputs)
    
    return {"raw": result, "structured": None}
