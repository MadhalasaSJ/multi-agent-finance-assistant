
import re
import ollama


class LanguageAgent:
    def __init__(self):
        self.model = "gemma3:1b"

        self.supported_languages = {
            "English": "English",
            "Hindi": "Hindi",
            "German": "German",
        }

        self.company_names = {
            "TSM": "TSMC",
            "TSMC": "TSMC",
            "005930.KS": "Samsung",
            "SSNLF": "Samsung",
            "0700.HK": "Tencent",
            "BABA": "Alibaba",
            "NVDA": "NVIDIA",
            "AAPL": "Apple",
            "MSFT": "Microsoft",
        }

        self.company_aliases = {
            "TSMC": ["TSMC", "Taiwan Semiconductor", "TSM"],
            "Samsung": ["Samsung", "005930.KS", "SSNLF"],
            "Tencent": ["Tencent", "0700.HK"],
            "Alibaba": ["Alibaba", "BABA"],
            "NVIDIA": ["NVIDIA", "NVDA"],
            "Apple": ["Apple", "AAPL"],
            "Microsoft": ["Microsoft", "MSFT"],
        }

        self.translations = {
            "English": {
                "title": "Technology Stock Market Brief",
                "intro": "Stock movements based on the supplied closing prices:",
                "up": "increased",
                "down": "decreased",
                "unchanged": "was unchanged",
                "unavailable": "price movement is unavailable",
                "previous": "Previous close",
                "current": "Current close",
                "news": "Relevant company news",
                "no_data": "No matching stock-price data was found.",
                "no_news": "No relevant company news was retrieved.",
                "translation_error": "A news item could not be reliably translated and was omitted.",
                "largest": "Largest increase",
                "weakest": "Weakest performance",
                "currency_note": "Prices are shown in the currency supplied by the data source.",
            },
            "Hindi": {
                "title": "टेक्नोलॉजी कंपनियों के शेयरों का विवरण",
                "intro": "दिए गए क्लोजिंग प्राइस के आधार पर शेयरों में बदलाव:",
                "up": "में वृद्धि हुई",
                "down": "में गिरावट आई",
                "unchanged": "में कोई बदलाव नहीं हुआ",
                "unavailable": "की कीमत में बदलाव का डेटा उपलब्ध नहीं है",
                "previous": "पिछला क्लोजिंग प्राइस",
                "current": "वर्तमान क्लोजिंग प्राइस",
                "news": "संबंधित कंपनी समाचार",
                "no_data": "मांगी गई कंपनियों के शेयरों का डेटा नहीं मिला।",
                "no_news": "कोई प्रासंगिक कंपनी समाचार प्राप्त नहीं हुआ।",
                "translation_error": "एक समाचार का विश्वसनीय अनुवाद नहीं हो सका, इसलिए उसे शामिल नहीं किया गया।",
                "largest": "सबसे अधिक वृद्धि",
                "weakest": "सबसे कमजोर प्रदर्शन",
                "currency_note": "कीमतें डेटा स्रोत द्वारा दी गई मुद्रा में दिखाई गई हैं।",
            },
            "German": {
                "title": "Marktbericht für Technologieaktien",
                "intro": "Kursbewegungen auf Grundlage der angegebenen Schlusskurse:",
                "up": "ist gestiegen",
                "down": "ist gefallen",
                "unchanged": "ist unverändert geblieben",
                "unavailable": "keine Kursänderungsdaten verfügbar",
                "previous": "Vorheriger Schlusskurs",
                "current": "Aktueller Schlusskurs",
                "news": "Relevante Unternehmensnachrichten",
                "no_data": "Keine passenden Aktiendaten gefunden.",
                "no_news": "Es wurden keine relevanten Unternehmensnachrichten abgerufen.",
                "translation_error": "Eine Nachricht konnte nicht zuverlässig übersetzt werden und wurde ausgelassen.",
                "largest": "Größter Anstieg",
                "weakest": "Schwächste Entwicklung",
                "currency_note": "Die Kurse werden in der vom Datenanbieter gelieferten Währung angezeigt.",
            },
        }

        print("Initializing market brief generator...")

    def _prepare_verified_facts(self, market_data):
        """Calculate stock movements from actual API price fields."""
        facts = []

        for symbol, data in (market_data or {}).items():
            company = self.company_names.get(symbol, symbol)

            current = data.get("current", data.get("current_close"))
            previous = data.get("previous", data.get("previous_close"))

            if data.get("error") or current is None or previous is None:
                facts.append({
                    "symbol": symbol,
                    "company": company,
                    "previous": None,
                    "current": None,
                    "change": None,
                })
                continue

            try:
                current = float(current)
                previous = float(previous)

                if previous <= 0:
                    raise ValueError("Invalid previous close")

                change = ((current - previous) / previous) * 100

                facts.append({
                    "symbol": symbol,
                    "company": company,
                    "previous": previous,
                    "current": current,
                    "change": change,
                })

            except (TypeError, ValueError, OverflowError):
                facts.append({
                    "symbol": symbol,
                    "company": company,
                    "previous": None,
                    "current": None,
                    "change": None,
                })

        return facts

    def _requested_companies(self, user_query, facts):
        """Find companies explicitly named in the user's question."""
        if not user_query:
            return []

        query = user_query.lower()
        requested = []

        for fact in facts:
            company = fact["company"]
            aliases = self.company_aliases.get(
                company, [company, fact["symbol"]]
            )

            if any(alias.lower() in query for alias in aliases):
                requested.append(fact)

        return requested

    def _format_price(self, value):
        return f"{value:,.2f}"

    def _filter_news(self, retrieved_texts, user_query, facts):
        """Exclude news about companies unrelated to the question."""
        documents = [
            text.strip()
            for text in (retrieved_texts or [])
            if isinstance(text, str) and text.strip()
        ]

        requested = self._requested_companies(user_query, facts)

        # If specific companies were named, keep only documents
        # mentioning those companies or their ticker symbols.
        if requested:
            aliases = {
                alias.lower()
                for fact in requested
                for alias in self.company_aliases.get(
                    fact["company"], [fact["company"], fact["symbol"]]
                )
            }

            documents = [
                doc for doc in documents
                if any(alias in doc.lower() for alias in aliases)
            ]

        # Remove duplicates while preserving document order.
        return list(dict.fromkeys(documents))

    def _translate_news(self, document, language):
        """Translate a retrieved document without changing its facts."""
        if language == "English":
            return document

        prompt = f"""
Translate the financial news below into {language}.

Requirements:
- Translate the complete text into {language}.
- Preserve company names, ticker symbols, dates, numbers,
  percentages, currencies, and financial terminology.
- Do not add explanations, predictions, or new information.
- Do not summarize or omit any claims.
- Return only the translation.

Source text:
{document}
"""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            f"You are a faithful financial translator. "
                            f"Output only {language}. Never add facts."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                options={"temperature": 0.0},
            )

            translated = response["message"]["content"].strip()

            if not translated:
                return None

            # Do not accept a translation if numerical tokens changed.
            number_pattern = r"(?<!\w)[+-]?\d[\d,]*(?:\.\d+)?%?"
            source_numbers = re.findall(number_pattern, document)
            translated_numbers = re.findall(number_pattern, translated)

            if source_numbers != translated_numbers:
                print("Translation rejected: numerical values changed.")
                return None

            # Hindi output must contain Devanagari characters.
            if language == "Hindi" and not re.search(
                r"[\u0900-\u097F]", translated
            ):
                return None

            # Avoid accepting an untranslated English document.
            if language == "German" and translated == document:
                return None

            return translated

        except Exception as error:
            print(f"News translation failed: {error}")
            return None

    def synthesize_brief(
        self,
        retrieved_texts,
        market_data,
        language="English",
        user_query=None,
    ):
        language = self.supported_languages.get(language, "English")
        labels = self.translations[language]

        facts = self._prepare_verified_facts(market_data)

        requested_facts = self._requested_companies(user_query, facts)

        # For specific questions, show only the requested companies.
        # For general market questions, show all supplied market data.
        display_facts = requested_facts if requested_facts else facts

        lines = [
            labels["title"],
            "",
            labels["intro"],
            "",
        ]

        if not display_facts:
            lines.append(labels["no_data"])
        else:
            available = []

            for fact in display_facts:
                company = fact["company"]
                symbol = fact["symbol"]
                change = fact["change"]

                if change is None:
                    lines.append(
                        f"{company} ({symbol}): {labels['unavailable']}."
                    )
                    continue

                if change > 0:
                    direction = labels["up"]
                elif change < 0:
                    direction = labels["down"]
                else:
                    direction = labels["unchanged"]

                # Use natural Hindi sentence structure.
                if language == "Hindi":
                    movement = (
                        f"{company} ({symbol}) के शेयर में "
                        f"{abs(change):.2f}% की {('वृद्धि' if change > 0 else 'गिरावट')} हुई।"
                        if change != 0
                        else f"{company} ({symbol}) के शेयर में कोई बदलाव नहीं हुआ।"
                    )
                elif language == "German":
                    movement = (
                        f"{company} ({symbol}) {direction} "
                        f"um {abs(change):.2f}%."
                    )
                else:
                    movement = (
                        f"{company} ({symbol}) {direction} "
                        f"by {abs(change):.2f}%."
                    )

                lines.append(movement)
                lines.append(
                    f"{labels['previous']}: "
                    f"{self._format_price(fact['previous'])}; "
                    f"{labels['current']}: "
                    f"{self._format_price(fact['current'])}."
                )

                available.append(fact)

            if len(available) > 1:
                biggest = max(available, key=lambda item: item["change"])
                weakest = min(available, key=lambda item: item["change"])

                lines.append("")

                if language == "Hindi":
                    lines.append(
                        f"{labels['largest']}: {biggest['company']} "
                        f"({biggest['change']:+.2f}%)।"
                    )
                    lines.append(
                        f"{labels['weakest']}: {weakest['company']} "
                        f"({weakest['change']:+.2f}%)।"
                    )
                elif language == "German":
                    lines.append(
                        f"{labels['largest']}: {biggest['company']} "
                        f"({biggest['change']:+.2f}%)."
                    )
                    lines.append(
                        f"{labels['weakest']}: {weakest['company']} "
                        f"({weakest['change']:+.2f}%)."
                    )
                else:
                    lines.append(
                        f"{labels['largest']}: {biggest['company']} "
                        f"({biggest['change']:+.2f}%)."
                    )
                    lines.append(
                        f"{labels['weakest']}: {weakest['company']} "
                        f"({weakest['change']:+.2f}%)."
                    )

        # Filter first, then translate only relevant news.
        relevant_news = self._filter_news(
            retrieved_texts, user_query, facts
        )

        lines.extend(["", labels["news"] + ":"])

        translated_news = []

        for document in relevant_news:
            translated = self._translate_news(document, language)

            if translated:
                translated_news.append(translated)

        if translated_news:
            for document in translated_news:
                lines.append(f"- {document}")
        elif relevant_news:
            lines.append(labels["translation_error"])
        else:
            lines.append(labels["no_news"])

        lines.extend(["", labels["currency_note"]])

        return "\n".join(lines)


if __name__ == "__main__":
    agent = LanguageAgent()

    # Illustrative test prices only. The live app must use APIAgent data.
    market_data = {
        "NVDA": {"current": 213.71, "previous": 215.38},
        "AAPL": {"current": 350.04, "previous": 343.83},
    }

    retrieved_docs = [
        "NVDA reported earnings for 2026-07-31. "
        "Reported EPS: 2.22, Estimated EPS: 2.09. "
        "Earnings Surprise: 6.2201%.",
        "TSMC reported earnings, beating estimates by 4%.",
        "AAPL shares gained during the latest trading session.",
    ]

    query = "NVIDIA और Apple के शेयरों में क्या बदलाव आया?"

    for language in ["English", "Hindi", "German"]:
        print(
            f"\n--- {language} ---\n",
            agent.synthesize_brief(
                retrieved_docs,
                market_data,
                language=language,
                user_query=query,
            ),
        )
