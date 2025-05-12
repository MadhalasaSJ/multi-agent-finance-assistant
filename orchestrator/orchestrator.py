from agents.api_agent import APIAgent
from agents.scraper_agent import ScraperAgent
from agents.retriever_agent import RetrieverAgent
from agents.language_agent import LanguageAgent

class Orchestrator:
    def __init__(self):
        self.api_agent = APIAgent(["TSM", "005930.KS", "BABA"])
        self.scraper_agent = ScraperAgent()
        self.retriever_agent = RetrieverAgent()
        self.language_agent = LanguageAgent()

    def handle(self, query: str) -> str:
        print(f"🔍 Received query: {query}")

        # Step 1: Scrape earnings
        earnings_summary = self.scraper_agent.get_earnings_summary("TSM")
        print(f"📄 Earnings Summary: {earnings_summary}")

        # Step 2: Get market data
        market_data = self.api_agent.get_market_data()
        print(f"📈 Market Data: {market_data}")

        # Step 3: Add docs to retriever and query
        self.retriever_agent.add_documents([earnings_summary])
        context = self.retriever_agent.retrieve(query)
        print(f"📚 Retrieved Context: {context}")

        # Step 4: Generate final brief
        response = self.language_agent.synthesize_brief(context, market_data)
        print(f"🧠 Final Response: {response}")
        return response
