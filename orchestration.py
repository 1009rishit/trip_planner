# main_orchestrator.py
from datetime import datetime
from tasks.travel_task import run_travel_research
from tasks.weather_task import run_weather_advice
from tasks.transport_task import run_transport_advice
from tasks.hotel_task import run_hotel_recommendation
from tasks.budget_task import run_budget_optimizer
from tasks.itinerary_task import run_itinerary_builder
import json

def safe_context_value(agent_out):
    if isinstance(agent_out.get("structured"), dict):
        return agent_out["structured"]   # already dict
    try:
        return json.loads(str(agent_out["raw"]))  # parse JSON string
    except Exception:
        return str(agent_out["raw"])  # fallback as plain text
    

def parse_user_prompt(user_prompt: str):
    """
    Lightweight parser that extracts key fields from the user's natural prompt.
    This is a simple heuristic parser. You can replace with a robust NLP parser later.
    Returns a context dict with keys:
        origin, destination, start_date (YYYY-MM-DD), end_date (YYYY-MM-DD),
        travel_mode_preference, budget_total (int), travelers (int)
    """
    # Simple defaults
    ctx = {
        "origin": None,
        "destination": None,
        "start_date": None,
        "end_date": None,
        "travel_mode_preference": None,
        "budget_total": None,
        "travelers": 1,
    }

    # Very lightweight parsing — best-effort. Update as needed.
    # Examples this will parse: "I want to travel from delhi to manali on 1/09/2025 to 3/09/2025 and I want to travel by my car, My budget is something about 20000 and we are travelling 2 person"
    import re
    s = user_prompt.lower()

    # origin -> destination
    m = re.search(r"from\s+([a-z\s\-]+)\s+to\s+([a-z\s\-]+)", s)
    if m:
        ctx["origin"] = m.group(1).strip().title()
        ctx["destination"] = m.group(2).strip().title()

    # dates
    m = re.search(r"(\d{1,2}[/-]\d{1,2}[/-]\d{4})\s*(?:to|-)\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})", s)
    if m:
        def normalize_date(d):
            d = d.replace("/", "-")
            # Convert d/m/yyyy or dd-mm-yyyy to YYYY-MM-DD
            try:
                parsed = datetime.strptime(d, "%d-%m-%Y")
                return parsed.strftime("%Y-%m-%d")
            except Exception:
                try:
                    parsed = datetime.strptime(d, "%d/%m/%Y")
                    return parsed.strftime("%Y-%m-%d")
                except Exception:
                    return None
        ctx["start_date"] = normalize_date(m.group(1))
        ctx["end_date"] = normalize_date(m.group(2))

    # travel mode
    if "car" in s or "by my car" in s:
        ctx["travel_mode_preference"] = "car"
    elif "flight" in s or "plane" in s:
        ctx["travel_mode_preference"] = "flight"

    # budget
    m = re.search(r"budget.*?(\d{3,})", s)
    if m:
        try:
            ctx["budget_total"] = int(m.group(1))
        except:
            ctx["budget_total"] = None

    # travelers
    m = re.search(r"we are\s*(\d+)\s*person", s)
    if m:
        ctx["travelers"] = int(m.group(1))

    return ctx

def orchestrate(user_prompt: str):
    """
    Runs tasks in this order with explicit separate task runs:
      1) Travel Research
      2) Weather Advisor
      3) Transport Advisor
      4) Hotel Recommendation
      5) Budget Optimizer
      6) Itinerary Builder

    Returns the aggregated results dict.
    """
    print("Parsing user prompt...")
    context = parse_user_prompt(user_prompt)
    print("Parsed context:", context)

    results = {}

    # 1) Travel research
    print("\n[1/6] Running Travel Researcher...")
    travel_out = run_travel_research(user_prompt, context)
    results["travel_research"] = travel_out
   
    # 2) Weather advisor
    print("\n[2/6] Running Weather Advisor...")
    weather_ctx = {
        "destination": context.get("destination"),
        "start_date": context.get("start_date"),
        "end_date": context.get("end_date")
    }
    weather_out = run_weather_advice(user_prompt, weather_ctx)
    results["weather_advice"] = weather_out

    # 3) Transport advisor
    print("\n[3/6] Running Transport Advisor...")
    transport_ctx = {
        "origin": context.get("origin"),
        "destination": context.get("destination"),
        "travel_mode_preference": context.get("travel_mode_preference"),
        "travelers": context.get("travelers"),
        "weather_summary": weather_out["raw"]
    }
    transport_out = run_transport_advice(user_prompt, transport_ctx)
    results["transport_advice"] = transport_out

    # 4) Hotel recommendation
    print("\n[4/6] Running Hotel Recommendation...")
    hotel_ctx = {
        "destination": context.get("destination"),
        "budget_total": context.get("budget_total"),
        "travelers": context.get("travelers"),
        "attractions_summary": travel_out["raw"]
    }
    hotel_out = run_hotel_recommendation(user_prompt, hotel_ctx)
    results["hotel_recommendation"] = hotel_out

    # 5) Budget optimizer
    print("\n[5/6] Running Budget Optimizer...")
    budget_ctx = {
        "budget_total": context.get("budget_total"),
        "transport_estimates": transport_out["raw"],
        "hotel_options": hotel_out["raw"],
        "trip_length_days": None, 
        "travelers": context.get("travelers")
    }
    budget_out = run_budget_optimizer(user_prompt, budget_ctx)
    results["budget_optimizer"] = budget_out

    # 6) Itinerary builder
    print("\n[6/6] Running Itinerary Builder...")
    itinerary_ctx = {
        "research": safe_context_value(travel_out),
        "weather": safe_context_value(weather_out),
        "transport": safe_context_value(transport_out),
        "hotels": safe_context_value(hotel_out),
        "budget": safe_context_value(budget_out)
    }
    itinerary_out = run_itinerary_builder(user_prompt, itinerary_ctx)
    results["itinerary"] = itinerary_out

    print("\nAll tasks completed.")
    return results

if __name__ == "__main__":
    sample_prompt = (
        "I want to travel from Delhi to Manali on 01/09/2025 to 03/09/2025. "
        "I want to travel by my car, My budget is something about 20000 and we are travelling 2 person"
    )
    full_results = orchestrate(sample_prompt)
    for k, v in full_results.items():
        print("\n" + "="*40)
        print(f"{k.upper()} RAW OUTPUT:\n")
        print(v["raw"])
