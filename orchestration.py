# orchestration.py
from datetime import datetime
from typing import Dict, Any
import re

# Import your existing task functions
from tasks.travel_task import run_travel_research
from tasks.weather_task import run_weather_advice
from tasks.transport_task import run_transport_advice
from tasks.hotel_task import run_hotel_recommendation
from tasks.budget_task import run_budget_optimizer
from tasks.itinerary_task import run_itinerary_builder

# ChromaDB memory
from db.memory_store import add_memory, query_memory


class ConversationalOrchestrator:
    """Handles conversational flow with persistent memory in ChromaDB."""

    INTENT_PATTERNS = {
        "overview": [r"give me details", r"tell me about", r"overview", r"information about"],
        "weather": [r"weather", r"climate", r"temperature", r"rain", r"season"],
        "transport": [r"transport", r"travel by", r"how to reach", r"getting there"],
        "hotels": [r"hotel", r"accommodation", r"stay", r"where to stay"],
        "budget": [r"budget", r"cost", r"price", r"expense"],
        "itinerary": [r"itinerary", r"plan", r"schedule", r"day by day"],
        "full_planning": [r"plan everything", r"complete planning", r"full trip"]
    }

    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        self.context: Dict[str, Any] = {
            "origin": None,
            "destination": None,
            "start_date": None,
            "end_date": None,
            "travel_mode_preference": None,
            "budget_total": None,
            "travelers": 1
        }
        self.agent_outputs: Dict[str, Any] = {}
        self.conversation_history: list[Dict[str, str]] = []

  
    def parse_user_prompt(self, user_prompt: str) -> Dict[str, Any]:
        ctx = self.context.copy()
        s = user_prompt.lower()

        # Extract origin and destination
        m = re.search(r"from\s+([a-z\s\-]+)\s+to\s+([a-z\s\-]+)", s)
        if m:
            ctx["origin"] = m.group(1).strip().title()
            ctx["destination"] = m.group(2).strip().title()

        # Extract dates
        m = re.search(r"(\d{1,2}[/-]\d{1,2}[/-]\d{4})\s*(?:to|-)\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})", s)
        if m:
            def normalize_date(d: str):
                d = d.replace("/", "-")
                for fmt in ("%d-%m-%Y", "%d/%m/%Y"):
                    try:
                        return datetime.strptime(d, fmt).strftime("%Y-%m-%d")
                    except:
                        continue
                return None
            ctx["start_date"] = normalize_date(m.group(1))
            ctx["end_date"] = normalize_date(m.group(2))

        # Travel mode
        if "car" in s:
            ctx["travel_mode_preference"] = "car"
        elif "flight" in s or "plane" in s:
            ctx["travel_mode_preference"] = "flight"
        elif "train" in s:
            ctx["travel_mode_preference"] = "train"

        # Budget
        m = re.search(r"budget.*?(\d+)", s)
        if m:
            try:
                ctx["budget_total"] = int(m.group(1))
            except:
                pass

        # Travelers
        m = re.search(r"(?:we are|travelling)\s*(\d+)\s*person", s)
        if m:
            ctx["travelers"] = int(m.group(1))

        return ctx

    # -------------------
    # Intent Classification
    # -------------------
    def classify_intent(self, user_input: str) -> str:
        user_input_lower = user_input.lower()
        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, user_input_lower):
                    return intent
        return "overview"

    # -------------------
    # Formatting Output
    # -------------------
    @staticmethod
    def format_output(agent_out: Any) -> Dict[str, Any]:
        if isinstance(agent_out, dict):
            return agent_out
        return {"raw": str(agent_out)}

    # -------------------
    # Agent Executors
    # -------------------
    def run_travel_research_agent(self, prompt: str):
        out = run_travel_research(prompt, self.context)
        self.agent_outputs["travel_research"] = self.format_output(out)
        return out

    def run_weather_agent(self, prompt: str):
        ctx = {
            "destination": self.context.get("destination"),
            "start_date": self.context.get("start_date"),
            "end_date": self.context.get("end_date")
        }
        out = run_weather_advice(prompt, ctx)
        self.agent_outputs["weather_advice"] = self.format_output(out)
        return out

    def run_transport_agent(self, prompt: str):
        ctx = {
            "origin": self.context.get("origin"),
            "destination": self.context.get("destination"),
            "travel_mode_preference": self.context.get("travel_mode_preference")
        }
        out = run_transport_advice(prompt, ctx)
        self.agent_outputs["transport_advice"] = self.format_output(out)
        return out

    def run_hotel_agent(self, prompt: str):
        ctx = {
            "destination": self.context.get("destination"),
            "budget_total": self.context.get("budget_total")
        }
        out = run_hotel_recommendation(prompt, ctx)
        self.agent_outputs["hotel_recommendation"] = self.format_output(out)
        return out

    def run_budget_agent(self, prompt: str):
        ctx = {
            "budget_total": self.context.get("budget_total")
        }
        out = run_budget_optimizer(prompt, ctx)
        self.agent_outputs["budget_optimizer"] = self.format_output(out)
        return out

    def run_itinerary_agent(self, prompt: str):
        # Fill context with outputs of previous agents, default to empty string if missing
        ctx = {
            "research": self.agent_outputs.get("travel_research", {}).get("raw", ""),
            "weather": self.agent_outputs.get("weather_advice", {}).get("raw", ""),
            "transport": self.agent_outputs.get("transport_advice", {}).get("raw", ""),
            "hotels": self.agent_outputs.get("hotel_recommendation", {}).get("raw", ""),
            "budget": self.agent_outputs.get("budget_optimizer", {}).get("raw", "")
        }

        # Optional: remove keys that are empty if you want
        # ctx = {k: v for k, v in ctx.items() if v}

        try:
            # Call CrewAI task
            out = run_itinerary_builder(prompt, ctx)
        except ValueError as e:
            # Fallback if interpolation fails
            print("CrewAI interpolation error, using fallback.")
            out = {"raw": "Sorry, could not generate full itinerary, but here's what I have."}

        # Save output in agent_outputs
        self.agent_outputs["itinerary"] = self.format_output(out)
        return out


    # -------------------
    # Orchestration
    # -------------------
    def process_user_input(self, user_input: str) -> Dict[str, Any]:
        # Retrieve past memory
        memory_results = query_memory(user_input, top_k=3)
        past_context = ""
        if memory_results and memory_results.get("documents"):
            past_context = "\n".join(memory_results["documents"][0])

        # Update context
        new_ctx = self.parse_user_prompt(user_input)
        self.context.update({k: v for k, v in new_ctx.items() if v is not None})

        # Classify intent
        intent = self.classify_intent(user_input)

        # Run relevant agent
        if intent == "overview":
            response = self.run_travel_research_agent(user_input + "\nContext:\n" + past_context)
        elif intent == "weather":
            response = self.run_weather_agent(user_input + "\nContext:\n" + past_context)
        elif intent == "transport":
            response = self.run_transport_agent(user_input + "\nContext:\n" + past_context)
        elif intent == "hotels":
            response = self.run_hotel_agent(user_input + "\nContext:\n" + past_context)
        elif intent == "budget":
            response = self.run_budget_agent(user_input + "\nContext:\n" + past_context)
        elif intent in ["itinerary", "full_planning"]:
            response = self.run_itinerary_agent(user_input + "\nContext:\n" + past_context)
        else:
            response = self.run_travel_research_agent(user_input + "\nContext:\n" + past_context)

        # Store conversation memory
        memory_metadata = {
            "user_id": self.user_id,
            "intent": intent,
            "timestamp": datetime.now().isoformat()
        }
        doc_id = f"{self.user_id}_{datetime.now().timestamp()}"
        memory_text = f"Q: {user_input}\nA: {str(response)}"
        add_memory(doc_id=doc_id, text=memory_text, metadata=memory_metadata)

        # Update local conversation history
        self.conversation_history.append({"user": user_input, "assistant": str(response)})

        return {
            "intent": intent,
            "response": self.format_output(response),
            "context": self.context
        }

    # -------------------
    # Context Summary
    # -------------------
    def get_context_summary(self) -> str:
        summary = "📌 **Trip Context:**\n"
        for k, v in self.context.items():
            if v:
                summary += f"- {k}: {v}\n"
        summary += "\n✅ **Completed Agents:** " + ", ".join(self.agent_outputs.keys())
        return summary
