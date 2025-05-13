from agents.api_agent import APIAgent
from agents.scraper_agent import ScraperAgent
from agents.retriever_agent import RetrieverAgent
from agents.language_agent import LanguageAgent

class Orchestrator:
    def __init__(self):
        # Mapping keywords to stock symbols
        self.supported_companies = {
            "tsmc": "TSM",
            "tsm": "TSM",
            "samsung": "005930.KS",
            "005930": "005930.KS",
            "alibaba": "BABA",
            "baba": "BABA"
        }

        self.api_agent = APIAgent(list(set(self.supported_companies.values())))
        self.scraper_agent = ScraperAgent()
        self.retriever_agent = RetrieverAgent()
        self.language_agent = LanguageAgent()

    def extract_company_symbol(self, query: str) -> str | None:
        query = query.lower()
        for keyword, symbol in self.supported_companies.items():
            if keyword in query:
                return symbol
        return None

    def is_sector_summary(self, query: str) -> bool:
        keywords = [
            "tech sector", "asia tech", "asian market", "market movement", 
            "stock summary", "tech stocks", "summary of tech", "market brief"
        ]
        return any(k in query.lower() for k in keywords)

    def handle(self, query: str) -> str:
        print(f"🔍 Received query: {query}")

        # General tech sector query
        if self.is_sector_summary(query):
            print("🧠 Handling sector-wide summary...")
            market_data = self.api_agent.get_market_data()
            context = ["Summary of Asia tech sector performance."]
            return self.language_agent.synthesize_brief(context, market_data)

        # Specific company query
        selected_symbol = self.extract_company_symbol(query)
        if not selected_symbol:
            print("⚠️ No specific company detected — defaulting to TSM.")
            selected_symbol = "TSM"

        print(f"🏷️ Selected company: {selected_symbol}")

        earnings_summary = self.scraper_agent.get_earnings_summary(selected_symbol)
        market_data = self.api_agent.get_market_data()

        self.retriever_agent.add_documents([earnings_summary])
        context = self.retriever_agent.retrieve(query)

        response = self.language_agent.synthesize_brief(context, market_data)
        print(f"🧠 Final response: {response}")
        return response
