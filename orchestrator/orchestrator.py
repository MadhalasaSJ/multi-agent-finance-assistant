from agents.api_agent import APIAgent
from agents.scraper_agent import ScraperAgent
from agents.retriever_agent import RetrieverAgent
from agents.language_agent import LanguageAgent


class Orchestrator:
    def __init__(self):
        # Track supported companies and their ticker symbols
        self.supported_companies = {
            "tsmc": "TSM",
            "tsm": "TSM",
            "samsung": "005930.KS",
            "005930": "005930.KS",
            "alibaba": "BABA",
            "baba": "BABA"
        }

        self.default_company = "TSM"
        self.api_agent = APIAgent(list(set(self.supported_companies.values())))
        self.scraper_agent = ScraperAgent()
        self.retriever_agent = RetrieverAgent()
        self.language_agent = LanguageAgent()

    def extract_company_symbol(self, query: str) -> str:
        """Basic keyword matching to select the company mentioned in the query."""
        query_lower = query.lower()
        for keyword, symbol in self.supported_companies.items():
            if keyword in query_lower:
                return symbol
        return None  # No specific company matched

    def is_sector_summary(self, query: str) -> bool:
        """Detects if the query is about general tech/market movement."""
        keywords = ["asia tech", "tech sector", "stock movement", "market summary", "tech movement"]
        return any(kw in query.lower() for kw in keywords)

    def handle(self, query: str) -> str:
        print(f"🔍 Received query: {query}")

        # Step 1: Determine if this is a sector-wide summary
        if self.is_sector_summary(query):
            print("🧠 Detected sector-wide query")

            # Get market data for all tracked companies
            market_data = self.api_agent.get_market_data()
            print(f"📈 Market Data: {market_data}")

            # Create a dummy context for LLM
            context = ["Summary of Asia tech stock movement."]
            response = self.language_agent.synthesize_brief(context, market_data)
            print(f"🧠 Final Response: {response}")
            return response

        # Step 2: Otherwise detect a specific company
        selected_company = self.extract_company_symbol(query)
        if not selected_company:
            print("⚠️ No specific company found in query — defaulting to TSM.")
            selected_company = self.default_company

        print(f"🏷️ Detected company: {selected_company}")

        # Step 3: Scrape earnings for the company
        earnings_summary = self.scraper_agent.get_earnings_summary(selected_company)
        print(f"📄 Earnings Summary for {selected_company}: {earnings_summary}")

        # Step 4: Get market data
        market_data = self.api_agent.get_market_data()
        print(f"📈 Market Data: {market_data}")

        # Step 5: Use retriever to add context and respond
        self.retriever_agent.add_documents([earnings_summary])
        context = self.retriever_agent.retrieve(query)
        print(f"📚 Retrieved Context: {context}")

        # Step 6: Final language synthesis
        response = self.language_agent.synthesize_brief(context, market_data)
        print(f"🧠 Final Response: {response}")
        return response
