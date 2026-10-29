
from agents.api_agent import APIAgent
from agents.scraper_agent import ScraperAgent
from agents.retriever_agent import RetrieverAgent
from agents.language_agent import LanguageAgent


class Orchestrator:
    def __init__(self):
        self.supported_companies = {
            "tsmc": "TSM",
            "tsm": "TSM",
            "samsung": "005930.KS",
            "005930": "005930.KS",
            "alibaba": "BABA",
            "baba": "BABA",
            "tencent": "0700.HK",
            "0700": "0700.HK",
            "nvidia": "NVDA",
            "nvda": "NVDA",
            "apple": "AAPL",
            "aapl": "AAPL",
            "microsoft": "MSFT",
            "msft": "MSFT",
        }

        symbols = list(dict.fromkeys(self.supported_companies.values()))

        self.api_agent = APIAgent(symbols)
        self.scraper_agent = ScraperAgent()
        self.retriever_agent = RetrieverAgent()
        self.language_agent = LanguageAgent()

        # Avoid repeatedly adding the same document to FAISS.
        self.indexed_documents = set()

    def extract_company_symbols(self, query: str) -> list:
        query_lower = query.lower()
        selected = []

        for keyword in sorted(
            self.supported_companies,
            key=len,
            reverse=True,
        ):
            if keyword in query_lower:
                symbol = self.supported_companies[keyword]

                if symbol not in selected:
                    selected.append(symbol)

        return selected

    def is_comparison_query(self, query: str) -> bool:
        keywords = [
            "compare",
            "comparison",
            "which stock",
            "which company's stock",
            "highest increase",
            "largest increase",
            "increased the most",
            "best performing",
            "compare stocks",
            "तुलना",
            "सबसे अधिक",
            "किस कंपनी",
            "welche aktie",
            "vergleich",
            "am stärksten gestiegen",
        ]

        query_lower = query.lower()
        return any(keyword in query_lower for keyword in keywords)

    def is_sector_summary(self, query: str) -> bool:
        keywords = [
            "tech sector",
            "asia tech",
            "asian market",
            "market movement",
            "stock summary",
            "tech stocks",
            "summary of tech",
            "market brief",
            "technology stocks",
            "technology companies",
            "शेयर बाजार",
            "शेयरों की कीमत",
            "शेयरों में बदलाव",
            "technologieaktien",
        ]

        query_lower = query.lower()
        return any(keyword in query_lower for keyword in keywords)

    def _retrieve_company_news(self, symbol: str, query: str) -> list:
        """Fetch and retrieve news for a company, if available."""
        try:
            summary = self.scraper_agent.get_earnings_summary(symbol)

            if not isinstance(summary, str) or not summary.strip():
                return []

            summary = summary.strip()

            if summary not in self.indexed_documents:
                self.retriever_agent.add_documents([summary])
                self.indexed_documents.add(summary)

            results = self.retriever_agent.retrieve(query, top_k=2)

            return [
                document
                for document in results
                if isinstance(document, str) and document.strip()
            ]

        except Exception as error:
            print(f"News retrieval failed for {symbol}: {error}")
            return []

    def handle(
        self,
        query: str,
        language: str = "English",
    ) -> str:
        print(f"Received query: {query}")
        print(f"Response language: {language}")

        if language not in {"English", "Hindi", "German"}:
            language = "English"

        selected_symbols = self.extract_company_symbols(query)

        # Comparison questions should include all explicitly mentioned
        # companies. Sector-wide questions compare all supported stocks.
        if self.is_sector_summary(query):
            symbols_to_fetch = list(
                dict.fromkeys(self.supported_companies.values())
            )
        elif self.is_comparison_query(query) and len(selected_symbols) < 2:
            symbols_to_fetch = list(
                dict.fromkeys(self.supported_companies.values())
            )
        elif selected_symbols:
            symbols_to_fetch = selected_symbols
        else:
            return self.language_agent.synthesize_brief(
                [],
                {},
                language=language,
                user_query=query,
            )

        print(f"Fetching market data for: {symbols_to_fetch}")

        all_market_data = self.api_agent.get_market_data()

        market_data = {
            symbol: all_market_data[symbol]
            for symbol in symbols_to_fetch
            if symbol in all_market_data
        }

        retrieved_documents = []

        # Retrieve news only for the companies relevant to this query.
        for symbol in symbols_to_fetch:
            company_news = self._retrieve_company_news(symbol, query)
            retrieved_documents.extend(company_news)

        # Remove repeated documents while preserving order.
        retrieved_documents = list(dict.fromkeys(retrieved_documents))

        response = self.language_agent.synthesize_brief(
            retrieved_documents,
            market_data,
            language=language,
            user_query=query,
        )

        print(f"Final response: {response}")
        return response
