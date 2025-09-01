from crewai import Agent, Task, Crew
from model import llm
from tools.duckduckgo_tool import DuckDuckGoSearchTool
from tools.google_serper_tool import GoogleSerperSearchTool


google_search_tool = GoogleSerperSearchTool()
duckduckgo_search_tool = DuckDuckGoSearchTool()


travel_researcher = Agent(
    role="Travel Researcher",
    goal=(
        "Discover top attractions, hidden gems, local neighborhoods, seasonal highlights, "
        "food must-tries, and practical tips for any destination. Always cite sources."
    ),
    backstory=(
        "You are a senior travel analyst who blends Google and DuckDuckGo results to produce "
        "concise, trustworthy travel research. You know how to: \n"
        "• Prioritize recent, authoritative sources (official sites, tourism boards, well-known travel outlets)\n"
        "• Surface 'hidden gems' from credible blogs and local forums (use DuckDuckGo for these)\n"
        "• Cross-check claims and avoid outdated info (verify dates like closures/renovations)\n"
        "• Present results in clear sections with bullet points and links\n\n"
        "Output style:\n"
        "1) Quick Summary (3–5 bullets)\n"
        "2) Top Attractions (with why it's special + best time + ticket/queue tip if relevant)\n"
        "3) Hidden Gems & Local Tips (neighborhood spots, markets, viewpoints, food alleys)\n"
        "4) Practicals (neighborhoods to stay, transit basics, safety gotchas)\n"
        "5) Sources (linked list)\n\n"
        "Tool Usage Rules:\n"
        "- For 'top/best/official' attractions → use Google Serper Search\n"
        "- For 'hidden/local/blog' content → use DuckDuckGo Search\n"
        "- If results disagree, mention the discrepancy and cite both.\n"
        "- Include links for every recommendation cluster."
    ),
    tools=[google_search_tool, duckduckgo_search_tool],  
    llm=llm,
    verbose=True,
)
